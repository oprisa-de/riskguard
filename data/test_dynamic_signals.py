import pandas as pd
import numpy as np
from datetime import datetime
from data.risk_engine import RiskEngine

def test_dynamic_danger_signals():
    # Setup the engine
    engine = RiskEngine(risk_threshold=0.30)

    # Define test cases
    # 1. Overdue payment
    # 2. Significant engagement drop
    # 3. High-value revenue drop
    # 4. Normal stable behavior (no signals)
    data = {
        'customer_id': ['C1', 'C1', 'C1', 'C2', 'C2', 'C2', 'C3', 'C3', 'C3', 'C4', 'C4', 'C4'],
        'revenue_amount': [100000, 100000, 100000, 1000000, 1000000, 1000000, 50000, 50000, 50000, 500000, 500000, 500000],
        'date': [datetime(2024, 1, 1)] * 12,
        'payment_status': ['Paid', 'Paid', 'Overdue', 'Paid', 'Paid', 'Paid', 'Paid', 'Paid', 'Paid', 'Paid', 'Paid', 'Paid'],
        'engagement_score': [0.9, 0.9, 0.9, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8]
    }

    # Add specific test data
    df = pd.DataFrame(data)

    # Adjusting indices to have specific test cases
    # C1: Overdue (index 2)
    # C2: Engagement drop (index 5 - I'll manually set it)
    # C3: Stable (index 8)
    # C4: Revenue Drop (index 11)

    # Injecting the specific test cases
    df.loc[2, 'payment_status'] = 'Overdue'
    df.loc[5, 'engagement_score'] = 0.3  # Significant drop from 0.8
    df.loc[11, 'revenue_amount'] = 100000  # Significant drop from 500k

    # Create a fresh test set with distinct IDs
    test_df = pd.DataFrame({
        'customer_id': ['Test_Overdue', 'Test_Overdue'],
        'revenue_amount': [1000, 1000],
        'date': [datetime(2024,1,1), datetime(2024,1,2)],
        'payment_status': ['Paid', 'Overdue'],
        'engagement_score': [0.8, 0.8]
    })
    # 1. Test Overdue
    test_df_overdue = pd.DataFrame({
        'customer_id': ['Overdue_User', 'Overdue_User'],
        'revenue_amount': [1000, 1000],
        'date': [datetime(2024,1,1), datetime(2024,1,2)],
        'payment_status': ['Paid', 'Overdue'],
        'engagement_score': [0.8, 0.8]
    })

    # 2. Test Engagement Drop
    test_df_drop = pd.DataFrame({
        'customer_id': ['Drop_User', 'Drop_User', 'Drop_User'],
        'revenue_amount': [1000, 1000, 1000],
        'date': [datetime(2024,1,1), datetime(2024,1,2), datetime(2024,1,3)],
        'payment_status': ['Paid', 'Paid', 'Paid'],
        'engagement_score': [0.9, 0.9, 0.3]
    })

    # 3. Test Revenue Drop
    test_df_rev = pd.DataFrame({
        'customer_id': ['Rev_User', 'Rev_User', 'Rev_User'],
        'revenue_amount': [1000000, 1000000, 100000],
        'date': [datetime(2024,1,1), datetime(2024,1,2), datetime(2024,1,3)],
        'payment_status': ['Paid', 'Paid', 'Paid'],
        'engagement_score': [0.8, 0.8, 0.8]
    })

    print("Running test 1: Overdue detection...")
    overdue_res = engine.detect_danger_signals(test_df_overdue)
    assert any(s['signal_type'] == 'Payment Overdue' for s in overdue_res)
    print("Success: Overdue detected.")

    print("Running test 2: Engagement Drop detection...")
    drop_res = engine.detect_danger_signals(test_df_drop)
    assert any(s['signal_type'] == 'Engagement Drop' for s in drop_res)
    print("Success: Engagement drop detected.")

    print("Running test 3: Revenue Drop detection...")
    rev_res = engine.detect_danger_signals(test_df_rev)
    assert any(s['signal_type'] == 'Revenue Drop' for s in rev_res)
    print("Success: Revenue drop detected.")

    print("\nAll dynamic danger signal tests passed!")

if __name__ == "__main__":
    test_dynamic_danger_signals()
