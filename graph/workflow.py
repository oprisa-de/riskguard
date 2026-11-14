from typing import Any, Dict, List, TypedDict
import pandas as pd
from langgraph.graph import StateGraph, START, END

from data.ingestion import DataIngestor
from data.risk_engine import RiskEngine
from agents.profiler import ProfilerAgent
from agents.market_scout import MarketScoutAgent
from agents.project_architect import ProjectArchitectAgent


class RiskGuardState(TypedDict, total=False):
    file_path: str
    risk_threshold: float
    raw_records_count: int
    records: List[Dict[str, Any]]
    risk_report: Dict[str, Any]
    profiler_summary: Dict[str, Any]
    market_analysis: Dict[str, Any]
    diversification_roadmap: Dict[str, Any]


def ingest_node(state: RiskGuardState) -> Dict[str, Any]:
    ingestor = DataIngestor()
    df = ingestor.load_csv(state["file_path"])
    return {
        "raw_records_count": int(len(df)),
        "records": df.to_dict(orient="records"),
    }


def risk_engine_node(state: RiskGuardState) -> Dict[str, Any]:
    df = pd.DataFrame(state["records"])
    engine = RiskEngine(risk_threshold=state.get("risk_threshold", 0.30))
    report = engine.get_summary_report(df)
    return {"risk_report": report}


def profiler_node(state: RiskGuardState) -> Dict[str, Any]:
    df = pd.DataFrame(state["records"])
    profiler = ProfilerAgent()
    summary = profiler.get_summary(df)
    return {"profiler_summary": summary}


def market_scout_node(state: RiskGuardState) -> Dict[str, Any]:
    successful_profiles = state.get("profiler_summary", {}).get("successful_profiles", [])
    scout = MarketScoutAgent()
    analysis = scout.get_summary(successful_profiles)
    return {"market_analysis": analysis}


def project_architect_node(state: RiskGuardState) -> Dict[str, Any]:
    risk_report = state.get("risk_report", {})
    segments = state.get("market_analysis", {}).get("market_segments", [])
    architect = ProjectArchitectAgent()
    roadmap = architect.build_roadmap(risk_report, segments)
    return {"diversification_roadmap": roadmap}


def build_riskguard_graph():
    """Compiles the end-to-end RiskGuard multi-agent LangGraph workflow."""
    builder = StateGraph(RiskGuardState)

    builder.add_node("ingest", ingest_node)
    builder.add_node("risk_engine", risk_engine_node)
    builder.add_node("profiler", profiler_node)
    builder.add_node("market_scout", market_scout_node)
    builder.add_node("project_architect", project_architect_node)

    builder.add_edge(START, "ingest")
    builder.add_edge("ingest", "risk_engine")
    builder.add_edge("risk_engine", "profiler")
    builder.add_edge("profiler", "market_scout")
    builder.add_edge("market_scout", "project_architect")
    builder.add_edge("project_architect", END)

    return builder.compile()