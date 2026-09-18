import streamlit as st
import pandas as pd
import os
import sys

# Add parent dir to path for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard.data_loader import (
    get_fleet_metrics,
    get_available_chiller_ids,
    get_chiller_readings,
    get_expected_energy,
    get_anomaly_data
)
from dashboard.components import (
    inject_custom_css,
    render_chiller_selector_cards,
    render_fleet_metrics_summary,
    render_chiller_fleet_table,
    render_actual_energy_chart,
    render_contextual_operating_conditions,
    render_contextual_deviation_section,
    render_persistence_analysis,
    render_investigation_report,
    render_anomaly_replay_view
)

# Page Setup (Collapsed sidebar)
st.set_page_config(
    page_title="CHILLER FORENSICS // Telemetry Operations",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
inject_custom_css()

# Load Data
fleet_metrics = get_fleet_metrics()
chiller_ids = get_available_chiller_ids()
total_records = fleet_metrics.get("total_readings", len(chiller_ids))

# State Management for Selected Chiller
default_chiller = "CHILLER-01" if "CHILLER-01" in chiller_ids else (chiller_ids[0] if chiller_ids else "CHILLER-01")
if "selected_chiller" not in st.session_state:
    st.session_state["selected_chiller"] = default_chiller

if st.session_state["selected_chiller"] not in chiller_ids and chiller_ids:
    st.session_state["selected_chiller"] = chiller_ids[0]

# Centered Title Header with Muted Champagne Gold
st.markdown(
    f"""
    <div style="text-align: center; padding: 22px 0 16px 0; border-bottom: 1px solid rgba(191, 161, 95, 0.2); margin-bottom: 22px;">
        <h1 style="font-family: 'Cinzel', serif; font-size: 2.75rem; font-weight: 700; color: #E2E6EE; letter-spacing: 0.12em; margin: 0;">
            CHILLER FORENSICS
        </h1>
        <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.88rem; font-weight: 600; color: #BFA15F; letter-spacing: 0.16em; text-transform: uppercase; margin-top: 8px;">
            Thermodynamic Forensics & Anomaly Diagnostic Terminal
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; color: #7A8494; letter-spacing: 0.06em; margin-top: 6px;">
            SPEC: YUKTHI-2026 // SOURCE: development_dataset.csv ({total_records:,} OBSERVATIONS) // INTERVAL: 30 MINUTES // ML: ACTIVE
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Top 3 Clickable Chiller Selector Cards
selected_chiller = render_chiller_selector_cards(fleet_metrics["chiller_stats"], st.session_state["selected_chiller"])

# Load data for the active selected chiller
df_chiller = get_chiller_readings(selected_chiller)
expected_energy_series = get_expected_energy(selected_chiller)
anomaly_data = get_anomaly_data(selected_chiller)

# Active Target Banner
st.markdown(
    f"""
    <div style="display: flex; justify-content: space-between; align-items: baseline; background: #0E1218; border: 1px solid rgba(191, 161, 95, 0.2); border-left: 3px solid #BFA15F; padding: 10px 16px; margin: 16px 0 18px 0; border-radius: 3px;">
        <div>
            <span style="font-family: 'Cinzel', serif; font-size: 1.05rem; font-weight: 700; color: #BFA15F;">
                INSPECTION TARGET: {selected_chiller}
            </span>
            <span style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.80rem; color: #7A8494; margin-left: 12px;">
                {len(df_chiller):,} Readings Loaded
            </span>
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; color: #7A8494;">
            CALIBRATION: OUT-OF-BAG RESIDUALS // YUKTHI-2026 COMPLIANT
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Main Navigation Tabs for the selected chiller
tab_diag, tab_replay, tab_fleet = st.tabs([
    f"EQUIPMENT DIAGNOSTICS [{selected_chiller}]",
    f"CHRONOLOGICAL REPLAY [{selected_chiller}]",
    "FLEET OVERVIEW"
])

with tab_diag:
    # 1. Actual Energy Over Time Line Chart
    render_actual_energy_chart(df_chiller, expected_series=expected_energy_series, chiller_id=selected_chiller)
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 2. Contextual Operating Conditions & Selectable Variable Chart
    render_contextual_operating_conditions(df_chiller)
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 3. Contextual Deviation & Persistence
    col1, col2 = st.columns(2)
    with col1:
        render_contextual_deviation_section(anomaly_data)
    with col2:
        render_persistence_analysis(anomaly_data)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 4. Investigation Report
    render_investigation_report(anomaly_data)

with tab_replay:
    render_anomaly_replay_view(df_chiller, chiller_id=selected_chiller)

with tab_fleet:
    render_fleet_metrics_summary(fleet_metrics)
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    render_chiller_fleet_table(fleet_metrics["chiller_stats"])

# Footer
st.markdown(
    """
    <div style='margin-top: 36px; padding-top: 14px; border-top: 1px solid rgba(191, 161, 95, 0.16); display: flex; justify-content: space-between; font-family: monospace; font-size: 0.72rem; color: #505767;'>
        <span>CHILLER FORENSICS // YUKTHI 2026 SPECIFICATION COMPLIANT</span>
        <span>STATUS: OPERATIONAL // TELEMETRY REPLAY SYNCHRONIZED</span>
    </div>
    """,
    unsafe_allow_html=True
)
