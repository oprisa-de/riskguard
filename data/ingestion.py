import pandas as pd
import numpy as np
from typing import List, Tuple
from datetime import datetime
import os

class DataIngestor:
    """
    Handles ingestion of data from various sources (CSV, Excel, SQL, API).
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
        Validates data integrity and handles missing values/invalid types gracefully.
        """
        # Check columns
        missing_cols = [col for col in self.required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

        # Select only required columns
        df = df[self.required_columns].copy()

        # Cast types - errors='coerce' will turn invalid entries into NaN
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['revenue_amount'] = pd.to_numeric(df['revenue_amount'], errors='coerce')
        df['engagement_score'] = pd.to_numeric(df['engagement_score'], errors='coerce')

        # --- Validation Rules ---
        # 1. Ensure engagement_score is between 0 and 1
        df['engagement_score'] = df['engagement_score'].clip(0.0, 1.0)

        # 2. Ensure revenue_amount is non-negative
        df['revenue_amount'] = df['revenue_amount'].clip(lower=0.0)

        # 3. Ensure date is not in the future
        df['date'] = df[df['date'].notna()]['date'].apply(lambda x: x if x <= pd.Timestamp.now() else pd.NaT)

        # Handle missing values for critical columns
        df['revenue_amount'] = df['revenue_amount'].fillna(0.0)
        df['engagement_score'] = df['engagement_score'].fillna(0.0)
        df['date'] = df['date'].fillna(pd.Timestamp.now())

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

    def load_from_sql(self, connection_string: str, query: str) -> pd.DataFrame:
        """
        Loads data from a SQL database.
        """
        # Placeholder for SQL connection logic
        # In a real production environment, we would use sqlalchemy or psycopg2
        print(f"Fetching data from SQL: {query}")
        df = pd.DataFrame({
            'customer_id': ['SQL_001'],
            'revenue_amount': [1000.0],
            'date': [pd.Timestamp.now()],
            'payment_status': ['Paid'],
            'category': ['Retail'],
            'engagement_score': [0.8]
        })
        return self._validate_and_clean(df)

    def load_from_api(self, endpoint: str) -> pd.DataFrame:
        """
        Loads data from a JSON-based API endpoint.
        """
        # Placeholder for API request logic
        # In a real production environment, we would use the requests library
        print(f"Fetching data from API: {endpoint}")
        data = [
            {'customer_id': 'API_001', 'revenue_amount': 1000.0, 'date': '2024-01-01',
             'payment_status': 'Paid', 'category': 'Retail', 'engagement_score': 0.7}
        ]
        df = pd.DataFrame(data)
        return self._validate_and_clean(df)
