import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List
from dataclasses import dataclass

@dataclass
class CustomerRecord:
    customer_id: str
    revenue_amount: float
    date: datetime
    payment_status: str  # 'Paid', 'Pending', 'Overdue'
    category: str
    engagement_score: float

class SyntheticDataGenerator:
    """
    Generates mock data for RiskGuard testing.
    Initial focus: 1M Euro monthly revenue starting Aug 2025.
    """
    def __init__(self):
        self.start_date = datetime(2025, 8, 1)

    def generate_client_history(self, customer_id: str, num_months: int) -> List[CustomerRecord]:
        records = []
        current_revenue = 1_000_000.0

        for i in range(num_months):
            current_date = self.start_date + timedelta(days=i*30)

            # Simulate realistic revenue growth/fluctuation
            growth_factor = np.random.uniform(0.95, 1.05)
            current_revenue *= growth_factor

            # Simulate payment status (90% success)
            status = "Paid" if np.random.random() > 0.1 else "Overdue"

            # Engagement score (0.0 to 1.0)
            engagement = np.random.uniform(0.6, 0.95)

            records.append(CustomerRecord(
                customer_id=customer_id,
                revenue_amount=round(current_revenue, 2),
                date=current_date,
                payment_status=status,
                category="Enterprise",
                engagement_score=round(engagement, 2)
            ))
        return records

    def generate_full_mock_dataset(self, num_clients: int, months: int) -> pd.DataFrame:
        all_records = []
        for i in range(num_clients):
            client_id = f"CLIENT_{i:03d}"
            records = self.generate_client_history(client_id, months)
            all_records.extend(records)

        df = pd.DataFrame([vars(r) for r in all_records])
        return df

if __name__ == "__main__":
    generator = SyntheticDataGenerator()
    df = generator.generate_full_mock_dataset(num_clients=5, months=12)
    print(f"Generated {len(df)} records.")
    print(df.head())
