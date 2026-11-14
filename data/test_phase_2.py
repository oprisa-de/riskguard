import pandas as pd
import sys
import os
from typing import Dict
from risk_engine import RiskEngine
from ingestion import DataIngestor

def run_full_pipeline():
    # 1. Generate sample data
    from data.mock_generator import MockDataGenerator
    print("--- Initializing Mock Data ---")
    mock_path = "/riskguard/data/mock_sample.csv"
    generator = MockDataGenerator(mock_path)
    generator.generate_sample_csv()
    print(f"Created {mock_path}")

    # 2. Ingest data
    print("\n--- Ingesting Data ---")
    ingestor = DataIngestor()
    df = ingestor.load_csv(mock_path)
    print(f"Loaded {len(df)} records from CSV.")

    # 3. Analyze Risks
    print("\n--- Running Risk Analysis ---")
    # Set a 30% concentration threshold
    engine = RiskEngine(risk_threshold=0.30)
    report = engine.get_summary_report(df)

    # 4. Print Results
    print(f"Total Revenue: €{report['total_revenue']:,.2f}")
    print(f"Concentrated Clients: {report['concentrated_clients']}")
    print(f"Risk Count: {report['risk_count']}")
    print(f"Max Risk Score: {report['max_risk_score']}")
    print("\nDanger Signals Found:")
    if not report['danger_signals']:
        print("No immediate danger signals detected.")
    for signal in report['danger_signals']:
        print(f"- [{signal['severity']}] {signal['signal_type']}: {signal['description']} (ID: {signal['customer_id']})")

if __name__ == "__main__":
    # Support for running as a module
    sys.argv[0] = os.path.abspath(__file__)
    try:
        run_full_pipeline()
    except Exception as e:
        print(f"Error during execution: {e}")
