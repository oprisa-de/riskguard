import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class RiskEngine:
    """
    Analyzes customer data to identify concentration risks and payment issues.
    """
    def __init__(self, risk_threshold: float = 0.30):
        """
        Args:
            risk_threshold: The percentage of total revenue (0.30 = 30%)
                             that triggers a concentration warning.
        """
        self.risk_threshold = risk_threshold

    def calculate_concentration_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Identifies which customers exceed the risk threshold and calculates a risk score.
        """
        # Group by customer to see total revenue per client
        client_totals = df.groupby('customer_id')['revenue_amount'].sum().reset_index()

        # Calculate total company revenue
        total_revenue = client_totals['revenue_amount'].sum()

        # Calculate share percentage
        client_totals['revenue_share'] = client_totals['revenue_amount'] / total_revenue

        # Flag high risk
        client_totals['is_concentrated'] = client_totals['revenue_share'] > self.risk_threshold

        # Calculate Risk Score (0-100)
        # Scoring Logic:
        # 70% Concentration (Revenue Share) + 30% Payment Status (Overdue = 100%, Paid = 0%)

        # Get the latest payment status for each client
        latest_status = df.sort_values('date').groupby('customer_id')['payment_status'].last()

        # Calculate Score
        # The revenue share is multiplied by 100 to get a 0-100 scale
        # The overdue check gives 100 if Overdue, else 0.
        client_totals['risk_score'] = (
            (client_totals['revenue_share'] * 100 * 0.7) +
            (client_totals['customer_id'].map(lambda x: 100 if latest_status[x] == 'Overdue' else 0) * 0.3)
        ).round(2)

        # Ensure the score is capped at 100
        client_totals['risk_score'] = client_totals['risk_score'].clip(upper=100.0)

        return client_totals

    def identify_payment_risks(self, df: pd.DataFrame) -> List[Tuple[str, str]]:
        """
        Finds customers with 'Overdue' status.
        """
        overdue_records = df[df['payment_status'] == 'Overdue']
        return list(overdue_records['customer_id'].unique())

    def detect_danger_signals(self, df: pd.DataFrame) -> List[Dict]:
        """
        Identifies 'Danger Signals' such as payment delays or significant drops in engagement.
        """
        signals = []

        # 1. Detect Overdue Payments
        overdue_customers = df[df['payment_status'] == 'Overdue']['customer_id'].unique()
        for customer in overdue_customers:
            signals.append({
                "customer_id": customer,
                "signal_type": "Payment Overdue",
                "severity": "High",
                "description": f"Customer {customer} has overdue payment records."
            })

        # 2. Detect Significant Engagement Drops
        # If average engagement score is below 0.5, flag as a potential drop
        low_engagement = df[df['engagement_score'] < 0.5].groupby('customer_id').size()
        for customer, count in low_engagement.items():
            if count > 1:
                signals.append({
                    "customer_id": customer,
                    "signal_type": "Engagement Drop",
                    "severity": "Medium",
                    "description": f"Customer {customer} shows consistently low engagement scores."
                })

        return signals

    def get_summary_report(self, df: pd.DataFrame) -> Dict:
        """
        Generates a high-level overview of current risks.
        """
        client_totals = self.calculate_concentration_scores(df)
        overdue_list = self.identify_payment_risks(df)
        danger_signals = self.detect_danger_signals(df)

        summary = {
            "total_revenue": df['revenue_amount'].sum(),
            "concentrated_clients": client_totals[client_totals['is_concentrated'] == True]['customer_id'].tolist(),
            "overdue_clients": overdue_list,
            "danger_signals": danger_signals,
            "max_risk_score": client_totals['risk_score'].max()
        }
        return summary

if __name__ == "__main__":
    # Example usage (internal test)
    import pandas as pd
    # Dummy data for testing
    data = {
        'customer_id': ['C1', 'C1', 'C2', 'C2'],
        'revenue_amount': [500000, 500000, 100000, 100000],
        'payment_status': ['Paid', 'Overdue', 'Paid', 'Paid'],
        'date': [pd.Timestamp('2025-08-01')] * 4
    }
    df = pd.DataFrame(data)

    engine = RiskEngine(risk_threshold=0.4)
    report = engine.get_summary_report(df)
    print(f"Report Summary: {report}")
