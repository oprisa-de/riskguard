import pytest
import pandas as pd
import requests
from datetime import datetime

from data.ingestion import DataIngestor
from data.risk_engine import RiskEngine
from agents.profiler import ProfilerAgent
from graph.workflow import build_riskguard_graph


def test_data_ingestor_validation_and_coercion(tmp_path):
    csv_file = tmp_path / "sample.csv"
    df_raw = pd.DataFrame({
        "customer_id": ["C1", "C2"],
        "revenue_amount": [250000.0, "invalid_number"],
        "date": ["2025-08-01", "2025-09-01"],
        "payment_status": ["Paid", "Overdue"],
        "category": ["Enterprise", "Enterprise"],
        "engagement_score": [1.4, -0.2],  # Out-of-bounds values to test clipping
    })
    df_raw.to_csv(csv_file, index=False)

    ingestor = DataIngestor()
    cleaned = ingestor.load_csv(str(csv_file))

    assert len(cleaned) == 2
    assert cleaned.loc[1, "revenue_amount"] == 0.0
    assert cleaned.loc[0, "engagement_score"] == 1.0
    assert cleaned.loc[1, "engagement_score"] == 0.0


def test_data_ingestor_missing_columns():
    ingestor = DataIngestor()
    df_incomplete = pd.DataFrame({"customer_id": ["C1"], "revenue_amount": [1000.0]})

    with pytest.raises(ValueError, match="Missing required columns"):
        ingestor._validate_and_clean(df_incomplete)


def test_risk_engine_catches_100_percent_overdue_and_drops():
    engine = RiskEngine(risk_threshold=0.30, overdue_rate_threshold=0.20)
    df = pd.DataFrame({
        "customer_id": [
            "ALL_OVERDUE", "ALL_OVERDUE",
            "CHRONIC_LATE", "CHRONIC_LATE", "CHRONIC_LATE", "CHRONIC_LATE",
            "REV_DROP", "REV_DROP", "REV_DROP",
        ],
        "revenue_amount": [
            500000, 500000,
            200000, 200000, 200000, 200000,
            600000, 600000, 100000,
        ],
        "date": [
            datetime(2025, 8, 1), datetime(2025, 9, 1),
            datetime(2025, 8, 1), datetime(2025, 9, 1), datetime(2025, 10, 1), datetime(2025, 11, 1),
            datetime(2025, 8, 1), datetime(2025, 9, 1), datetime(2025, 10, 1),
        ],
        "payment_status": [
            "Overdue", "Overdue",
            "Overdue", "Paid", "Overdue", "Paid",
            "Paid", "Paid", "Paid",
        ],
        "engagement_score": [
            0.8, 0.8,
            0.8, 0.8, 0.8, 0.8,
            0.9, 0.9, 0.2,
        ],
    })

    report = engine.get_summary_report(df)
    signals = report["danger_signals"]

    assert "ALL_OVERDUE" in report["concentrated_clients"]
    assert any(s["customer_id"] == "ALL_OVERDUE" and s["signal_type"] == "Payment Overdue" for s in signals)
    assert any(s["customer_id"] == "CHRONIC_LATE" and s["signal_type"] == "Payment Overdue" for s in signals)
    assert any(s["customer_id"] == "REV_DROP" and s["signal_type"] == "Revenue Drop" for s in signals)
    assert any(s["customer_id"] == "REV_DROP" and s["signal_type"] == "Engagement Drop" for s in signals)


def test_risk_engine_handles_empty_dataframe():
    engine = RiskEngine()
    report = engine.get_summary_report(pd.DataFrame())

    assert report["total_revenue"] == 0.0
    assert report["concentrated_clients"] == []
    assert report["danger_signals"] == []
    assert report["max_risk_score"] == 0.0


def test_profiler_zero_revenue_and_risk_filtering():
    profiler = ProfilerAgent(revenue_threshold=500_000.0)
    df = pd.DataFrame({
        "customer_id": ["ZERO_START", "ZERO_START", "RISKY_WHALE", "RISKY_WHALE"],
        "revenue_amount": [0.0, 600_000.0, 1_000_000.0, 1_100_000.0],
        "date": [
            datetime(2025, 8, 1), datetime(2025, 9, 1),
            datetime(2025, 8, 1), datetime(2025, 9, 1),
        ],
        "payment_status": ["Paid", "Paid", "Overdue", "Overdue"],
        "engagement_score": [0.85, 0.90, 0.85, 0.85],
    })

    summary = profiler.get_summary(df)
    successful_ids = [p["id"] for p in summary["successful_profiles"]]

    assert "ZERO_START" in successful_ids
    assert "RISKY_WHALE" not in successful_ids
    assert "RISKY_WHALE" in summary["risk_alerts"]


def test_end_to_end_langgraph_workflow_with_fallback(tmp_path, monkeypatch):
    def mock_offline_post(*args, **kwargs):
        raise requests.ConnectionError("Simulated offline Ollama for unit test")

    monkeypatch.setattr(requests, "post", mock_offline_post)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "your_anthropic_api_key_here")

    csv_file = tmp_path / "portfolio.csv"
    df = pd.DataFrame({
        "customer_id": ["ANCHOR_A", "ANCHOR_A", "SMALL_B", "SMALL_B"],
        "revenue_amount": [1_200_000.0, 1_300_000.0, 150_000.0, 180_000.0],
        "date": ["2025-08-01", "2025-09-01", "2025-08-01", "2025-09-01"],
        "payment_status": ["Paid", "Paid", "Paid", "Overdue"],
        "category": ["Enterprise", "Enterprise", "Mid-Market", "Mid-Market"],
        "engagement_score": [0.92, 0.94, 0.65, 0.50],
    })
    df.to_csv(csv_file, index=False)

    app = build_riskguard_graph()
    result = app.invoke({"file_path": str(csv_file), "risk_threshold": 0.30})

    assert result["raw_records_count"] == 4
    assert "ANCHOR_A" in result["risk_report"]["concentrated_clients"]
    assert len(result["market_analysis"]["market_segments"]) >= 3
    assert result["diversification_roadmap"]["engine_used"] == "deterministic-fallback"
    assert len(result["diversification_roadmap"]["priority_actions"]) == 3