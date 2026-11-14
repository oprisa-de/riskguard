import os
import json
import tempfile
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data.mock_generator import MockDataGenerator
from data.ingestion import DataIngestor
from graph.workflow import build_riskguard_graph

st.set_page_config(
    page_title="RiskGuard | Portfolio Diversification Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _prepare_input_file(data_source: str, uploaded_file) -> str | None:
    """Returns a valid CSV path for the LangGraph workflow (supports CSV & Excel uploads)."""
    if data_source == "Synthetic Portfolio Demo":
        sample_path = "data/mock_sample.csv"
        if not os.path.exists(sample_path):
            MockDataGenerator(sample_path).generate_sample_csv()
        return sample_path

    if uploaded_file is None:
        return None

    suffix = os.path.splitext(uploaded_file.name)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_in:
        tmp_in.write(uploaded_file.getbuffer())
        raw_path = tmp_in.name

    if suffix in (".xlsx", ".xls"):
        df_clean = DataIngestor().load_excel(raw_path)
        csv_path = raw_path + ".csv"
        df_clean.to_csv(csv_path, index=False)
        return csv_path

    return raw_path


def main():
    st.title("🛡️ RiskGuard: AI-Powered Portfolio Diversification Engine")
    st.caption(
        "Privacy-First Multi-Agent Intelligence • Concentration Risk Scoring, Danger Signals & 90-Day Strategy"
    )

    # --- Sidebar Configuration ---
    with st.sidebar:
        st.header("⚙️ Configuration")
        data_source = st.radio(
            "Portfolio Data Source",
            options=["Synthetic Portfolio Demo", "Upload CSV / Excel"],
            index=0,
        )

        uploaded_file = None
        if data_source == "Upload CSV / Excel":
            uploaded_file = st.file_uploader(
                "Upload client revenue file",
                type=["csv", "xlsx", "xls"],
                help="Required columns: customer_id, revenue_amount, date, payment_status, category, engagement_score",
            )

        risk_threshold_pct = st.slider(
            "Concentration Risk Threshold (%)",
            min_value=10,
            max_value=60,
            value=30,
            step=5,
            help="Clients exceeding this share of total revenue trigger a concentration alert.",
        )
        risk_threshold = risk_threshold_pct / 100.0

        run_clicked = st.button("🚀 Run Multi-Agent Pipeline", type="primary", use_container_width=True)

        st.divider()
        st.markdown(
            "**Pipeline Nodes:**\n"
            "1. `DataIngestor` (Validation)\n"
            "2. `RiskEngine` (Concentration & Alerts)\n"
            "3. `ProfilerAgent` (Success DNA)\n"
            "4. `MarketScoutAgent` (Ollama / GDPR-Safe)\n"
            "5. `ProjectArchitectAgent` (90-Day Plan)"
        )

    # --- Execute LangGraph Pipeline ---
    if run_clicked:
        file_path = _prepare_input_file(data_source, uploaded_file)
        if not file_path:
            st.warning("Please upload a CSV or Excel file before running the analysis.")
            return

        with st.spinner("Running LangGraph multi-agent workflow (RiskEngine → Profiler → MarketScout → Architect)..."):
            try:
                app = build_riskguard_graph()
                final_state = app.invoke({
                    "file_path": file_path,
                    "risk_threshold": risk_threshold,
                })
                st.session_state["riskguard_result"] = final_state
                st.session_state["active_threshold"] = risk_threshold_pct
            except Exception as exc:
                st.error(f"Pipeline execution failed: {exc}")
                return

    if "riskguard_result" not in st.session_state:
        st.info("Configure your threshold in the sidebar and click **Run Multi-Agent Pipeline** to analyze the portfolio.")
        return

    result = st.session_state["riskguard_result"]
    active_threshold = st.session_state.get("active_threshold", risk_threshold_pct)
    risk = result["risk_report"]
    profiler = result["profiler_summary"]
    markets = result["market_analysis"]["market_segments"]
    roadmap = result["diversification_roadmap"]

    # --- Top KPI Strip ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue Analyzed", f"€{risk['total_revenue']:,.2f}")
    col2.metric(
        "Concentrated Clients",
        f"{len(risk['concentrated_clients'])}",
        delta=f"Max Risk: {risk['max_risk_score']:.2f}",
        delta_color="inverse",
    )
    col3.metric(
        "Overdue Accounts",
        f"{len(risk['overdue_clients'])}",
        delta=f"{len(risk['danger_signals'])} Danger Signals",
        delta_color="inverse" if risk["overdue_clients"] else "normal",
    )
    col4.metric(
        "Success DNA Profiles",
        f"{profiler['successful_profiles_count']} / {profiler['total_profiles_analyzed']}",
        delta="Verified Low-Risk",
    )

    st.divider()

    # --- Interactive Charts ---
    breakdown_df = pd.DataFrame(risk.get("concentration_breakdown", []))
    if not breakdown_df.empty:
        chart_col1, chart_col2 = st.columns([3, 2])

        with chart_col1:
            st.subheader("Revenue Concentration vs. Safety Red Line")
            breakdown_df["revenue_share_pct"] = (breakdown_df["revenue_share"] * 100).round(2)
            breakdown_df["Status"] = breakdown_df["is_concentrated"].map(
                {True: f"Concentrated (>{active_threshold}%)", False: "Within Threshold"}
            )
            fig_bar = px.bar(
                breakdown_df,
                x="customer_id",
                y="revenue_share_pct",
                color="Status",
                text="revenue_share_pct",
                color_discrete_map={
                    f"Concentrated (>{active_threshold}%)": "#EF4444",
                    "Within Threshold": "#10B981",
                },
                labels={"customer_id": "Client ID", "revenue_share_pct": "Revenue Share (%)"},
            )
            fig_bar.add_hline(
                y=active_threshold,
                line_dash="dash",
                line_color="#F59E0B",
                annotation_text=f"Red Line ({active_threshold}%)",
            )
            fig_bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_bar.update_layout(height=380, margin=dict(t=20, b=20))
            st.plotly_chart(fig_bar, use_container_width=True)

        with chart_col2:
            st.subheader("Portfolio Revenue Distribution")
            fig_pie = go.Figure(
                data=[
                    go.Pie(
                        labels=breakdown_df["customer_id"],
                        values=breakdown_df["revenue_amount"],
                        hole=0.45,
                        textinfo="label+percent",
                    )
                ]
            )
            fig_pie.update_layout(height=380, margin=dict(t=20, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)

    # --- Multi-Agent Output Tabs ---
    tab1, tab2, tab3 = st.tabs([
        "🚨 Danger Signals & Risk Matrix",
        "🧬 Success DNA & Market Scout",
        "🗺️ 90-Day Diversification Roadmap",
    ])

    with tab1:
        st.subheader("Active Danger Signals")
        signals = risk.get("danger_signals", [])
        if not signals:
            st.success("No active payment delays, engagement drops, or revenue contractions detected.")
        else:
            for sig in signals:
                badge = "🔴" if sig["severity"] == "High" else "🟠"
                st.warning(f"{badge} **[{sig['severity']}] {sig['signal_type']}** (`{sig['customer_id']}`): {sig['description']}")

        st.subheader("Client Concentration & Payment Breakdown")
        if not breakdown_df.empty:
            display_df = breakdown_df[
                ["customer_id", "revenue_amount", "revenue_share_pct", "latest_status", "overdue_rate", "risk_score", "is_concentrated"]
            ].rename(
                columns={
                    "customer_id": "Client ID",
                    "revenue_amount": "Total Revenue (€)",
                    "revenue_share_pct": "Share (%)",
                    "latest_status": "Latest Invoice",
                    "overdue_rate": "Overdue Rate",
                    "risk_score": "Composite Risk",
                    "is_concentrated": "Concentrated",
                }
            )
            st.dataframe(display_df, use_container_width=True, hide_index=True)

    with tab2:
        left_col, right_col = st.columns(2)
        with left_col:
            st.subheader("🧬 Extracted Success DNA Accounts")
            profiles = profiler.get("successful_profiles", [])
            if not profiles:
                st.info("No clients met the reliability and engagement thresholds.")
            for prof in profiles:
                with st.container(border=True):
                    st.markdown(f"**{prof['id']}** — €{prof['total_revenue']:,.2f}")
                    st.caption(prof["summary"])
                    st.write(
                        f"Growth: `{prof['growth']:+.0%}` | "
                        f"Engagement: `{prof['engagement']:.2f}` | "
                        f"Reliability: `{prof['reliability']:.0%}`"
                    )

        with right_col:
            st.subheader("🔭 Target Expansion Verticals (GDPR-Safe)")
            for seg in markets:
                with st.container(border=True):
                    st.markdown(f"**{seg['segment']}** (Synergy Score: `{seg['score']:.2f}`)")
                    st.progress(min(max(float(seg["score"]), 0.0), 1.0))
                    st.write(seg["reasoning"])

    with tab3:
        st.subheader(f"90-Day Strategic Execution Plan (`{roadmap['engine_used']}`)")
        st.info(f"**Executive Summary:** {roadmap['executive_summary']}")

        for action in roadmap.get("priority_actions", []):
            with st.container(border=True):
                st.markdown(f"### {action['phase']} — {action['target_segment']}")
                st.write(f"**Action:** {action['action']}")
                st.caption(f"**Expected Impact:** {action['expected_impact']}")

        st.markdown("#### 📊 Key Performance Indicators (KPIs)")
        for kpi in roadmap.get("kpis_to_track", []):
            st.markdown(f"- {kpi}")

        export_payload = {k: v for k, v in result.items() if k != "records"}
        st.download_button(
            label="📥 Download Full JSON Report",
            data=json.dumps(export_payload, indent=2, ensure_ascii=False),
            file_name="riskguard_report.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()