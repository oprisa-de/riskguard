import os
import json
import requests
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class RoadmapAction(BaseModel):
    phase: str = Field(..., description="Execution horizon, e.g., Days 1-30, Days 31-60, Days 61-90")
    action: str = Field(..., min_length=5, description="Concrete operational or commercial initiative")
    target_segment: str = Field(..., description="Target industry or account group")
    expected_impact: str = Field(..., description="Quantified or structural risk-reduction outcome")


class DiversificationRoadmap(BaseModel):
    executive_summary: str = Field(..., min_length=10)
    target_concentration_ceiling: float = Field(..., ge=0.05, le=0.50)
    priority_actions: List[RoadmapAction] = Field(..., min_length=1)
    kpis_to_track: List[str] = Field(..., min_length=1)
    engine_used: str = Field(default="deterministic-fallback")


class ProjectArchitectAgent:
    """
    Synthesizes concentration risk diagnostics and target market opportunities
    into an actionable 90-day portfolio diversification roadmap.
    Supports hybrid execution: Cloud Claude (if configured) -> Local Ollama -> Deterministic Fallback.
    """

    def __init__(self, use_cloud: bool = True, timeout: int = 60):
        self.use_cloud = use_cloud
        self.timeout = timeout
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "gemma4:12b")

    def _has_valid_anthropic_key(self) -> bool:
        return (
            self.use_cloud
            and bool(self.anthropic_key)
            and self.anthropic_key != "your_anthropic_api_key_here"
        )

    @staticmethod
    def _sanitize_risk_context(risk_report: Dict[str, Any]) -> Dict[str, Any]:
        """Builds an anonymized risk snapshot without exposing raw client IDs."""
        breakdown = risk_report.get("concentration_breakdown", [])
        top_shares = sorted(
            [round(float(row.get("revenue_share", 0.0)), 4) for row in breakdown],
            reverse=True,
        )[:3]
        signal_types = [s.get("signal_type") for s in risk_report.get("danger_signals", [])]

        return {
            "total_revenue": risk_report.get("total_revenue", 0.0),
            "concentrated_client_count": len(risk_report.get("concentrated_clients", [])),
            "overdue_client_count": len(risk_report.get("overdue_clients", [])),
            "max_risk_score": risk_report.get("max_risk_score", 0.0),
            "top_3_revenue_shares": top_shares,
            "active_danger_signal_types": signal_types,
        }

    def _build_prompt(
        self,
        sanitized_risk: Dict[str, Any],
        market_segments: List[Dict[str, Any]],
    ) -> str:
        return (
            "You are a Chief Strategy Officer specializing in B2B revenue concentration mitigation.\n"
            f"Anonymized Portfolio Risk Metrics: {json.dumps(sanitized_risk)}\n"
            f"Validated Target Expansion Segments: {json.dumps(market_segments)}\n\n"
            "Design a concrete 90-day diversification roadmap to reduce single-client dependency below 25%.\n"
            "Return ONLY a valid JSON object with exact keys:\n"
            "- 'executive_summary' (string)\n"
            "- 'target_concentration_ceiling' (float between 0.05 and 0.50)\n"
            "- 'priority_actions' (list of 3-4 objects with keys: 'phase', 'action', 'target_segment', 'expected_impact')\n"
            "- 'kpis_to_track' (list of 3-4 strings)"
        )

    def _call_anthropic(self, prompt: str) -> Dict[str, Any]:
        from anthropic import Anthropic

        client = Anthropic(api_key=self.anthropic_key)
        message = client.messages.create(
            model=self.anthropic_model,
            max_tokens=1200,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = message.content[0].text.strip()
        # Strip markdown fences if present
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        data = json.loads(raw_text)
        data["engine_used"] = f"anthropic:{self.anthropic_model}"
        return DiversificationRoadmap(**data).model_dump()

    def _call_ollama(self, prompt: str) -> Dict[str, Any]:
        response = requests.post(
            f"{self.ollama_host}/api/generate",
            json={
                "model": self.ollama_model,
                "prompt": prompt,
                "format": "json",
                "stream": False,
                "options": {"temperature": 0.3},
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        raw_text = response.json().get("response", "")
        data = json.loads(raw_text)
        data["engine_used"] = f"ollama:{self.ollama_model}"
        return DiversificationRoadmap(**data).model_dump()

    @staticmethod
    def _fallback_roadmap(
        sanitized_risk: Dict[str, Any],
        market_segments: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        primary_segment = (
            market_segments[0]["segment"]
            if market_segments
            else "Adjacent Enterprise Verticals"
        )
        secondary_segment = (
            market_segments[1]["segment"]
            if len(market_segments) > 1
            else "Mid-Market Recurring Accounts"
        )
        conc_count = sanitized_risk.get("concentrated_client_count", 0)

        roadmap = DiversificationRoadmap(
            executive_summary=(
                f"Portfolio currently exhibits {conc_count} concentrated account(s) "
                f"(max risk score: {sanitized_risk.get('max_risk_score', 0.0)}). "
                f"Immediate outbound replication in {primary_segment} is required to cap single-client share at 25%."
            ),
            target_concentration_ceiling=0.25,
            priority_actions=[
                RoadmapAction(
                    phase="Days 1-30",
                    action="Enforce credit controls on overdue accounts and package top-client case studies into vertical playbooks.",
                    target_segment="Existing High-Risk & Anchor Accounts",
                    expected_impact="Stabilize cash collection and isolate churn exposure.",
                ),
                RoadmapAction(
                    phase="Days 31-60",
                    action=f"Launch targeted outbound pilot (20 qualified prospects) replicating Success DNA in {primary_segment}.",
                    target_segment=primary_segment,
                    expected_impact="Generate 3-5 new mid-tier pipeline opportunities to dilute top-2 revenue share.",
                ),
                RoadmapAction(
                    phase="Days 61-90",
                    action=f"Expand commercial acquisition into {secondary_segment} and introduce multi-year volume incentives.",
                    target_segment=secondary_segment,
                    expected_impact="Reduce single-client revenue concentration below the 25% safety threshold.",
                ),
            ],
            kpis_to_track=[
                "Top-1 Client Revenue Share (< 25%)",
                "Top-3 Client Concentration Ratio (< 55%)",
                "Portfolio Overdue Invoice Rate (< 5%)",
                "New-Vertical Pipeline Contribution (%)",
            ],
            engine_used="deterministic-fallback",
        )
        return roadmap.model_dump()

    def build_roadmap(
        self,
        risk_report: Dict[str, Any],
        market_segments: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generates a validated DiversificationRoadmap dictionary."""
        sanitized_risk = self._sanitize_risk_context(risk_report)
        prompt = self._build_prompt(sanitized_risk, market_segments)

        if self._has_valid_anthropic_key():
            try:
                return self._call_anthropic(prompt)
            except Exception as exc:
                print(f"[ProjectArchitectAgent] Cloud Claude unavailable, switching to Ollama ({exc})")

        try:
            return self._call_ollama(prompt)
        except Exception as exc:
            print(f"[ProjectArchitectAgent] Ollama unavailable, using deterministic roadmap ({exc})")
            return self._fallback_roadmap(sanitized_risk, market_segments)