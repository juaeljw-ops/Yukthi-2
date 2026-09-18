import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
from dashboard.data_loader import get_context_variables


def get_status_style(status_str: str) -> Dict[str, str]:
    st_upper = str(status_str).upper()
    if st_upper in ["PRIORITY", "CRITICAL"]:
        return {
            "tag": "[CRITICAL]",
            "label": "CRITICAL",
            "color": "#F43F5E",
            "bg": "rgba(244, 63, 94, 0.10)",
            "border": "#7F1D1D"
        }
    elif st_upper in ["INVESTIGATE", "HIGH"]:
        return {
            "tag": "[INVESTIGATE]",
            "label": "INVESTIGATE",
            "color": "#EF4444",
            "bg": "rgba(239, 68, 68, 0.10)",
            "border": "#991B1B"
        }
    elif st_upper in ["WATCH", "WARNING", "MEDIUM"]:
        return {
            "tag": "[WATCH]",
            "label": "WATCH",
            "color": "#E5B842",
            "bg": "rgba(229, 184, 66, 0.10)",
            "border": "#854D0E"
        }
    elif st_upper in ["NORMAL", "NOMINAL"]:
        return {
            "tag": "[NOMINAL]",
            "label": "NOMINAL",
            "color": "#10B981",
            "bg": "rgba(16, 185, 129, 0.10)",
            "border": "#064E3B"
        }
    else:
        return {
            "tag": f"[{st_upper}]",
            "label": st_upper,
            "color": "#94A3B8",
            "bg": "rgba(148, 163, 184, 0.08)",
            "border": "#334155"
        }


