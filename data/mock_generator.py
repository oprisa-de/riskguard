import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
import os

@dataclass
class CustomerRecord:
    customer_id: str
    revenue_amount: float
    date: datetime
    payment_status: str
    category: str
    engagement_score: float

class MockDataGenerator:
    """
    Generates a sample CSV file representing a diverse customer base
    with a few high-revenue/concentrated accounts.
    """
    def __init__(self, output_path: str):
        self.output_path = output_path

    def generate_sample_csv(self):
        records = []
        # Generate 15 records for 5 customers
        # 1: Loyal (Stable, mid-range)
        # 2: Whale (Very high revenue, low risk)
        # 3: Volatile (High risk, frequent overdue)
        # 4: Growth (Consistent growth)
        # 5: Legacy (Low revenue, high engagement)

        profiles = [
            {"id": "CLIENT_001", "base": 500000, "growth": 0.05, "risk": 0.05},
            {"id": "CLIENT_002", "base": 1200000, "growth": 0.10, "risk": 0.05},
            {"id": "CLIENT_003", "base": 300000, "growth": 0.20, "risk": 0.30},
            {"id": "CLIENT_004", "base": 1000000, "growth": 0.12, "risk": 0.05},
            {"id": "CLIENT_005", "base": 100000, "growth": 0.02, "risk": 0.10},
        ]

        for p in profiles:
            current_revenue = p["base"]
            for i in range(6): # 6 months of history
                date = datetime(2025, 8, 1) + timedelta(days=i*30)
                status = "Paid"
                if np.random.random() < p["risk"]:
                    status = "Overdue"

                engagement = np.random.uniform(0.6, 1.0) if p["risk"] < 0.2 else np.random.uniform(0.3, 0.7)

                records.append({
                    "customer_id": p["id"],
                    "revenue_amount": round(current_revenue * (1 + p["growth"] * (i/6)), 2),
                    "date": date,
                    "payment_status": status,
                    "category": "Enterprise",
                    "engagement_score": round(engagement, 2)
                })

        df = pd.DataFrame(records)
        df.to_csv(self.output_path, index=False)
        print(f"Mock data saved to {self.output_path}")

if __name__ == "__main__":
    # Example run
    path = "/riskguard/data/mock_sample.csv"
    gen = MockDataGenerator(path)
    gen.generate_sample_csv()
