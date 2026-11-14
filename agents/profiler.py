import pandas as pd
import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class ClientProfile:
    customer_id: str
    revenue_growth_rate: float
    avg_engagement_score: float
    payment_reliability: float
    risk_level: str
    summary: str

class ProfilerAgent:
    """
    The Profiler Agent analyzes historical customer data to identify
    'Success DNA' and high-value client profiles.
    """
    def __init__(self, revenue_threshold: float = 1000000.0):
        self.revenue_threshold = revenue_threshold

    def analyze_profiles(self, df: pd.DataFrame) -> List[ClientProfile]:
        """
        Identifies high-performing customers and segments them by engagement and revenue.
        """
        profiles = []

        # Group by customer to analyze historical data
        grouped = df.groupby('customer_id')

        for customer_id, group in grouped:
            # Calculate Metrics
            total_revenue = group['revenue_amount'].sum()
            avg_engagement = group['engagement_score'].mean()

            # Growth Rate (Simplistic: comparison of first and last record)
            sorted_group = group.sort_values('date')
            if len(sorted_group) > 1:
                initial_rev = sorted_group.iloc[0]['revenue_amount']
                final_rev = sorted_group.iloc[-1]['revenue_amount']
                growth = (final_rev - initial_rev) / initial_rev
            else:
                growth = 0.0

            # Payment Reliability
            overdue_count = (group['payment_status'] == 'Overdue').sum()
            reliability = 1.0 - (overdue_count / len(group))

            # Determine Success DNA
            # A "Successful" client has high revenue and high engagement
            is_high_value = total_revenue >= self.revenue_threshold
            is_engaged = avg_engagement > 0.7

            risk_level = "Low"
            if total_revenue > self.revenue_threshold * 2 and reliability < 0.8:
                risk_level = "High"
            elif reliability < 0.6:
                risk_level = "Medium"

            if is_high_value and is_engaged:
                summary = f"High-Value Anchor: Consistent engagement with high revenue contribution."
            elif is_high_value and not is_engaged:
                summary = f"Revenue Anchor: High revenue but declining engagement. Risk of churn."
            else:
                summary = "Standard Growth: Emerging client with steady engagement."

            profiles.append(ClientProfile(
                customer_id=str(customer_id),
                revenue_growth_rate=round(growth, 2),
                avg_engagement_score=round(avg_engagement, 2),
                payment_reliability=round(reliability, 2),
                risk_level=risk_level,
                summary=summary
            ))

        return profiles

    def get_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Provides a summary of the successful profiles found in the dataset.
        """
        profiles = self.analyze_profiles(df)

        successful_profiles = [
            p for p in profiles
            if p.revenue_growth_rate > 0.1 or p.avg_engagement_score > 0.8
        ]

        return {
            "total_profiles_analyzed": len(profiles),
            "successful_profiles_count": len(successful_profiles),
            "successful_profiles": [
                {
                    "id": p.customer_id,
                    "growth": p.revenue_growth_rate,
                    "engagement": p.avg_engagement_score,
                    "summary": p.summary
                } for p in successful_profiles
            ],
            "risk_alerts": [
                p.customer_id for p in profiles if p.risk_level == "High"
            ]
        }

if __name__ == "__main__":
    # Example Internal Test
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta

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
    print(f"Profiler Analysis Summary: {summary}")
