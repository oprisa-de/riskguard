import pandas as pd
import numpy as np
from datetime import datetime
from agents.profiler import ProfilerAgent
from agents.market_scout import MarketScoutAgent

def test_market_scout():
    # 1. Setup Mock Data
    data = {
        'customer_id': ['C1', 'C2', 'C3'],
        'revenue_amount': [1000000, 1500000, 2000000],
        'date': [datetime(2024, 1, 1)] * 3,
        'payment_status': ['Paid', 'Paid', 'Paid'],
        'engagement_score': [0.9, 0.95, 0.85]
    }
    df = pd.DataFrame(data)

    # 2. Run Profiler
    profiler = ProfilerAgent()
    summary = profiler.get_summary(df)
    successful_profiles = summary['successful_profiles']

    print(f"Profiler identified {len(successful_profiles)} successful profiles.")

    # 3. Run Market Scout
    scout = MarketScoutAgent()
    market_analysis = scout.get_summary(successful_profiles)

    print(f"Market Scout Analysis Results:")
    for segment in market_analysis['market_segments']:
        print(f"- {segment['segment']} (Score: {segment['score']}): {segment['reasoning']}")

if __name__ == "__main__":
    test_market_scout()
