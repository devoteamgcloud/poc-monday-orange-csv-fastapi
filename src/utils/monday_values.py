import pandas as pd

from src.logger import logger


def value_to_string(value) -> str:
    """Normalize any value to string format for comparison"""
    return "" if pd.isna(value) or value in (None, "null") else str(value).strip()


def normalize_date(date_value) -> str:
    """Normalize Jira date (dd-mm-yyyy HH:MM:SS) to Monday format (yyyy-mm-dd)"""
    try:
        parsed_date = pd.to_datetime(date_value, dayfirst=True, errors="coerce")
        if pd.notna(parsed_date):
            return f"{parsed_date.year:04d}-{parsed_date.month:02d}-{parsed_date.day:02d}"
        return ""
    except Exception as e:
        logger.warning(f"Could not parse date '{date_value}': {str(e)}")
        return ""
    

def compare_values(source_value, monday_value, column_id: str) -> tuple[bool, str]:
    """Compare source and Monday values, returning (is_different, normalized_source_value)"""
    source_str = value_to_string(source_value)
    monday_str = value_to_string(monday_value)
    
    if column_id.startswith("date_"):
        source_str = normalize_date(source_value)
        
    return source_str != monday_str, source_str


def format_value_for_mutation(value, column_id: str):
    """
    Format a value for a Monday.com mutation based on the column type.
    """

    # --- Date Column ---
    # Monday expects: {"date": "YYYY-MM-DD"}
    if column_id.startswith("date_"):
        return {"date": normalize_date(value)}

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
        return str(value).strip()
