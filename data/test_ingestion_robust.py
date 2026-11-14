import pandas as pd
import numpy as np
import pytest
from data.ingestion import DataIngestor


def test_ingestion_robustness():
    ingestor = DataIngestor()

    # Case 1: Valid data
    df_valid = pd.DataFrame({
        "customer_id": ["C001"],
        "revenue_amount": [1000.0],
        "date": ["2023-01-01"],
        "payment_status": ["Paid"],
        "category": ["Retail"],
        "engagement_score": [0.8],
    })
    cleaned_valid = ingestor._validate_and_clean(df_valid)
    assert cleaned_valid.shape == (1, 6)

    # Case 2: Missing required columns
    df_missing = pd.DataFrame({
        "customer_id": ["C002"],
        "revenue_amount": [500.0],
    })
    with pytest.raises(ValueError, match="Missing required columns"):
        ingestor._validate_and_clean(df_missing)

    # Case 3: Invalid data types (coerced to NaN then filled)
    df_invalid = pd.DataFrame({
        "customer_id": ["C003"],
        "revenue_amount": ["invalid_number"],
        "date": ["invalid_date"],
        "payment_status": ["Paid"],
        "category": ["Retail"],
        "engagement_score": ["invalid_score"],
    })
    cleaned_invalid = ingestor._validate_and_clean(df_invalid)
    assert cleaned_invalid.iloc[0]["revenue_amount"] == 0.0
    assert cleaned_invalid.iloc[0]["engagement_score"] == 0.0

    # Case 4: Partial missing values (NaNs)
    df_nan = pd.DataFrame({
        "customer_id": ["C004"],
        "revenue_amount": [np.nan],
        "date": [pd.Timestamp("2023-01-01")],
        "payment_status": ["Paid"],
        "category": ["Retail"],
        "engagement_score": [np.nan],
    })
    cleaned_nan = ingestor._validate_and_clean(df_nan)
    assert cleaned_nan.iloc[0]["revenue_amount"] == 0.0
    assert cleaned_nan.iloc[0]["engagement_score"] == 0.0


if __name__ == "__main__":
    test_ingestion_robustness()
    print("All ingestion robustness tests passed!")
