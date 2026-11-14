import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from profiler import ProfilerAgent

def test_profiler():
    data = {
        'customer_id': ['C1', 'C1', 'C2', 'C2', 'C3', 'C3'],
        'revenue_amount': [100000, 120000, 500000, 550000, 200000, 210000],
        'date': [datetime(2024, 1, 1)] * 6,
        'payment_status': ['Paid', 'Paid', 'Paid', 'Overdue', 'Paid', 'Paid'],
        'engagement_score': [0.9, 0.95, 0.4, 0.3, 0.8, 0.85]
    }
    df = pd.DataFrame(data)
    
    profiler = ProfilerAgent()
    summary = profiler.get_summary(df)
    
    print(f"Total Profiles: {summary['total_profiles_analyzed']}")
    print(f"Successful: {summary['successful_profiles_count']}")
    for p in summary['successful_profiles']:
        print(f"  - {p['id']}: {p['summary']}")
    print(f"Risk Alerts: {summary['risk_alerts']}")

if __name__ == "__main__":
    test_profiler()
