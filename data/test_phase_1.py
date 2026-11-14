from synthetic_generator import SyntheticDataGenerator
from risk_engine import RiskEngine
import pandas as pd
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def run_phase_1_demo():
    logger.info("Initializing Phase 1: Risk & Concentration Analysis")

    # 1. Generate Synthetic Data
    # Simulate 5 clients with 12 months of data
    generator = SyntheticDataGenerator()
    df = generator.generate_full_mock_dataset(num_clients=5, months=12)

    logger.info(f"Generated {len(df)} data points for {df['customer_id'].nunique()} customers.")

    # 2. Analyze Risk
    # We set a 30% threshold for "High Concentration"
    engine = RiskEngine(risk_threshold=0.30)
    report = engine.get_summary_report(df)

    # 3. Output Results
    print("\n--- RiskGuard Analysis Report ---")
    print(f"Total Analyzed Revenue: €{report['total_revenue']:,.2f}")
    print(f"Concentrated Clients Found: {report['concentrated_clients']}")
    print(f"Overdue Accounts: {report['overdue_clients']}")
    print(f"Total High-Risk Concentration Count: {report['risk_count']}")
    print("--------------------------------\n")

    # Show the full concentration table
    print("Detailed Concentration Scores:")
    print(df.groupby('customer_id')['revenue_amount'].sum().reset_index())

if __name__ == "__main__":
    run_phase_1_demo()
