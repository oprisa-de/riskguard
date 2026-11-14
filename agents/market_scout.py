import os
import json
import requests
from typing import Any, Dict, List
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

load_dotenv()


class MarketSegment(BaseModel):
    segment: str = Field(..., min_length=2, description="Target industry or market segment")
    score: float = Field(..., ge=0.0, le=1.0, description="Synergy score between 0.0 and 1.0")
    reasoning: str = Field(..., min_length=5, description="Strategic rationale for expansion")


class MarketScoutOutput(BaseModel):
    segments: List[MarketSegment]


class MarketScoutAgent:
    """
    Analyzes anonymized 'Success DNA' patterns from high-performing clients
    to identify and score new target industries for portfolio diversification.
    """

    def __init__(self, model_name: str | None = None, timeout: int = 60):
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "gemma4:12b")
        self.base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.timeout = timeout

    @staticmethod
    def _anonymize_profiles(profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Strips customer identifiers before passing behavioral metrics to an LLM."""
        anonymized = []
        for idx, profile in enumerate(profiles, start=1):
            anonymized.append({
                "pattern_id": f"SUCCESS_PATTERN_{idx}",
                "total_revenue": profile.get("total_revenue"),
                "growth_rate": profile.get("growth"),
                "engagement_score": profile.get("engagement"),
                "payment_reliability": profile.get("reliability"),
                "profile_archetype": profile.get("summary"),
            })
        return anonymized

    def _parse_and_validate(self, raw_content: str) -> List[Dict[str, Any]]:
        """Parses LLM JSON output and enforces the MarketSegment Pydantic schema."""
        parsed = json.loads(raw_content)

        if isinstance(parsed, list):
            raw_list = parsed
        elif isinstance(parsed, dict):
            raw_list = (
                parsed.get("segments")
                or parsed.get("market_segments")
                or next((v for v in parsed.values() if isinstance(v, list)), [])
            )
        else:
            raise ValueError("Unexpected JSON root type from LLM.")

        validated_segments: List[Dict[str, Any]] = []
        for item in raw_list:
            if not isinstance(item, dict):
                continue
            segment_obj = MarketSegment(
                segment=str(item.get("segment", "")).strip(),
                score=float(item.get("score", 0.0)),
                reasoning=str(item.get("reasoning", "")).strip(),
            )
            validated_segments.append(segment_obj.model_dump())

        if not validated_segments:
            raise ValidationError.from_exception_data("MarketScoutOutput", [])

        return sorted(validated_segments, key=lambda x: x["score"], reverse=True)

    def identify_new_markets(self, successful_profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generates 3-5 validated expansion market segments using local Ollama."""
        if not successful_profiles:
            return [
                MarketSegment(
                    segment="No Expansion Data",
                    score=0.0,
                    reasoning="No reliable high-performing client profiles met the Success DNA criteria.",
                ).model_dump()
            ]

        anonymized_patterns = self._anonymize_profiles(successful_profiles)

        prompt = (
            "You are a B2B portfolio diversification strategist.\n"
            f"Analyze these anonymized high-performing client patterns: {json.dumps(anonymized_patterns)}\n\n"
            "Identify 3 to 5 adjacent industries or market segments where this exact commercial profile "
            "(high engagement, reliable payment behavior, recurring enterprise revenue) can be replicated.\n"
            "Return ONLY a JSON object with a single key 'segments' containing a list of objects, "
            "each with exact keys: 'segment' (string), 'score' (float between 0.0 and 1.0), and 'reasoning' (string)."
        )

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "format": "json",
                    "stream": False,
                    "options": {"temperature": 0.4},
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            raw_content = response.json().get("response", "")
            return self._parse_and_validate(raw_content)
        except Exception as exc:
            print(f"[MarketScoutAgent] Falling back to deterministic segments ({exc})")
            return self._fallback_logic()

    @staticmethod
    def _fallback_logic() -> List[Dict[str, Any]]:
        """Deterministic fallback when Ollama is offline or returns invalid JSON."""
        fallback_items = [
            MarketSegment(
                segment="Mid-Market B2B SaaS & Cloud Infrastructure",
                score=0.86,
                reasoning="Matches recurring enterprise contract dynamics with high engagement and predictable billing cycles.",
            ),
            MarketSegment(
                segment="Industrial Supply Chain & Logistics Tech",
                score=0.79,
                reasoning="High operational stickiness and multi-month retention mirror top-performing anchor accounts.",
            ),
            MarketSegment(
                segment="Healthcare Operations & MedTech Providers",
                score=0.74,
                reasoning="Strong payment reliability and long-term vendor commitment reduce revenue volatility.",
            ),
        ]
        return [item.model_dump() for item in fallback_items]

    def get_summary(self, successful_profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Returns validated market segments ready for downstream strategic planning."""
        segments = self.identify_new_markets(successful_profiles)
        return {
            "market_segments": segments,
            "top_segment": segments[0]["segment"] if segments else None,
        }