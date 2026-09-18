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
    render_fleet_metrics_summary,
    render_chiller_fleet_table,
    render_actual_energy_chart,
    render_contextual_operating_conditions,
    render_contextual_deviation_section,
    render_persistence_analysis,
    render_investigation_report,
    render_anomaly_replay_view
)

# Page Setup
st.set_page_config(
    page_title="Chiller Forensics // Telemetry Operations",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
inject_custom_css()

# Industrial Operations Header
st.markdown(
    """
    <div style="border-bottom: 1px solid #1E2330; padding-bottom: 10px; margin-bottom: 18px;">
        <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px;">
            <div style="display: flex; align-items: baseline; gap: 12px;">
                <span style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF; letter-spacing: 0.05em; font-family: monospace;">CHILLER FORENSICS</span>
                <span style="font-size: 0.80rem; font-weight: 600; color: #C8A252; letter-spacing: 0.08em; text-transform: uppercase;">Operations Terminal</span>
            </div>
            <div style="font-family: monospace; font-size: 0.76rem; color: #626B7E;">
                SPEC: YUKTHI-2026 // MODEL: RANDOM FOREST ENSEMBLE // RUNTIME: ACTIVE
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar Navigation
chiller_ids = get_available_chiller_ids()
default_chiller = "CHILLER-01" if "CHILLER-01" in chiller_ids else (chiller_ids[0] if chiller_ids else "CHILLER-01")

st.sidebar.markdown(
    """
    <div style="font-size: 0.70rem; font-weight: 700; color: #7C8394; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 6px;">
        Equipment Directory
    </div>
    """,
    unsafe_allow_html=True
)

selected_chiller = st.sidebar.selectbox(
    "Select Chiller Asset:",
    options=chiller_ids,
    index=chiller_ids.index(default_chiller) if default_chiller in chiller_ids else 0,
    label_visibility="collapsed"
)

fleet_metrics = get_fleet_metrics()
total_records = fleet_metrics.get("total_readings", len(chiller_ids))

st.sidebar.markdown(
    f"""
    <div style="border-top: 1px solid #1E2330; margin-top: 20px; padding-top: 14px; font-family: monospace; font-size: 0.74rem; color: #626B7E; line-height: 1.8;">
        <div>DATASET: <span style="color: #C8A252;">development_dataset.csv</span></div>
        <div>OBSERVATIONS: <span style="color: #ECECEE;">{total_records:,}</span></div>
        <div>INTERVAL: <span style="color: #ECECEE;">30 MINUTES</span></div>
        <div>CALIBRATION: <span style="color: #ECECEE;">OUT-OF-BAG RESIDUALS</span></div>
    </div>
    """,
    unsafe_allow_html=True
)

# Load data for selected equipment
df_chiller = get_chiller_readings(selected_chiller)
expected_energy_series = get_expected_energy(selected_chiller)
anomaly_data = get_anomaly_data(selected_chiller)

# Main Tabs Navigation
tab_fleet, tab_investigation, tab_replay = st.tabs([
    "FLEET TELEMETRY",
    f"DIAGNOSTICS [{selected_chiller}]",
    f"CHRONOLOGICAL REPLAY [{selected_chiller}]"
])

with tab_fleet:
    render_fleet_metrics_summary(fleet_metrics)
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    render_chiller_fleet_table(fleet_metrics["chiller_stats"])

with tab_investigation:
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px;">
            <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF; font-family: monospace;">EQUIPMENT DIAGNOSTICS: {selected_chiller}</div>
            <div style="font-size: 0.78rem; color: #7C8394; font-family: monospace;">SOURCE: development_dataset.csv</div>
        </div>
        """,
        unsafe_allow_html=True
    )

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

# Footer
st.markdown(
    """
    <div style='margin-top: 36px; padding-top: 14px; border-top: 1px solid #1E2330; display: flex; justify-content: space-between; font-family: monospace; font-size: 0.72rem; color: #505767;'>
        <span>CHILLER FORENSICS // YUKTHI 2026 SPECIFICATION COMPLIANT</span>
        <span>STATUS: OPERATIONAL // TELEMETRY REPLAY SYNCHRONIZED</span>
    </div>
    """,
    unsafe_allow_html=True
)

