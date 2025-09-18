import json
import pprint

import httpx
import pandas as pd

import src.utils.monday_values as monday_utils
from src.config import settings
from src.logger import logger


class MondayService:
    def __init__(self):
        self.api_token = settings.monday_api_token
        self.api_endpoint = settings.monday_api_endpoint
        self.headers = {"Authorization": self.api_token}
        # Create client for reusing connections
        self.client = httpx.Client(headers=self.headers)

    def __del__(self):
        self.client.close()

    def _call(
        self,
        json: str = None,
    ):
        r = self.client.post(url=self.api_endpoint, json=json)
        r.raise_for_status()
        return r.json()

    def prepare_mutations(
        self, csv_df: pd.DataFrame, board_mapping: dict, monday_items: dict
    ) -> tuple:
        """
        Prepare mutations for creating or updating items based on the CSV DataFrame and existing items.
        @return: Tuple of (items_to_create, items_to_update)
        """

        items_to_create = []
        items_to_update = []
        key_column_csv = "Key"

        logger.info(
            f"Preparing mutations for {len(csv_df)} csv rows items against {len(monday_items)} Monday items..."
        )

        # Iterate through each row in the CSV DataFrame
        for _, row in csv_df.iterrows():
            jira_key = row[key_column_csv]

            ### Case 1 : Update - Item exist in Monday ###
            if jira_key in monday_items:
                monday_item = monday_items[jira_key]
                changed_columns_values = {}

                # Create a map of column_id to text for easier comparison
                # TODO: check if this can be optimized by storing this map when fetching items
                # TODO: check if all columns types are covered by the text field
                monday_item_columns_dict = {
                    column["id"]: column["text"]
                    for column in monday_item.get("column_values", [])
                }

                ### Iterate over the Jira-Monday mapping ###
                for csv_col, monday_id in board_mapping.items():
                    if csv_col not in row:
                        continue

                    # Compare Jira and Monday values
                    jira_value = row[csv_col]
                    monday_value = monday_item_columns_dict.get(monday_id)
                    are_values_different, jira_value_str = monday_utils.compare_values(
                        jira_value, monday_value, monday_id
                    )

                    # Format Jira value for Monday mutation if different
                    if are_values_different:
                        formatted_value = monday_utils.format_value_for_mutation(
                            jira_value, monday_id
                        )
                        if formatted_value is not None:
                            changed_columns_values[monday_id] = formatted_value

                if changed_columns_values:
                    items_to_update.append(
                        {
                            "item_id": monday_item["id"],
                            "column_values": changed_columns_values,
                        }
                    )
                    logger.info(
                        f"Item '{jira_key}' (ID: {monday_item['id']}) will be updated with changes: {changed_columns_values}"
                    )

            ### Case 2 Upsert - Item doesn't exist in Monday ###
            else:
                new_item_columns = {}
                for csv_col, monday_id in board_mapping.items():
                    if csv_col in row and pd.notna(row[csv_col]):
                        formatted_value = monday_utils.format_value_for_mutation(
                            row[csv_col], monday_id
                        )
                        if formatted_value is not None:
                            new_item_columns[monday_id] = formatted_value

                items_to_create.append(
                    {
                        "name": row["Summary"],
                        "column_values": json.dumps(new_item_columns),
                    }
                )
                logger.info(
                    f"Item '{row["Summary"]}' will be created with values: {new_item_columns}"
                )

        return items_to_create, items_to_update

    def fetch_monday_items(
        self, items_keys: list[str], board_id: str, key_column_id: str
    ) -> dict:
        """
        Fetch all items from a Board by key_column_id matching any of items_keys.
        Uses pagination to retrieve all items if necessary.
        Returns a map of items with the key being the value in the key_column_id.
        @param items_keys: List of keys to search for in the key_column_id.
        @param board_id: ID of the board to search.
        @param key_column_id: ID of the column to match the keys against.
        @return: Dictionary mapping item keys to their details.
        """

        query = """
          query ($boardId: ID!, $columnId: String!, $itemsKeys: [String]!, $cursor: String) {
          items_page_by_column_values (
            board_id: $boardId
            columns: [{column_id: $columnId, column_values: $itemsKeys}]
            limit: 100,
            cursor: $cursor
          ) {
            cursor
            items {
              id
              name
              column_values {
                id
                text
              }
            }
          }
        }
        """

        monday_items_map = {}

        cursor = None

        while True:
            variables = {
                "boardId": board_id,
                "columnId": key_column_id,
                "itemsKeys": items_keys,
                "cursor": cursor,
            }

            json = {"query": query, "variables": variables}

            try:
                data = self._call(json=json)
                if "errors" in data:
                    print(f"GraphQL errors: {data['errors']}")
                    break

                result_data = data.get("data", {}).get(
                    "items_page_by_column_values", {}
                )
                items = result_data.get("items", [])

                if not items and cursor is None:
                    logger.info("No items found.")

                # Process the fetched items and assign the column values to the map
                for item in items:
                    item_jira_key = next(
                        (
                            cv["text"]
                            for cv in item["column_values"]
                            if cv["id"] == key_column_id
                        ),
                        None,
                    )

                    if item_jira_key:
                        monday_items_map[item_jira_key] = {
                            "id": item["id"],
                            "name": item["name"],
                            "column_values": item["column_values"],
                        }

                # Check if there's a next page
                cursor = result_data.get("cursor")
                if not cursor:
                    logger.info("No more pages to fetch.")
                    break

                logger.info(f"Fetching next page with cursor: {cursor}")

            except httpx.HTTPError as e:
                logger.error(
                    f"Error fetching items: {e.response.json() if hasattr(e.response, 'json') else str(e)}"
                )
                break

        return monday_items_map

    def execute_mutations(
        self, board_id: str, items_to_create: list[dict], items_to_update: list[dict]
    ):
        """
        Execute create and update mutations for Monday.com items.
        """

        if items_to_create:
            logger.info(f"Creating {len(items_to_create)} items...")

            create_query = """
            mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON!) {
              create_item (
                board_id: $boardId,
                item_name: $itemName,
                column_values: $columnValues
              ) {
                id
              }
            }
            """
            for item in items_to_create:
                variables = {
                    "itemName": item["name"],
                    "boardId": board_id,
                    "columnValues": item["column_values"],
                }
                try:
                    print("***Creating item:***")
                    pprint.pprint(item)

                    response = self._call(
                        json={"query": create_query, "variables": variables}
                    )
                    if "errors" in response:
                        logger.error(
                            f"Error creating item '{item['name']}': {response['errors']}"
                        )
                    else:
                        logger.info(
                            f"Item '{item['name']}' created with ID: {response['data']['create_item']['id']}"
                        )
                except httpx.HTTPError as e:
                    logger.error(f"HTTP error creating item '{item['name']}': {str(e)}")

        if items_to_update:
            logger.info(f"Updating {len(items_to_update)} items...")

            update_query = """
            mutation ($itemId: ID!, $boardId: ID!, $columnValues: JSON!) {
                change_multiple_column_values (
                    board_id: $boardId,
                    item_id: $itemId,
                    column_values: $columnValues
                ) {
                    id
                }
            }
            """
            for item in items_to_update:
                variables = {
                    "boardId": board_id,
                    "itemId": item["item_id"],
                    "columnValues": json.dumps(item["column_values"]),
                }
                try:
                    print("***Updating item ID:***")
                    pprint.pprint(item)
                    response = self._call(
                        json={"query": update_query, "variables": variables}
                    )
                    if "errors" in response:
                        logger.error(
                            f"Error updating item ID '{item['item_id']}': {response['errors']}"
                        )
                    else:
                        logger.info(
                            f"Item ID '{item['item_id']}' updated successfully."
                        )
                except httpx.HTTPError as e:
                    logger.error(
                        f"HTTP error updating item ID '{item['item_id']}': {str(e)}"
                    )
