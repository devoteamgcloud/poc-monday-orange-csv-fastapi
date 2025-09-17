import httpx

from src.config import settings
from src.logger import logger

class MondayService:
    def __init__(self):
        self.api_token = settings.monday_api_token
        self.api_endpoint = settings.monday_api_endpoint
        self.headers = {"Authorization": self.api_token}
        # Create client for reusing connections
        self.client = httpx.Client()

    def __del__(self):
        self.client.close()

    def _call(
        self,
        json: str = None,
    ):

        r = self.client.post(headers=self.headers, url=self.api_endpoint, json=json)
        r.raise_for_status()

        return r.json()

    def fetch_monday_items(
        self, items_keys: list[str], board_id: str, key_column_id: str
    ):

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
                    item_jira_key = next((cv["text"] for cv in item["column_values"] if cv["id"] == key_column_id), None)

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
                logger.error(f"Error fetching items: {e.response.json() if hasattr(e.response, 'json') else str(e)}")
                break

        return monday_items_map

    def get_boards(self):
        # Implementation to interact with Monday.com API to get boards
        pass

    def create_item(self, board_id: int, item_name: str):
        # Implementation to create an item on a specific board
        pass
