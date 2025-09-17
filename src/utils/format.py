import pandas as pd

from src.config import settings
from src.logger import logger


def format_value_for_mutation(value, column_id: str):
    """
    Format a value for a Monday.com mutation based on the column type.
    """

    if pd.isna(value):
        return None

    value = str(value)

    # --- Date Column ---
    # Monday expects: {"date": "YYYY-MM-DD"}
    if column_id.startswith("date_"):
        try:
            # Pandas helps parse various date formats automatically
            formatted_date = pd.to_datetime(value, dayfirst=True).strftime("%Y-%m-%d")
            return {"date": formatted_date}
        except (ValueError, TypeError):
            logger.warning(
                f"Could not parse date '{value}' for column {column_id}. Skipping."
            )
            return None

    # --- Status or Color Column ---
    # Monday can match by the label's text: {"label": "Status Text"}
    elif column_id.startswith("color_"):
        return {"label": value}

    # --- Dropdown Column ---
    # Monday expects a list of labels: {"labels": ["Value 1", "Value 2"]}
    elif column_id.startswith("dropdown_"):
        # Assuming multiple dropdown values in the CSV are separated by a comma
        labels = [label.strip() for label in value.split(",")]
        return {"labels": labels}

    # --- Text Column (Default) ---
    # For text, numbers, etc., no special formatting is needed.
    else:
        return value
