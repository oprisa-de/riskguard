import pandas as pd
import numpy as np
from typing import List, Tuple
from datetime import datetime
import os

class DataIngestor:
    """
    Handles ingestion of data from various sources (CSV, Excel).
    Supports cleaning and standardizing for the RiskEngine.
    """
    def __init__(self):
        self.required_columns = [
            'customer_id',
            'revenue_amount',
            'date',
            'payment_status',
            'category',
            'engagement_score'
        ]

    def _validate_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ensures the dataframe contains required columns and correct data types.
        """
        # Check columns
        for col in self.required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # Select only required columns
        df = df[self.required_columns].copy()

        # Cast types
        df['date'] = pd.to_datetime(df['date'])
        df['revenue_amount'] = pd.to_numeric(df['revenue_amount'])
        df['engagement_score'] = pd.to_numeric(df['engagement_score'])

        return df

    def load_csv(self, file_path: str) -> pd.DataFrame:
        """
        Loads data from a CSV file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        df = pd.read_csv(file_path)
        return self._validate_and_clean(df)

    def load_excel(self, file_path: str) -> pd.DataFrame:
        """
        Loads data from an Excel file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        df = pd.read_excel(file_path)
        return self._validate_and_clean(df)

if __name__ == "__main__":
    # This part is for manual testing
    print("DataIngestor initialized.")
