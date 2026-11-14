import pandas as pd
import numpy as np
from datetime import datetime
from data.ingestion import DataIngestor

def test_ingestion_robustness():
    ingestor = DataIngestor()

    # Case 1: Valid data
    print("Testing valid data...")
    df_valid = pd.DataFrame({
        'customer_id': ['C001'],
        'revenue_amount': [1000.0],
        'date': ['2023-01-01'],
        'payment_status': ['Paid'],
        'category': ['Retail'],
        'engagement_score': [0.8]
    })
    cleaned_valid = ingestor.load_csv("dummy_valid.csv") # Need to mock file existence or just use internal method
    # Since load_csv checks file existence, I'll call _validate_and_clean directly for unit tests
    cleaned_valid = ingestor._validate_and_clean(df_valid)
    print(f"Success: {cleaned_valid.shape == (1, 6)}")

    # Case 2: Missing required columns
    print("\nTesting missing columns...")
    df_missing = pd.DataFrame({
        'customer_id': ['C002'],
        'revenue_amount': [500.0]
        # missing other columns
    })
    try:
        ingestor._validate_and_clean(df_missing)
    except ValueError as e:
        print(f"Caught expected error: {e}")

    # Case 3: Invalid data types (handled by coerce)
    print("\nTesting invalid types (should be coerced to NaN then filled)...")
    df_invalid = pd.DataFrame({
        'customer_id': ['C003'],
        'revenue_amount': ['invalid_number'],
        'date': ['invalid_date'],
        'payment_status': ['Paid'],
        'category': ['Retail'],
        'engagement_score': ['invalid_score']
    })
    cleaned_invalid = ingestor._validate_and_clean(df_invalid)
    print(f"Revenue amount for C003: {cleaned_invalid.iloc[0]['revenue_amount']}")
    print(f"Date for C003: {cleaned_invalid.iloc[0]['date']}")

    # Case 4: Partial missing values (NaNs)
    print("\nTesting missing values (NaNs)...")
    df_nan = pd.DataFrame({
        'customer_id': ['C004'],
        'revenue_amount': [np.nan],
        'date': [pd.Timestamp('2023-01-01')],
        'payment_status': ['Paid'],
        'category': ['Retail'],
        'engagement_score': [np.nan]
    })
    cleaned_nan = ingestor._validate_and_clean(df_nan)
    print(f"Revenue for C004: {cleaned_nan.iloc[0]['revenue_amount']}")
    print(f"Engagement for C004: {cleaned_nan.iloc[0]['engagement_score']}")

if __name__ == "__main__":
    test_ingestion_robustness()