def inject_custom_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            letter-spacing: -0.01em;
        }

        h1, h2, h3, .cinzel-font {
            font-family: 'Cinzel', serif !important;
            letter-spacing: 0.05em;
        }

        /* Completely remove sidebar and expand controls */
        [data-testid="stSidebar"], section[data-testid="stSidebar"], [data-testid="collapsedControl"] {
            display: none !important;
        }

        .stApp {
            background-color: #080A0F;
            color: #FAF6EE;
        }

        .telemetry-mono {
            font-family: 'JetBrains Mono', 'SF Mono', Consolas, monospace;
            font-feature-settings: "tnum" 1;
        }

        .metric-panel {
            background: #0D111A;
            border: 1px solid rgba(212, 175, 55, 0.2);
            border-radius: 4px;
            padding: 14px 16px;
            margin-bottom: 10px;
        }

        .metric-panel-header {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 0.72rem;
            font-weight: 600;
            color: #8E8A82;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 6px;
        }

        .metric-panel-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.65rem;
            font-weight: 700;
            color: #FAF6EE;
            font-feature-settings: "tnum" 1;
            line-height: 1.15;
        }

        .metric-panel-sub {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 0.74rem;
            color: #8E8A82;
            margin-top: 6px;
        }

        .asset-card {
            background: #0D111A;
            border: 1px solid rgba(212, 175, 55, 0.22);
            border-radius: 4px;
            padding: 16px;
            margin-bottom: 10px;
            transition: all 0.2s ease;
        }

        .asset-card-active {
            background: #111726 !important;
            border: 2px solid #D4AF37 !important;
            box-shadow: 0 0 18px rgba(212, 175, 55, 0.22) !important;
        }

        .status-tag {
            display: inline-block;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.70rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 3px;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            border-bottom: 1px solid rgba(212, 175, 55, 0.2);
            padding-bottom: 6px;
            margin-bottom: 14px;
        }

        .section-title {
            font-family: 'Cinzel', serif;
            font-size: 0.96rem;
            font-weight: 700;
            color: #FAF6EE;
            letter-spacing: 0.06em;
        }

        .section-sub {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 0.72rem;
            color: #8E8A82;
            letter-spacing: 0.04em;
        }

        /* Streamlit Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
            border-bottom: 1px solid rgba(212, 175, 55, 0.25);
            background: transparent;
        }

        .stTabs [data-baseweb="tab"] {
            font-family: 'Cinzel', serif;
            font-size: 0.85rem;
            font-weight: 600;
            color: #8E8A82;
            border-radius: 4px 4px 0 0;
            padding: 10px 20px;
            background: transparent;
            border: 1px solid transparent;
            letter-spacing: 0.05em;
        }

        .stTabs [aria-selected="true"] {
            color: #D4AF37 !important;
            border: 1px solid rgba(212, 175, 55, 0.3) !important;
            border-bottom: 2px solid #D4AF37 !important;
            background: #0D111A !important;
        }

        /* Button Styling */
        .stButton > button {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 0.78rem;
            font-weight: 600;
            background: #0D111A;
            color: #FAF6EE;
            border: 1px solid rgba(212, 175, 55, 0.25);
            border-radius: 3px;
            padding: 8px 16px;
            letter-spacing: 0.04em;
            transition: all 0.15s ease;
        }

        .stButton > button:hover {
            border-color: #D4AF37;
            color: #D4AF37;
            background: #141B29;
        }

        /* Primary Button (Active state) */
        .stButton > button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] {
            background: #D4AF37 !important;
            color: #080A0F !important;
            border: 1px solid #D4AF37 !important;
            font-weight: 700 !important;
        }

        div[data-baseweb="select"] > div {
            background-color: #0D111A !important;
            border: 1px solid rgba(212, 175, 55, 0.25) !important;
            border-radius: 3px !important;
            color: #FAF6EE !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 0.82rem !important;
        }

        div[data-baseweb="input"] input {
            background-color: #0D111A !important;
            border-radius: 3px !important;
            color: #FAF6EE !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 0.82rem !important;
        }

        .telemetry-row {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #161D2B;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.76rem;
        }

        .telemetry-row-label {
            color: #8E8A82;
        }

        .telemetry-row-val {
            color: #FAF6EE;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_chiller_selector_cards(fleet_stats: List[Dict[str, Any]], active_chiller: str) -> str:
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px; border-bottom: 1px solid rgba(212, 175, 55, 0.2); padding-bottom: 6px;">
            <span style="font-family: 'Cinzel', serif; font-size: 0.95rem; font-weight: 700; color: #FAF6EE; letter-spacing: 0.08em;">
                FLEET ASSET DIRECTORY
            </span>
            <span style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.74rem; color: #8E8A82;">
                CLICK ASSET CARD TO REVEAL TELEMETRY & DIAGNOSTICS
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    stats_map = {item["equipment"]: item for item in fleet_stats}
    chiller_ids = sorted(list(stats_map.keys()))
    
    selected = active_chiller
    cols = st.columns(len(chiller_ids) if chiller_ids else 3)
    
    for idx, cid in enumerate(chiller_ids):
        item = stats_map.get(cid, {})
        is_active = (cid == active_chiller)
        status = item.get("status", "UNASSESSED")
        style = get_status_style(status)
        readings = item.get("readings", 0)
        avg_e = item.get("avg_energy", 0.0)
        max_e = item.get("max_energy", 0.0)
        dev = item.get("current_deviation_pct")

        dev_str = f"+{dev:.1f}%" if dev is not None else "NOMINAL"
        dev_color = style["color"] if (dev is not None and dev > 5.0) else "#10B981"

        card_class = "asset-card asset-card-active" if is_active else "asset-card"
        border_top = "border-top: 3px solid #D4AF37;" if is_active else f"border-top: 3px solid {style['color']};"

        with cols[idx]:
            indicator_html = (
                '<div style="font-family: \'Plus Jakarta Sans\', sans-serif; font-size: 0.70rem; font-weight: 700; color: #D4AF37; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 4px;">● CURRENTLY ACTIVE</div>'
                if is_active else
                '<div style="font-family: \'Plus Jakarta Sans\', sans-serif; font-size: 0.70rem; color: #8E8A82; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px;">MONITORED CHILLER</div>'
            )

            st.markdown(
                f"""
                <div class="{card_class}" style="{border_top} margin-bottom: 8px;">
                    {indicator_html}
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="font-family: 'Cinzel', serif; font-size: 1.30rem; font-weight: 700; color: {'#D4AF37' if is_active else '#FAF6EE'};">
                            {cid}
                        </span>
                        <span class="status-tag" style="color: {style['color']}; background: {style['bg']}; border: 1px solid {style['border']};">
                            {style['tag']}
                        </span>
                    </div>
                    <div class="telemetry-row">
                        <span class="telemetry-row-label">READING COUNT</span>
                        <span class="telemetry-row-val">{readings:,}</span>
                    </div>
                    <div class="telemetry-row">
                        <span class="telemetry-row-label">MEAN POWER</span>
                        <span class="telemetry-row-val" style="color: #D4AF37;">{avg_e:.1f} kWh</span>
                    </div>
                    <div class="telemetry-row">
                        <span class="telemetry-row-label">PEAK DEMAND</span>
                        <span class="telemetry-row-val">{max_e:.1f} kWh</span>
                    </div>
                    <div class="telemetry-row" style="border-bottom: none;">
                        <span class="telemetry-row-label">EXCEEDANCE</span>
                        <span class="telemetry-row-val" style="color: {dev_color};">{dev_str}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            btn_label = f"✓ {cid} ACTIVE" if is_active else f"INSPECT {cid}"
            if st.button(btn_label, key=f"btn_select_{cid}", use_container_width=True, type="primary" if is_active else "secondary"):
                selected = cid
                st.session_state["selected_chiller"] = cid
                st.rerun()

    return selected


def render_fleet_metrics_summary(metrics: Dict[str, Any]):
    st.markdown(
        """
        <div class="section-header">
            <span class="section-title">FLEET TELEMETRY & SYSTEM OVERVIEW</span>
            <span class="section-sub">SOURCE: development_dataset.csv // SAMPLING: 30-MIN</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="metric-panel">
                <div class="metric-panel-header">MONITORED ASSETS</div>
                <div class="metric-panel-val" style="color: #D4AF37;">{metrics['total_chillers']}</div>
                <div class="metric-panel-sub">Active Telemetry Units</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-panel">
                <div class="metric-panel-header">DATASET OBSERVATIONS</div>
                <div class="metric-panel-val">{metrics['total_readings']:,}</div>
                <div class="metric-panel-sub">Half-Hourly Records</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f"""
            <div class="metric-panel">
                <div class="metric-panel-header">OBSERVATION WINDOW</div>
                <div class="metric-panel-val" style="font-size: 1.15rem; margin-top: 4px; color: #FAF6EE;">
                    {metrics['date_min'][:10]}
                </div>
                <div class="metric-panel-sub">TO {metrics['date_max'][:10]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c4:
        has_ml = any(c.get("has_ml", False) for c in metrics.get("chiller_stats", []))
        status_color = "#10B981" if has_ml else "#E5B842"
        status_text = "[ACTIVE: MODEL CALIBRATED]" if has_ml else "[STANDBY: PENDING ML]"
        st.markdown(
            f"""
            <div class="metric-panel">
                <div class="metric-panel-header">FORENSIC ENGINE STATUS</div>
                <div class="metric-panel-val" style="font-size: 1.05rem; margin-top: 4px; color: {status_color};">
                    {status_text}
                </div>
                <div class="metric-panel-sub">Residual Baseline Ingestion</div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_chiller_fleet_table(fleet_stats: List[Dict[str, Any]]):
    st.markdown(
        """
        <div class="section-header">
            <span class="section-title">ASSET STATUS DIRECTORY</span>
            <span class="section-sub">CHILLER OPERATIONAL STATUS MATRIX</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    search_query = st.text_input("FILTER ASSET ID:", "", placeholder="e.g. CHILLER-01").strip().upper()
    
    filtered = fleet_stats
    if search_query:
        filtered = [c for c in fleet_stats if search_query in c["equipment"].upper()]

    if not filtered:
        st.markdown(
            """
            <div style="padding: 16px; background: #0D111A; border: 1px solid rgba(212, 175, 55, 0.2); font-size: 0.80rem; color: #8E8A82;">
                [INFO] No equipment matched the search query.
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    cols = st.columns(len(filtered) if len(filtered) <= 3 else 3)
    for idx, item in enumerate(filtered):
        cid = item["equipment"]
        readings = item["readings"]
        avg_e = item["avg_energy"]
        max_e = item["max_energy"]
        status = item.get("status", "UNASSESSED")
        style = get_status_style(status)
        dev = item.get("current_deviation_pct")

        dev_str = f"+{dev:.1f}%" if dev is not None else "NOMINAL"
        dev_color = style["color"] if (dev is not None and dev > 5.0) else "#10B981"

        with cols[idx % len(cols)]:
            st.markdown(
                f"""
                <div class="asset-card" style="border-left: 3px solid {style['color']};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <span style="font-family: 'Cinzel', serif; font-size: 1.25rem; font-weight: 700; color: #FAF6EE;">
                            {cid}
                        </span>
                        <span class="status-tag" style="color: {style['color']}; background: {style['bg']}; border: 1px solid {style['border']};">
                            {style['tag']}
                        </span>
                    </div>
                    <div class="telemetry-row">
                        <span class="telemetry-row-label">READING COUNT</span>
                        <span class="telemetry-row-val">{readings:,}</span>
                    </div>
                    <div class="telemetry-row">
                        <span class="telemetry-row-label">MEAN POWER</span>
                        <span class="telemetry-row-val" style="color: #D4AF37;">{avg_e:.1f} kWh</span>
                    </div>
                    <div class="telemetry-row">
                        <span class="telemetry-row-label">PEAK DEMAND</span>
                        <span class="telemetry-row-val">{max_e:.1f} kWh</span>
                    </div>
                    <div class="telemetry-row" style="border-bottom: none;">
                        <span class="telemetry-row-label">EXCEEDANCE DELTA</span>
                        <span class="telemetry-row-val" style="color: {dev_color};">{dev_str}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


def render_actual_energy_chart(df_chiller: pd.DataFrame, expected_series: Optional[pd.Series] = None, chiller_id: str = ""):
    st.markdown(
        f"""
        <div class="section-header">
            <span class="section-title">POWER DEMAND: OBSERVED vs EXPECTED BASELINE — {chiller_id}</span>
            <span class="section-sub">SAMPLING: 30-MINUTES // ENERGY UNIT: kWh</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if df_chiller.empty:
        st.info(f"[INFO] No time-series records found for {chiller_id}.")
        return

    energy_col = "Chiller Energy Consumption (kWh)"
    if energy_col not in df_chiller.columns:
        st.error(f"[ERROR] Required column '{energy_col}' missing from telemetry.")
        return

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_chiller["timestamp"],
            y=df_chiller[energy_col],
            name="OBSERVED DEMAND",
            line=dict(color="#FAF6EE", width=1.5),
            hovertemplate="<b>TIMESTAMP:</b> %{x}<br><b>OBSERVED:</b> %{y:.1f} kWh<extra></extra>"
        )
    )

    if expected_series is not None and not expected_series.empty:
        fig.add_trace(
            go.Scatter(
                x=df_chiller["timestamp"],
                y=expected_series.reindex(df_chiller["timestamp"]).values,
                name="MODEL BASELINE",
                line=dict(color="#D4AF37", width=1.5, dash="dash"),
                hovertemplate="<b>TIMESTAMP:</b> %{x}<br><b>BASELINE:</b> %{y:.1f} kWh<extra></extra>"
            )
        )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0D111A",
        plot_bgcolor="#080A0F",
        margin=dict(l=40, r=30, t=25, b=35),
        height=380,
        hovermode="x unified",
        font=dict(family="Plus Jakarta Sans, sans-serif", size=11, color="#8E8A82"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        xaxis=dict(title="", gridcolor="#161D2B", linecolor="rgba(212, 175, 55, 0.2)", showgrid=True, zeroline=False),
        yaxis=dict(title="POWER CONSUMPTION (kWh)", gridcolor="#161D2B", linecolor="rgba(212, 175, 55, 0.2)", showgrid=True, zeroline=False)
    )

    st.plotly_chart(fig, use_container_width=True)


def render_contextual_operating_conditions(df_chiller: pd.DataFrame):
    st.markdown(
        """
        <div class="section-header">
            <span class="section-title">CONTEXTUAL SENSOR TELEMETRY</span>
            <span class="section-sub">MULTIVARIATE THERMODYNAMIC CONTEXT EXCLUDING TARGET ENERGY</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    context_cols = get_context_variables(df_chiller)
    if not context_cols:
        st.info("[INFO] No contextual sensors available in telemetry.")
        return

    cols = st.columns(min(len(context_cols), 4))
    for idx, col_name in enumerate(context_cols[:4]):
        mean_val = df_chiller[col_name].mean()
        min_val = df_chiller[col_name].min()
        max_val = df_chiller[col_name].max()
        
        with cols[idx % len(cols)]:
            st.markdown(
                f"""
                <div class="metric-panel">
                    <div class="metric-panel-header">{col_name}</div>
                    <div class="metric-panel-val" style="color: #D4AF37; font-size: 1.35rem;">
                        {mean_val:.1f}
                    </div>
                    <div class="metric-panel-sub">
                        MIN: {min_val:.1f} | MAX: {max_val:.1f}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        """
        <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.74rem; font-weight: 600; color: #8E8A82; margin-top: 10px; margin-bottom: 4px; text-transform: uppercase;">
            INTERACTIVE CONTEXT PARAMETER TRACE
        </div>
        """,
        unsafe_allow_html=True
    )
    
    selected_var = st.selectbox(
        "Select context variable to plot against timestamp:",
        options=context_cols,
        index=0,
        label_visibility="collapsed"
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_chiller["timestamp"],
            y=df_chiller[selected_var],
            name=selected_var.upper(),
            line=dict(color="#D4AF37", width=1.5),
            hovertemplate=f"<b>TIMESTAMP:</b> %{{x}}<br><b>{selected_var}:</b> %{{y:.2f}}<extra></extra>"
        )
    )
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0D111A",
        plot_bgcolor="#080A0F",
        margin=dict(l=40, r=30, t=20, b=35),
        height=280,
        font=dict(family="Plus Jakarta Sans, sans-serif", size=11, color="#8E8A82"),
        xaxis=dict(title="", gridcolor="#161D2B", linecolor="rgba(212, 175, 55, 0.2)", showgrid=True),
        yaxis=dict(title=selected_var.upper(), gridcolor="#161D2B", linecolor="rgba(212, 175, 55, 0.2)", showgrid=True)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_contextual_deviation_section(anomaly_data: Optional[Dict[str, Any]]):
    st.markdown(
        """
        <div class="section-header">
            <span class="section-title">EMPIRICAL DEVIATION ANALYSIS</span>
            <span class="section-sub">ACTUAL vs PREDICTED ENERGY RESIDUAL</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if not anomaly_data or "expected_energy" not in anomaly_data:
        st.markdown(
            """
            <div style="padding: 16px; background: #0D111A; border: 1px solid rgba(212, 175, 55, 0.2); font-size: 0.80rem; color: #8E8A82;">
                [INFO] Baseline model output pending ML pipeline calibration.
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    actual = anomaly_data.get("actual_energy", 0.0)
    expected = anomaly_data.get("expected_energy", 0.0)
    dev_pct = anomaly_data.get("deviation_pct", 0.0)
    residual = actual - expected

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="metric-panel">
                <div class="metric-panel-header">ACTUAL DEMAND (OBSERVED)</div>
                <div class="metric-panel-val">{actual:.1f} <span style="font-size: 0.9rem; color: #8E8A82;">kWh</span></div>
                <div class="metric-panel-sub">PREVAILING READING</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-panel">
                <div class="metric-panel-header">MODEL BASELINE (EXPECTED)</div>
                <div class="metric-panel-val" style="color: #D4AF37;">{expected:.1f} <span style="font-size: 0.9rem; color: #8E8A82;">kWh</span></div>
                <div class="metric-panel-sub">EMPIRICAL TARGET</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f"""
            <div class="metric-panel">
                <div class="metric-panel-header">CONTEXTUAL EXCEEDANCE</div>
                <div class="metric-panel-val" style="color: #EF4444;">+{dev_pct:.1f}%</div>
                <div class="metric-panel-sub">DELTA: +{residual:.1f} kWh</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        f"""
        <div style="background: #0D111A; border: 1px solid rgba(212, 175, 55, 0.25); border-left: 3px solid #D4AF37; padding: 12px 16px; margin-top: 10px; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.84rem; color: #FAF6EE; line-height: 1.6;">
            <div style="font-family: 'Cinzel', serif; font-weight: 700; color: #D4AF37; margin-bottom: 4px;">DIAGNOSTIC TELEMETRY LOG</div>
            <div style="color: #EDE8DE;">
                Observed energy demand is <strong style="color: #D4AF37;">+{dev_pct:.1f}% higher than expected</strong> for the measured thermodynamic operating conditions (ambient wet-bulb, water flow rates, and building RT load).
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_persistence_analysis(anomaly_data: Optional[Dict[str, Any]]):
    st.markdown(
        """
        <div class="section-header">
            <span class="section-title">SEQUENCE PERSISTENCE & SEVERITY</span>
            <span class="section-sub">TEMPORAL CONTINUITY FILTERING (WINDOW >= 3 PERIODS)</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not anomaly_data:
        st.markdown(
            """
            <div style="padding: 16px; background: #0D111A; border: 1px solid rgba(212, 175, 55, 0.2); font-size: 0.80rem; color: #8E8A82;">
                [INFO] Persistence evaluation pending ML anomaly results.
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    consec = anomaly_data.get("consecutive_abnormal_readings", 0)
    status = anomaly_data.get("severity", "NORMAL")
    trend = anomaly_data.get("trend", "STABLE")
    style = get_status_style(status)
    duration_min = consec * 30

    st.markdown(
        f"""
        <div class="asset-card" style="margin-bottom: 0;">
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px;">
                <div>
                    <div class="metric-panel-header">SEVERITY CLASSIFICATION</div>
                    <span class="status-tag" style="color: {style['color']}; background: {style['bg']}; border: 1px solid {style['border']}; margin-top: 4px;">
                        {style['tag']}
                    </span>
                </div>
                <div>
                    <div class="metric-panel-header">PERSISTENT SEQUENCE</div>
                    <div class="telemetry-mono" style="font-size: 1.25rem; font-weight: 700; color: #FAF6EE; margin-top: 2px;">
                        {consec} <span style="font-size: 0.80rem; color: #8E8A82;">READINGS ({duration_min} MIN)</span>
                    </div>
                </div>
                <div>
                    <div class="metric-panel-header">DEVIATION TRAJECTORY</div>
                    <div class="telemetry-mono" style="font-size: 1.25rem; font-weight: 700; color: #D4AF37; margin-top: 2px;">
                        {trend}
                    </div>
                </div>
            </div>
            <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(212, 175, 55, 0.15); font-size: 0.74rem; color: #8E8A82;">
                FILTER CRITERIA: Transient single-period spikes filtered. Persistent state confirmed after >=3 consecutive periods beyond 2.5 sigma threshold.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_investigation_report(anomaly_data: Optional[Dict[str, Any]]):
    st.markdown(
        """
        <div class="section-header">
            <span class="section-title">AUTOMATED ROOT-CAUSE ATTRIBUTION & ACTIONS</span>
            <span class="section-sub">DECISION SUPPORT & CORRECTIVE ACTION PROCEDURES</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not anomaly_data:
        st.markdown(
            """
            <div style="padding: 16px; background: #0D111A; border: 1px solid rgba(212, 175, 55, 0.2); font-size: 0.80rem; color: #8E8A82;">
                [INFO] Investigation report will display once ML anomaly evaluation is generated.
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    summary = anomaly_data.get("investigation_summary", "Review contextual parameter shifts around anomaly window.")
    recommendations = anomaly_data.get("recommended_investigation", [])
    context_changes = anomaly_data.get("context_changes", [])

    st.markdown(
        f"""
        <div class="asset-card">
            <div style="font-family: 'Cinzel', serif; font-size: 0.88rem; color: #D4AF37; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;">
                ATTRIBUTION SUMMARY
            </div>
            <div style="font-size: 0.88rem; color: #EDE8DE; line-height: 1.6; margin-bottom: 14px;">
                {summary}
            </div>
        """,
        unsafe_allow_html=True
    )

    if context_changes:
        st.markdown(
            """
            <div style="font-size: 0.72rem; font-weight: 600; color: #8E8A82; text-transform: uppercase; margin-bottom: 8px;">
                OBSERVED CONTEXTUAL PARAMETER DRIFT
            </div>
            """,
            unsafe_allow_html=True
        )
        for cc in context_changes:
            var_name = cc.get("variable", "Context Sensor")
            pct = cc.get("change_pct", 0.0)
            direction = cc.get("direction", "SHIFT")
            st.markdown(
                f"""
                <div class="telemetry-row" style="padding: 4px 0;">
                    <span class="telemetry-row-label">{var_name}</span>
                    <span class="telemetry-row-val" style="color: {'#EF4444' if abs(pct) > 10 else '#D4AF37'};">
                        {direction} ({pct:+.1f}%)
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        """
        <div style="font-family: 'Cinzel', serif; font-size: 0.85rem; font-weight: 700; color: #FAF6EE; text-transform: uppercase; margin-top: 14px; margin-bottom: 8px;">
            RECOMMENDED ENGINEERING ACTIONS
        </div>
        """,
        unsafe_allow_html=True
    )

    for idx, rec in enumerate(recommendations, 1):
        st.markdown(
            f"""
            <div style="background: #080A0F; border: 1px solid rgba(212, 175, 55, 0.2); border-left: 3px solid #D4AF37; padding: 10px 14px; margin-bottom: 8px; font-size: 0.82rem; color: #EDE8DE; display: flex; gap: 10px;">
                <span style="color: #D4AF37; font-weight: 700;">[ACTION {idx:02d}]</span>
                <span>{rec}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_anomaly_replay_view(df_chiller: pd.DataFrame, chiller_id: str):
    st.markdown(
        f"""
        <div class="section-header">
            <span class="section-title">CHRONOLOGICAL REPLAY & INCIDENT CLASSIFIER — {chiller_id}</span>
            <span class="section-sub">SAMPLING: 30-MINUTES // RESIDUAL EVALUATION ENGINE</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if df_chiller.empty:
        st.info(f"[INFO] No time-series records available for {chiller_id}.")
        return

    energy_col = "Chiller Energy Consumption (kWh)"
    total_len = len(df_chiller)
    timestamps = df_chiller["timestamp"].tolist()

    has_severity = "severity" in df_chiller.columns
    if has_severity:
        is_anomaly_mask = (df_chiller["severity"] != "NORMAL") | (df_chiller.get("is_abnormal", False) == True)
    else:
        is_anomaly_mask = pd.Series([False] * total_len)

    anomaly_indices = df_chiller.index[is_anomaly_mask].tolist()
    total_anomalies = len(anomaly_indices)

    # Master index state for this chiller
    cur_idx_key = f"cur_obs_idx_{chiller_id}"
    if cur_idx_key not in st.session_state:
        st.session_state[cur_idx_key] = anomaly_indices[0] if anomaly_indices else 0
    st.session_state[cur_idx_key] = min(max(0, st.session_state[cur_idx_key]), total_len - 1)

    # Anomaly position pointer
    anom_pos_key = f"anom_pos_{chiller_id}"
    if anom_pos_key not in st.session_state:
        st.session_state[anom_pos_key] = 0
    if total_anomalies > 0:
        st.session_state[anom_pos_key] = min(max(0, st.session_state[anom_pos_key]), total_anomalies - 1)

    mode_options = ["ALL OBSERVATIONS", "ANOMALOUS EVENTS ONLY"] if total_anomalies > 0 else ["ALL OBSERVATIONS"]
    
    col_mode, col_ctrl = st.columns([1.6, 3.4])
    with col_mode:
        selected_mode = st.radio(
            "Navigation Scope:",
            options=mode_options,
            horizontal=True,
            key=f"mode_{chiller_id}",
            label_visibility="collapsed"
        )

    if selected_mode == "ANOMALOUS EVENTS ONLY" and total_anomalies > 0:
        with col_ctrl:
            c_prev, c_stat, c_next = st.columns([1, 2, 1])
            with c_prev:
                if st.button("< PREV INCIDENT", key=f"btn_prev_{chiller_id}", use_container_width=True):
                    st.session_state[anom_pos_key] = max(0, st.session_state[anom_pos_key] - 1)
                    st.session_state[cur_idx_key] = anomaly_indices[st.session_state[anom_pos_key]]
                    st.rerun()
            with c_next:
                if st.button("NEXT INCIDENT >", key=f"btn_next_{chiller_id}", use_container_width=True):
                    st.session_state[anom_pos_key] = min(total_anomalies - 1, st.session_state[anom_pos_key] + 1)
                    st.session_state[cur_idx_key] = anomaly_indices[st.session_state[anom_pos_key]]
                    st.rerun()
            with c_stat:
                st.markdown(
                    f"""
                    <div style="text-align: center; padding-top: 6px; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #D4AF37; font-weight: 700;">
                        INCIDENT {st.session_state[anom_pos_key] + 1} OF {total_anomalies}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        def format_anomaly(i: int) -> str:
            idx = anomaly_indices[i]
            r = df_chiller.iloc[idx]
            ts = str(r.get("timestamp", ""))
            sev = str(r.get("severity", "ANOMALY"))
            dev = float(r.get("deviation_pct", 0.0)) if pd.notna(r.get("deviation_pct")) else 0.0
            z = float(r.get("residual_zscore", 0.0)) if pd.notna(r.get("residual_zscore")) else 0.0
            return f"INCIDENT #{i+1:03d} // {ts} // [{sev}] // DEV: {dev:+.1f}% // Z: {z:+.2f}σ"

        selected_incident_pos = st.selectbox(
            "Jump to Anomaly Incident:",
            options=list(range(total_anomalies)),
            format_func=format_anomaly,
            index=st.session_state[anom_pos_key],
            key=f"anom_select_{chiller_id}"
        )
        if selected_incident_pos != st.session_state[anom_pos_key]:
            st.session_state[anom_pos_key] = selected_incident_pos
            st.session_state[cur_idx_key] = anomaly_indices[selected_incident_pos]
            st.rerun()

        selected_idx = anomaly_indices[st.session_state[anom_pos_key]]

    else:
        # ALL OBSERVATIONS MODE
        with col_ctrl:
            c_day_prev, c_prev, c_stat, c_next, c_day_next = st.columns([1, 1, 2.2, 1, 1])
            with c_day_prev:
                if st.button("<< -1D", key=f"btn_dprev_{chiller_id}", use_container_width=True, help="Jump back 24 hours (48 intervals)"):
                    st.session_state[cur_idx_key] = max(0, st.session_state[cur_idx_key] - 48)
                    st.rerun()
            with c_prev:
                if st.button("< PREV", key=f"btn_all_prev_{chiller_id}", use_container_width=True, help="Previous 30-min reading"):
                    st.session_state[cur_idx_key] = max(0, st.session_state[cur_idx_key] - 1)
                    st.rerun()
            with c_next:
                if st.button("NEXT >", key=f"btn_all_next_{chiller_id}", use_container_width=True, help="Next 30-min reading"):
                    st.session_state[cur_idx_key] = min(total_len - 1, st.session_state[cur_idx_key] + 1)
                    st.rerun()
            with c_day_next:
                if st.button("+1D >>", key=f"btn_dnext_{chiller_id}", use_container_width=True, help="Jump forward 24 hours (48 intervals)"):
                    st.session_state[cur_idx_key] = min(total_len - 1, st.session_state[cur_idx_key] + 48)
                    st.rerun()
            with c_stat:
                curr_ts_disp = timestamps[st.session_state[cur_idx_key]]
                st.markdown(
                    f"""
                    <div style="text-align: center; padding-top: 3px; font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; color: #D4AF37; font-weight: 700;">
                        READING {st.session_state[cur_idx_key] + 1:,} OF {total_len:,}<br/>
                        <span style="font-size: 0.68rem; color: #8E8A82;">{curr_ts_disp}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        def format_all_reading(i: int) -> str:
            ts = timestamps[i]
            r = df_chiller.iloc[i]
            act = float(r.get(energy_col, 0.0))
            sev = str(r.get("severity", "NORMAL"))
            dev = float(r.get("deviation_pct", 0.0)) if pd.notna(r.get("deviation_pct")) else 0.0
            return f"#{i+1:04d} // {ts} // {act:.1f} kWh // [{sev}] ({dev:+.1f}%)"

        c_jump, c_slider = st.columns([1.8, 2.2])
        with c_jump:
            selected_all_ts = st.selectbox(
                "Select / Search Observation Event Timestamp:",
                options=list(range(total_len)),
                format_func=format_all_reading,
                index=st.session_state[cur_idx_key],
                key=f"sel_all_ts_{chiller_id}"
            )
            if selected_all_ts != st.session_state[cur_idx_key]:
                st.session_state[cur_idx_key] = selected_all_ts
                st.rerun()

        with c_slider:
            current_reading_ts = timestamps[st.session_state[cur_idx_key]]
            slider_pos = st.slider(
                f"Timeline Scrubber ({current_reading_ts}):",
                min_value=0,
                max_value=total_len - 1,
                value=st.session_state[cur_idx_key],
                key=f"slider_all_{chiller_id}"
            )
            if slider_pos != st.session_state[cur_idx_key]:
                st.session_state[cur_idx_key] = slider_pos
                st.rerun()

        selected_idx = st.session_state[cur_idx_key]

    row = df_chiller.iloc[selected_idx]
    current_status = str(row.get("severity", "NORMAL")).upper()
    is_abnormal = bool(row.get("is_abnormal", current_status != "NORMAL"))
    dev_pct = float(row.get("deviation_pct", 0.0)) if pd.notna(row.get("deviation_pct")) else 0.0
    actual_e = float(row.get(energy_col, 0.0))
    expected_e = float(row.get("expected_energy", actual_e)) if pd.notna(row.get("expected_energy")) else actual_e
    z_score = float(row.get("residual_zscore", 0.0)) if pd.notna(row.get("residual_zscore")) else 0.0
    consec = int(row.get("consecutive_abnormal_readings", 0)) if pd.notna(row.get("consecutive_abnormal_readings")) else 0
    event_id = row.get("event_id", None)
    residual = actual_e - expected_e

    case_badge = f'<span style="font-family: monospace; font-size: 0.76rem; color: #D4AF37; font-weight: 600;">CASE ID: {event_id}</span>' if pd.notna(event_id) else ""

    if is_abnormal or current_status in ["WATCH", "INVESTIGATE", "PRIORITY"]:
        border_color = "#EF4444"
        bg_color = "rgba(239, 68, 68, 0.08)"
        tag_bg = "#EF4444"
        tag_text = f"[ANOMALOUS EVENT: {current_status}]"
        desc_text = (
            f"Power demand exceeds statistical upper bound under prevailing operating conditions. "
            f"Residual z-score: <strong>+{z_score:.2f}σ</strong> (threshold ≥ 2.50σ). "
            f"Consumption is <strong>+{dev_pct:.1f}% (+{residual:.1f} kWh)</strong> above calibrated baseline. "
            f"Persistence sequence: <strong>{consec} consecutive reading(s)</strong> ({consec * 30} minutes)."
        )
    else:
        border_color = "#10B981"
        bg_color = "rgba(16, 185, 129, 0.08)"
        tag_bg = "#10B981"
        tag_text = "[NOMINAL OPERATING STATE]"
        desc_text = (
            f"Observed energy consumption complies with calibrated thermodynamic baseline. "
            f"Residual z-score is <strong>{z_score:+.2f}σ</strong> (within normal ±2.50σ tolerance). "
            f"Contextual deviation: <strong>{dev_pct:+.1f}%</strong>."
        )

    st.markdown(
        f"""
        <div style="background: {bg_color}; border: 1px solid {border_color}; border-left: 4px solid {border_color}; border-radius: 4px; padding: 16px 20px; margin-top: 14px; margin-bottom: 18px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="background: {tag_bg}; color: #FFFFFF; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 0.78rem; padding: 3px 10px; border-radius: 2px; letter-spacing: 0.06em;">
                        {tag_text}
                    </span>
                    {case_badge}
                </div>
                <div class="telemetry-mono" style="font-size: 0.88rem; font-weight: 600; color: #FAF6EE;">
                    INDEX #{selected_idx + 1:,} &bull; {row['timestamp']}
                </div>
            </div>
            <div style="margin-top: 10px; font-size: 0.84rem; color: #EDE8DE; line-height: 1.5;">
                {desc_text}
            </div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 14px; padding-top: 12px; border-top: 1px solid {border_color}33; font-family: 'JetBrains Mono', monospace;">
                <div>
                    <div style="font-size: 0.68rem; color: #8E8A82;">OBSERVED DEMAND</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: #FAF6EE;">{actual_e:.1f} <span style="font-size: 0.75rem; color: #8E8A82;">kWh</span></div>
                </div>
                <div>
                    <div style="font-size: 0.68rem; color: #8E8A82;">MODEL BASELINE</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: #D4AF37;">{expected_e:.1f} <span style="font-size: 0.75rem; color: #8E8A82;">kWh</span></div>
                </div>
                <div>
                    <div style="font-size: 0.68rem; color: #8E8A82;">EXCEEDANCE DELTA</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: {border_color};">{dev_pct:+.1f}% <span style="font-size: 0.75rem; color: #8E8A82;">({residual:+.1f} kWh)</span></div>
                </div>
                <div>
                    <div style="font-size: 0.68rem; color: #8E8A82;">RESIDUAL Z-SCORE</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: {border_color};">{z_score:+.2f}σ</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-header">
            <span class="section-title">INCIDENT HIGH-RESOLUTION FOCUS TRACE</span>
            <span class="section-sub">LOCAL WINDOW: +/-16 PERIODS (16-HOUR APERTURE)</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    w_start = max(0, selected_idx - 16)
    w_end = min(total_len, selected_idx + 17)
    focus_df = df_chiller.iloc[w_start:w_end].copy()

    fig_focus = go.Figure()

    if "expected_energy" in focus_df.columns:
        fig_focus.add_trace(
            go.Scatter(
                x=focus_df["timestamp"],
                y=focus_df["expected_energy"],
                name="MODEL BASELINE",
                line=dict(color="#D4AF37", width=1.5, dash="dash"),
                hovertemplate="<b>BASELINE:</b> %{y:.1f} kWh<extra></extra>"
            )
        )

    # Underlying continuous observed line
    fig_focus.add_trace(
        go.Scatter(
            x=focus_df["timestamp"],
            y=focus_df[energy_col],
            mode="lines",
            name="OBSERVED DEMAND",
            line=dict(color="#475569", width=1),
            hoverinfo="skip"
        )
    )

    focus_normal = focus_df[~focus_df.index.isin(anomaly_indices)]
    if not focus_normal.empty:
        fig_focus.add_trace(
            go.Scatter(
                x=focus_normal["timestamp"],
                y=focus_normal[energy_col],
                mode="markers",
                name="NOMINAL STATE",
                marker=dict(size=6, color="#10B981"),
                hovertemplate="<b>NOMINAL</b><br>TIME: %{x}<br>DEMAND: %{y:.1f} kWh<extra></extra>"
            )
        )

    focus_anom = focus_df[focus_df.index.isin(anomaly_indices)]
    if not focus_anom.empty:
        fig_focus.add_trace(
            go.Scatter(
                x=focus_anom["timestamp"],
                y=focus_anom[energy_col],
                mode="markers",
                name="ANOMALOUS EVENT",
                marker=dict(size=9, color="#EF4444", symbol="circle", line=dict(color="#FFFFFF", width=1)),
                hovertemplate="<b>ANOMALOUS</b><br>TIME: %{x}<br>DEMAND: %{y:.1f} kWh<extra></extra>"
            )
        )

    current_ts = str(row["timestamp"])
    fig_focus.add_vline(
        x=current_ts,
        line_width=1.5,
        line_dash="dot",
        line_color="#D4AF37",
        annotation_text="[INSPECTION CURSOR]",
        annotation_position="top left",
        annotation_font=dict(family="JetBrains Mono, monospace", size=10, color="#D4AF37")
    )

    fig_focus.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0D111A",
        plot_bgcolor="#080A0F",
        margin=dict(l=40, r=30, t=25, b=35),
        height=300,
        font=dict(family="Plus Jakarta Sans, sans-serif", size=11, color="#8E8A82"),
        hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        xaxis=dict(title="", gridcolor="#161D2B", linecolor="rgba(212, 175, 55, 0.2)", showgrid=True),
        yaxis=dict(title="ENERGY (kWh)", gridcolor="#161D2B", linecolor="rgba(212, 175, 55, 0.2)", showgrid=True)
    )

    st.plotly_chart(fig_focus, use_container_width=True)

    st.markdown(
        """
        <div class="section-header">
            <span class="section-title">FLEET-WIDE INCIDENT CHRONOLOGY OVERVIEW</span>
            <span class="section-sub">COMPLETE DATASET TIMELINE // RED POINTS = ANOMALIES</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    step = max(1, len(df_chiller) // 1200)
    bg_df = df_chiller.iloc[::step].copy()

    # Guarantee current_ts is explicitly in bg_df so cursor line is drawn accurately
    if row["timestamp"] not in bg_df["timestamp"].values:
        bg_df = pd.concat([bg_df, df_chiller.iloc[[selected_idx]]]).sort_values("timestamp")

    fig_full = go.Figure()

    fig_full.add_trace(
        go.Scatter(
            x=bg_df["timestamp"],
            y=bg_df[energy_col],
            mode="lines",
            name="OBSERVED PROFILE",
            line=dict(color="#334155", width=1),
            hoverinfo="skip"
        )
    )

    if total_anomalies > 0:
        anom_full_df = df_chiller.iloc[anomaly_indices]
        fig_full.add_trace(
            go.Scatter(
                x=anom_full_df["timestamp"],
                y=anom_full_df[energy_col],
                mode="markers",
                name="ANOMALOUS INCIDENTS",
                marker=dict(size=4, color="#EF4444"),
                hovertemplate="<b>INCIDENT</b><br>TIME: %{x}<br>DEMAND: %{y:.1f} kWh<extra></extra>"
            )
        )

    fig_full.add_vline(
        x=current_ts,
        line_width=1.5,
        line_dash="solid",
        line_color="#D4AF37"
    )

    fig_full.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0D111A",
        plot_bgcolor="#080A0F",
        margin=dict(l=40, r=30, t=20, b=35),
        height=220,
        font=dict(family="Plus Jakarta Sans, sans-serif", size=10, color="#8E8A82"),
        hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        xaxis=dict(title="", gridcolor="#161D2B", linecolor="rgba(212, 175, 55, 0.2)", showgrid=True),
        yaxis=dict(title="ENERGY (kWh)", gridcolor="#161D2B", linecolor="rgba(212, 175, 55, 0.2)", showgrid=True)
    )

    st.plotly_chart(fig_full, use_container_width=True)

    st.markdown(
        """
        <div class="section-header">
            <span class="section-title">THERMODYNAMIC SENSOR TELEMETRY AT CURSOR</span>
            <span class="section-sub">SIMULTANEOUS SENSOR MEASUREMENTS AT TIMELOCKED INTERVAL</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="metric-panel">
                <div class="metric-panel-header">COOLING WATER TEMP</div>
                <div class="metric-panel-val" style="font-size: 1.25rem;">{row.get('Cooling Water Temperature (C)', 0.0):.1f} <span style="font-size: 0.75rem; color: #8E8A82;">°C</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-panel">
                <div class="metric-panel-header">CHILLED WATER RATE</div>
                <div class="metric-panel-val" style="font-size: 1.25rem;">{row.get('Chilled Water Rate (L/sec)', 0.0):.1f} <span style="font-size: 0.75rem; color: #8E8A82;">L/s</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f"""
            <div class="metric-panel">
                <div class="metric-panel-header">BUILDING LOAD</div>
                <div class="metric-panel-val" style="font-size: 1.25rem; color: #D4AF37;">{row.get('Building Load (RT)', 0.0):.1f} <span style="font-size: 0.75rem; color: #8E8A82;">RT</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c4:
        st.markdown(
            f"""
            <div class="metric-panel">
                <div class="metric-panel-header">OUTSIDE TEMP</div>
                <div class="metric-panel-val" style="font-size: 1.25rem;">{row.get('Outside Temperature (F)', 0.0):.1f} <span style="font-size: 0.75rem; color: #8E8A82;">°F</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown(
            f"""
            <div class="metric-panel">
                <div class="metric-panel-header">RELATIVE HUMIDITY</div>
                <div class="metric-panel-val" style="font-size: 1.25rem;">{row.get('Humidity (%)', 0.0):.1f} <span style="font-size: 0.75rem; color: #8E8A82;">%</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c6:
        st.markdown(
            f"""
            <div class="metric-panel">
                <div class="metric-panel-header">DEW POINT</div>
                <div class="metric-panel-val" style="font-size: 1.25rem;">{row.get('Dew Point (F)', 0.0):.1f} <span style="font-size: 0.75rem; color: #8E8A82;">°F</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c7:
        st.markdown(
            f"""
            <div class="metric-panel">
                <div class="metric-panel-header">WIND SPEED</div>
                <div class="metric-panel-val" style="font-size: 1.25rem;">{row.get('Wind Speed (mph)', 0.0):.1f} <span style="font-size: 0.75rem; color: #8E8A82;">mph</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c8:
        st.markdown(
            f"""
            <div class="metric-panel">
                <div class="metric-panel-header">ATM PRESSURE</div>
                <div class="metric-panel-val" style="font-size: 1.25rem;">{row.get('Pressure (in)', 0.0):.2f} <span style="font-size: 0.75rem; color: #8E8A82;">in</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )
