import pandas as pd
import numpy as np
from typing import Any, Dict, List


class RiskEngine:
    """
    Analyzes customer revenue and interaction data to identify concentration risks,
    payment defaults, and early danger signals.
    """

    def __init__(self, risk_threshold: float = 0.30, overdue_rate_threshold: float = 0.20):
        """
        Args:
            risk_threshold: Share of total revenue (0.30 = 30%) above which a client
                            is flagged as concentrated.
            overdue_rate_threshold: Historical share of overdue invoices (0.20 = 20%)
                                    that triggers a recurring payment warning.
        """
        if not 0.0 < risk_threshold <= 1.0:
            raise ValueError("risk_threshold must be between 0.0 (exclusive) and 1.0 (inclusive).")
        self.risk_threshold = risk_threshold
        self.overdue_rate_threshold = overdue_rate_threshold

    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Returns a safely sorted copy without mutating the caller's DataFrame."""
        work_df = df.copy()
        if "date" in work_df.columns:
            work_df["date"] = pd.to_datetime(work_df["date"], errors="coerce")
            work_df = work_df.sort_values(by=["customer_id", "date"], kind="mergesort")
        else:
            work_df = work_df.sort_values(by=["customer_id"], kind="mergesort")
        return work_df

    def calculate_concentration_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates revenue share, concentration flags, and a composite risk score [0.0, 1.0]
        for each customer.
        """
        columns = [
            "customer_id",
            "revenue_amount",
            "revenue_share",
            "is_concentrated",
            "latest_status",
            "overdue_rate",
            "risk_score",
        ]
        if df.empty:
            return pd.DataFrame(columns=columns)

        work_df = self._prepare_dataframe(df)
        total_revenue = float(work_df["revenue_amount"].sum())

        client_totals = (
            work_df.groupby("customer_id", as_index=False)
            .agg(
                revenue_amount=("revenue_amount", "sum"),
                latest_status=("payment_status", "last"),
                overdue_rate=("payment_status", lambda s: float((s == "Overdue").mean())),
            )
        )

        if total_revenue > 0:
            client_totals["revenue_share"] = client_totals["revenue_amount"] / total_revenue
        else:
            client_totals["revenue_share"] = 0.0

        client_totals["is_concentrated"] = client_totals["revenue_share"] > self.risk_threshold

        # Composite risk score: 70% revenue concentration pressure + 30% payment default rate
        concentration_component = (client_totals["revenue_share"] / self.risk_threshold).clip(0.0, 1.0) * 0.70
        payment_component = client_totals["overdue_rate"].clip(0.0, 1.0) * 0.30
        client_totals["risk_score"] = (concentration_component + payment_component).round(2)

        client_totals["revenue_share"] = client_totals["revenue_share"].round(4)
        client_totals["overdue_rate"] = client_totals["overdue_rate"].round(2)

        return client_totals.sort_values(by="revenue_share", ascending=False).reset_index(drop=True)

    def identify_payment_risks(self, df: pd.DataFrame) -> List[str]:
        """Returns a sorted list of unique customer IDs with any 'Overdue' records."""
        if df.empty or "payment_status" not in df.columns:
            return []
        overdue_mask = df["payment_status"] == "Overdue"
        return sorted(df.loc[overdue_mask, "customer_id"].astype(str).unique().tolist())

    def detect_danger_signals(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identifies 'Danger Signals' including active or recurring payment delays,
        sharp engagement drops, and high-value revenue contractions.
        """
        if df.empty:
            return []

        signals: List[Dict[str, Any]] = []
        work_df = self._prepare_dataframe(df)

        for customer_id, group in work_df.groupby("customer_id", sort=False):
            cid = str(customer_id)
            latest_record = group.iloc[-1]

            # 1. Payment Overdue Detection (active default OR chronic overdue history)
            overdue_count = int((group["payment_status"] == "Overdue").sum())
            overdue_rate = overdue_count / len(group)

            if latest_record["payment_status"] == "Overdue":
                signals.append({
                    "customer_id": cid,
                    "signal_type": "Payment Overdue",
                    "severity": "High",
                    "description": (
                        f"Customer {cid} latest invoice is Overdue "
                        f"({overdue_count}/{len(group)} overdue records)."
                    ),
                })
            elif overdue_rate >= self.overdue_rate_threshold:
                signals.append({
                    "customer_id": cid,
                    "signal_type": "Payment Overdue",
                    "severity": "Medium",
                    "description": (
                        f"Customer {cid} shows recurring payment delays "
                        f"({overdue_count}/{len(group)} overdue records, {overdue_rate:.0%})."
                    ),
                })

            # 2. Dynamic Engagement Drop Detection (>30% drop vs. prior baseline)
            if len(group) > 1 and "engagement_score" in group.columns:
                historical_avg = float(group.iloc[:-1]["engagement_score"].mean())
                current_score = float(latest_record["engagement_score"])
                if not pd.isna(historical_avg) and not pd.isna(current_score) and historical_avg > 0:
                    if current_score < (historical_avg * 0.70):
                        signals.append({
                            "customer_id": cid,
                            "signal_type": "Engagement Drop",
                            "severity": "Medium",
                            "description": (
                                f"Customer {cid} engagement dropped to {current_score:.2f} "
                                f"(Historical avg: {historical_avg:.2f})."
                            ),
                        })

            # 3. High-Value Revenue Drop (>30% drop vs. prior baseline for accounts > 100k)
            if group["revenue_amount"].sum() > 100_000 and len(group) > 1:
                historical_rev_avg = float(group.iloc[:-1]["revenue_amount"].mean())
                current_rev = float(latest_record["revenue_amount"])
                if historical_rev_avg > 0 and current_rev < (historical_rev_avg * 0.70):
                    signals.append({
                        "customer_id": cid,
                        "signal_type": "Revenue Drop",
                        "severity": "High",
                        "description": (
                            f"Customer {cid} revenue dropped to {current_rev:,.2f} "
                            f"(Historical avg: {historical_rev_avg:,.2f})."
                        ),
                    })

        return signals

    def get_summary_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generates a consolidated risk and concentration summary report."""
        scores_df = self.calculate_concentration_scores(df)
        overdue_list = self.identify_payment_risks(df)
        signals = self.detect_danger_signals(df)

        concentrated_clients = (
            scores_df.loc[scores_df["is_concentrated"], "customer_id"].astype(str).tolist()
            if not scores_df.empty
            else []
        )
        max_risk_score = float(scores_df["risk_score"].max()) if not scores_df.empty else 0.0
        total_revenue = round(float(df["revenue_amount"].sum()), 2) if not df.empty else 0.0

        return {
            "total_revenue": total_revenue,
            "concentrated_clients": concentrated_clients,
            "overdue_clients": overdue_list,
            "danger_signals": signals,
            "max_risk_score": max_risk_score,
            "concentration_breakdown": scores_df.to_dict(orient="records"),
        }