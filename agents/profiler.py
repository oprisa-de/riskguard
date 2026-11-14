import pandas as pd
import numpy as np
from typing import Any, Dict, List
from dataclasses import dataclass


@dataclass
class ClientProfile:
    customer_id: str
    revenue_growth_rate: float
    avg_engagement_score: float
    payment_reliability: float
    risk_level: str
    summary: str
    total_revenue: float = 0.0


class ProfilerAgent:
    """
    Analyzes historical customer data to identify 'Success DNA'
    (reliable, engaged, growing high-value clients) and flag risky accounts.
    """

    def __init__(
        self,
        revenue_threshold: float = 1_000_000.0,
        min_engagement: float = 0.70,
        min_reliability: float = 0.80,
    ):
        self.revenue_threshold = revenue_threshold
        self.min_engagement = min_engagement
        self.min_reliability = min_reliability

    def analyze_profiles(self, df: pd.DataFrame) -> List[ClientProfile]:
        """Segments customers by revenue trajectory, engagement, and payment reliability."""
        if df.empty:
            return []

        work_df = df.copy()
        if "date" in work_df.columns:
            work_df["date"] = pd.to_datetime(work_df["date"], errors="coerce")

        profiles: List[ClientProfile] = []

        for customer_id, group in work_df.groupby("customer_id", sort=False):
            total_revenue = float(group["revenue_amount"].sum())
            avg_engagement = float(group["engagement_score"].mean()) if "engagement_score" in group.columns else 0.0

            # Safe, deterministic revenue growth calculation
            sorted_group = (
                group.sort_values("date", kind="mergesort")
                if "date" in group.columns
                else group
            )
            if len(sorted_group) > 1:
                initial_rev = float(sorted_group.iloc[0]["revenue_amount"])
                final_rev = float(sorted_group.iloc[-1]["revenue_amount"])
                if initial_rev > 0:
                    growth = (final_rev - initial_rev) / initial_rev
                elif final_rev > 0:
                    growth = 1.0
                else:
                    growth = 0.0
            else:
                growth = 0.0

            # Payment reliability [0.0, 1.0]
            overdue_count = int((group["payment_status"] == "Overdue").sum())
            reliability = 1.0 - (overdue_count / len(group))

            is_high_value = total_revenue >= self.revenue_threshold
            is_engaged = avg_engagement >= self.min_engagement
            is_reliable = reliability >= self.min_reliability

            # Risk classification
            if (is_high_value and not is_reliable) or reliability < 0.50:
                risk_level = "High"
            elif not is_reliable or (is_high_value and not is_engaged):
                risk_level = "Medium"
            else:
                risk_level = "Low"

            # Profile summary
            if not is_reliable:
                summary = (
                    f"Payment Risk Account: Reliability at {reliability:.0%} "
                    f"({overdue_count}/{len(group)} overdue). Exclude from expansion template."
                )
            elif is_high_value and is_engaged:
                summary = "High-Value Anchor: Consistent engagement with strong revenue contribution."
            elif is_high_value and not is_engaged:
                summary = "Revenue Anchor: High revenue but declining engagement. Risk of churn."
            elif growth > 0.10 and is_engaged:
                summary = "High-Momentum Growth: Rapidly expanding account with strong engagement."
            else:
                summary = "Standard Growth: Emerging client with steady engagement."

            profiles.append(
                ClientProfile(
                    customer_id=str(customer_id),
                    revenue_growth_rate=round(float(growth), 2),
                    avg_engagement_score=round(float(avg_engagement), 2),
                    payment_reliability=round(float(reliability), 2),
                    risk_level=risk_level,
                    summary=summary,
                    total_revenue=round(total_revenue, 2),
                )
            )

        return profiles

    def get_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Returns a JSON-serializable summary of reliable 'Success DNA' profiles
        and active risk alerts for downstream agents.
        """
        profiles = self.analyze_profiles(df)

        successful_profiles = [
            p
            for p in profiles
            if p.risk_level == "Low"
            and p.payment_reliability >= self.min_reliability
            and p.avg_engagement_score >= self.min_engagement
            and (
                p.total_revenue >= self.revenue_threshold
                or p.revenue_growth_rate > 0.10
                or p.avg_engagement_score >= 0.80
            )
        ]

        return {
            "total_profiles_analyzed": int(len(profiles)),
            "successful_profiles_count": int(len(successful_profiles)),
            "successful_profiles": [
                {
                    "id": p.customer_id,
                    "total_revenue": float(p.total_revenue),
                    "growth": float(p.revenue_growth_rate),
                    "engagement": float(p.avg_engagement_score),
                    "reliability": float(p.payment_reliability),
                    "summary": p.summary,
                }
                for p in successful_profiles
            ],
            "risk_alerts": [
                p.customer_id for p in profiles if p.risk_level in ("High", "Medium")
            ],
        }