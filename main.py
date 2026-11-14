import os
import json
from data.mock_generator import MockDataGenerator
from graph.workflow import build_riskguard_graph


def main():
    sample_csv = "data/mock_sample.csv"
    if not os.path.exists(sample_csv):
        MockDataGenerator(sample_csv).generate_sample_csv()

    app = build_riskguard_graph()
    final_state = app.invoke({
        "file_path": sample_csv,
        "risk_threshold": 0.30,
    })

    risk = final_state["risk_report"]
    profiler = final_state["profiler_summary"]
    markets = final_state["market_analysis"]["market_segments"]
    roadmap = final_state["diversification_roadmap"]

    print("\n=== RISKGUARD MULTI-AGENT REPORT ===")
    print(f"Total Revenue Analyzed : €{risk['total_revenue']:,.2f}")
    print(f"Concentrated Clients   : {risk['concentrated_clients']} (Max Risk: {risk['max_risk_score']})")
    print(f"Overdue Accounts       : {risk['overdue_clients']}")
    print(f"Success DNA Profiles   : {profiler['successful_profiles_count']} / {profiler['total_profiles_analyzed']}")

    print("\n--- Target Expansion Segments (MarketScout) ---")
    for seg in markets:
        print(f"• {seg['segment']} [Score: {seg['score']:.2f}] -> {seg['reasoning']}")

    print(f"\n--- 90-Day Diversification Roadmap (ProjectArchitect | {roadmap['engine_used']}) ---")
    print(f"Summary: {roadmap['executive_summary']}")
    for step in roadmap["priority_actions"]:
        print(f"  [{step['phase']}] ({step['target_segment']}): {step['action']} -> Impact: {step['expected_impact']}")

    output_path = "riskguard_report.json"
    export_payload = {k: v for k, v in final_state.items() if k != "records"}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_payload, f, indent=2, ensure_ascii=False)
    print(f"\nFull JSON report exported to {output_path}")


if __name__ == "__main__":
    main()