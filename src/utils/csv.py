import pandas as pd

from src.logger import logger


def load_and_filter(filepath) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Loads the CSV and splits it based on 'Issue Type'."""
    try:
        df = pd.read_csv(filepath, sep=";")
        # Ensure 'Issue Type' column exists
        if "Issue Type" not in df.columns:
            raise ValueError("CSV missing 'Issue Type' column.")

        df_projects = df[df["Issue Type"] == "Project"].copy()
        df_subtasks = df[df["Issue Type"] == "Sub-task"].copy()

        logger.info(
            f"Loaded CSV. Found {len(df_projects)} projects and {len(df_subtasks)} subtasks."
        )
        return df_projects, df_subtasks

    except FileNotFoundError:
        logger.error(f"Error: The file '{filepath}' was not found.")
        return None, None
