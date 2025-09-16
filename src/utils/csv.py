import pandas as pd
import logging

def load_and_filter(filepath) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Loads the CSV and splits it based on 'Issue Type'."""
    try:
        df = pd.read_csv(filepath, sep=';')
        # Ensure 'Issue Type' column exists
        if 'Issue Type' not in df.columns:
            raise ValueError("CSV missing 'Issue Type' column.")
            
        df_parents = df[df['Issue Type'] == 'Project'].copy()
        df_subtasks = df[df['Issue Type'] == 'Sub-task'].copy()
        
        logging.info(f"Loaded CSV. Found {len(df_parents)} parents and {len(df_subtasks)} subtasks.")
        return df_parents, df_subtasks
        
    except FileNotFoundError:
        logging.error(f"Error: The file '{filepath}' was not found.")
        return None, None