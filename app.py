"""
TimeWise - Turnaround Time (TAT) Analytics & Prediction System
Application Shell and Dashboard (Part 1 & Part 2)
"""

from datetime import datetime, time
import altair as alt
import pandas as pd
import streamlit as st

from src.database import (
    test_connection,
    get_total_predictions,
    get_average_turnaround,
    get_latest_prediction,
    get_recent_predictions,
    get_all_predictions,
)

# Configure page settings
st.set_page_config(
    page_title="TimeWise",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Design System CSS
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Typography & Global Resets */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    color: #17212B;
}

/* Background of entire application */
.stApp {
    background-color: #F7F9F8 !important;
}

/* Remove default Streamlit top decoration / header background */
header[data-testid="stHeader"] {
    background-color: transparent !important;
    z-index: 1;
}

/* Main block container compact spacing */
.main .block-container {
    padding-top: 1.75rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
    box-shadow: 1px 0 3px rgba(0, 0, 0, 0.02) !important;
    width: 260px !important;
}

/* Sidebar content flex layout */
section[data-testid="stSidebar"] > div:first-child {
    background-color: #FFFFFF !important;
    padding: 1.25rem 1rem 1.25rem 1rem !important;
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
}

/* Sidebar navigation buttons */
[data-testid="stSidebar"] div.stButton {
    margin-bottom: 0.2rem !important;
}

[data-testid="stSidebar"] div.stButton > button {
    width: 100% !important;
    border-radius: 8px !important;
    padding: 0.55rem 0.85rem !important;
    font-size: 0.875rem !important;
    line-height: 1.25rem !important;
    text-align: left !important;
    justify-content: flex-start !important;
    box-shadow: none !important;
    transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease !important;
    min-height: 2.4rem !important;
}

/* Inactive nav button */
[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
    background-color: transparent !important;
    color: #17212B !important;
    border: 1px solid transparent !important;
    font-weight: 500 !important;
}

[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
    background-color: #F1F5F3 !important;
    color: #17212B !important;
    border: 1px solid #E2E8F0 !important;
}

[data-testid="stSidebar"] div.stButton > button[kind="secondary"] span,
[data-testid="stSidebar"] div.stButton > button[kind="secondary"] p {
    color: #17212B !important;
    font-weight: 500 !important;
}

/* Active nav button */
[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background-color: #E7F5EC !important;
    color: #198754 !important;
    border: 1px solid #D0EAD9 !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover {
    background-color: #DCF2E4 !important;
    color: #198754 !important;
    border: 1px solid #BFE4CC !important;
}

[data-testid="stSidebar"] div.stButton > button[kind="primary"] span,
[data-testid="stSidebar"] div.stButton > button[kind="primary"] p {
    color: #198754 !important;
    font-weight: 600 !important;
}

/* Logo container in sidebar */
.timewise-logo-container {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0.35rem 0.4rem 1.1rem 0.4rem;
    border-bottom: 1px solid #E2E8F0;
    margin-bottom: 1rem;
}

.timewise-logo-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background-color: #E7F5EC;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.timewise-logo-icon svg {
    width: 18px;
    height: 18px;
    color: #198754;
}

.timewise-logo-text {
    font-size: 1.2rem;
    font-weight: 700;
    color: #17212B;
    letter-spacing: -0.02em;
    line-height: 1.2;
}

/* Bottom branding panel */
.sidebar-bottom-panel {
    margin-top: 2rem;
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 12px 14px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.bottom-panel-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.8125rem;
    font-weight: 600;
    color: #17212B;
}

.status-dot-green {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background-color: #198754;
    display: inline-block;
    flex-shrink: 0;
}

.bottom-panel-meta {
    font-size: 0.725rem;
    color: #64748B;
    margin-top: 4px;
    padding-left: 15px;
}

/* Header typography */
.page-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #17212B;
    margin: 0;
    line-height: 1.25;
    letter-spacing: -0.02em;
}

.page-subtitle {
    font-size: 0.875rem;
    color: #64748B;
    margin-top: 4px;
    margin-bottom: 1.25rem;
}

/* Metric Cards */
.metric-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 16px 18px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    min-height: 114px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    margin-bottom: 1rem;
}

.metric-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
}

.metric-card-label {
    font-size: 0.8125rem;
    font-weight: 500;
    color: #64748B;
}

.metric-card-icon {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    background-color: #E7F5EC;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #198754;
    flex-shrink: 0;
}

.metric-card-value {
    font-size: 1.625rem;
    font-weight: 700;
    color: #17212B;
    line-height: 1.15;
    letter-spacing: -0.02em;
}

.metric-card-sub {
    font-size: 0.75rem;
    color: #64748B;
    margin-top: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Chart and Section Panels */
.card-panel {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 18px 20px 14px 20px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    margin-bottom: 1.25rem;
}

.card-panel-title {
    font-size: 0.9375rem;
    font-weight: 600;
    color: #17212B;
    margin-bottom: 2px;
}

.card-panel-sub {
    font-size: 0.775rem;
    color: #64748B;
    margin-bottom: 12px;
}

/* Section Header for Recent Predictions */
.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #17212B;
    margin: 0;
    line-height: 1.25;
}

.section-subtitle {
    font-size: 0.8rem;
    color: #64748B;
    margin-top: 2px;
}

/* Recent Predictions Table */
.recent-table-container {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    margin-top: 0.75rem;
    margin-bottom: 1.5rem;
}

.recent-table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
}

.recent-table th {
    background-color: #F8FAFC;
    color: #64748B;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: 10px 16px;
    border-bottom: 1px solid #E2E8F0;
}

.recent-table td {
    padding: 11px 16px;
    font-size: 0.84rem;
    color: #17212B;
    border-bottom: 1px solid #F1F5F9;
}

.recent-table tr:last-child td {
    border-bottom: none;
}

.recent-table tr:hover td {
    background-color: #F8FAFC;
}

.badge-pill-green {
    display: inline-flex;
    align-items: center;
    background-color: #E7F5EC;
    color: #198754;
    font-weight: 600;
    font-size: 0.8125rem;
    padding: 2px 8px;
    border-radius: 4px;
}

/* Empty State Container */
.empty-state-box {
    border: 1.5px dashed #E2E8F0;
    border-radius: 8px;
    padding: 38px 20px;
    text-align: center;
    background-color: #F8FAFC;
    margin-top: 8px;
    margin-bottom: 8px;
}

.empty-state-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: #17212B;
    margin-bottom: 4px;
}

.empty-state-desc {
    font-size: 0.775rem;
    color: #64748B;
    max-width: 380px;
    margin: 0 auto;
}

/* MongoDB Offline Banner */
.db-offline-banner {
    display: flex;
    align-items: center;
    gap: 10px;
    background-color: #FEF3F2;
    border: 1px solid #FECDCA;
    color: #B42318;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.8125rem;
    font-weight: 500;
    margin-bottom: 1.25rem;
}

/* Main content placeholder card for other tabs */
.content-surface {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 28px 32px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.content-header-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #17212B;
    margin-bottom: 4px;
    letter-spacing: -0.02em;
}

.content-header-desc {
    font-size: 0.875rem;
    color: #64748B;
    margin-bottom: 24px;
}

.content-placeholder-box {
    border: 1.5px dashed #E2E8F0;
    border-radius: 8px;
    padding: 48px 24px;
    text-align: center;
    background-color: #F8FAFC;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Navigation Configuration
NAV_ITEMS = [
    {"id": "Dashboard", "label": "Dashboard", "icon": ":material/dashboard:"},
    {"id": "New Prediction", "label": "New Prediction", "icon": ":material/add_circle:"},
    {"id": "Prediction History", "label": "Prediction History", "icon": ":material/history:"},
    {"id": "Model Performance", "label": "Model Performance", "icon": ":material/analytics:"},
    {"id": "Settings", "label": "Settings", "icon": ":material/settings:"},
]

# Initialize state from query params or default
if "current_page" not in st.session_state:
    query_page = st.query_params.get("page", "Dashboard")
    valid_ids = [item["id"] for item in NAV_ITEMS]
    st.session_state.current_page = query_page if query_page in valid_ids else "Dashboard"

# Render Sidebar (Preserved exactly from Part 1)
with st.sidebar:
    # 1. Logo area: Green timer/clock icon + TimeWise text
    logo_html = """
    <div class="timewise-logo-container">
        <div class="timewise-logo-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
        </div>
        <div class="timewise-logo-text">TimeWise</div>
    </div>
    """
    st.markdown(logo_html, unsafe_allow_html=True)

    # 2. Navigation items
    for item in NAV_ITEMS:
        is_active = (st.session_state.current_page == item["id"])
        btn_type = "primary" if is_active else "secondary"

        if st.button(
            item["label"],
            icon=item["icon"],
            key=f"nav_{item['id']}",
            type=btn_type,
            use_container_width=True
        ):
            if not is_active:
                st.session_state.current_page = item["id"]
                st.query_params["page"] = item["id"]
                st.rerun()

    # 3. Bottom branding panel
    branding_html = """
    <div class="sidebar-bottom-panel">
        <div class="bottom-panel-header">
            <span class="status-dot-green"></span>
            <span>TimeWise Platform</span>
        </div>
        <div class="bottom-panel-meta">TAT Prediction Engine • v1.0</div>
    </div>
    """
    st.markdown(branding_html, unsafe_allow_html=True)

# Safe database connection check
@st.cache_data(ttl=5)
def safe_check_connection():
    return test_connection()

is_db_connected = safe_check_connection()

# Current Active Page Content
current_page = st.session_state.current_page

if current_page == "Dashboard":
    # ----------------------------------------------------
    # DASHBOARD PAGE
    # ----------------------------------------------------

    # Offline warning banner if MongoDB is unreachable
    if not is_db_connected:
        st.markdown(
            """
            <div class="db-offline-banner">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <span>MongoDB connection failed. Displaying offline mode; database metrics may be unavailable.</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Dashboard Header with Date Filter Control
    header_col1, header_col2 = st.columns([3.2, 1.3])

    with header_col1:
        st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-subtitle">Overview of predictions, activity, and model performance.</div>', unsafe_allow_html=True)

    with header_col2:
        date_filter = st.date_input(
            "Filter Period",
            value=(),
            help="Filter dashboard metrics and charts by created date range",
            label_visibility="collapsed"
        )

    # Build date query filter if dates are selected
    filter_query = {}
    if date_filter:
        if isinstance(date_filter, (tuple, list)):
            if len(date_filter) == 2:
                start_dt = datetime.combine(date_filter[0], time.min)
                end_dt = datetime.combine(date_filter[1], time.max)
                filter_query = {"created_at": {"$gte": start_dt, "$lte": end_dt}}
            elif len(date_filter) == 1:
                start_dt = datetime.combine(date_filter[0], time.min)
                end_dt = datetime.combine(date_filter[0], time.max)
                filter_query = {"created_at": {"$gte": start_dt, "$lte": end_dt}}

    # Safe Read Data Operations
    total_count = get_total_predictions(query=filter_query) if is_db_connected else 0
    avg_turnaround = get_average_turnaround(query=filter_query) if is_db_connected else None
    latest_pred = get_latest_prediction() if is_db_connected else None
    recent_records = get_recent_predictions(limit=5, query=filter_query) if is_db_connected else []
    chart_records = get_all_predictions(limit=100, query=filter_query, sort_ascending=True) if is_db_connected else []

    # Format values for metric cards
    # Card 1: Total Predictions
    total_val_str = f"{total_count:,}"
    total_sub_str = "Filtered period" if filter_query else "Stored in MongoDB"

    # Card 2: Average Turnaround (Labeled clearly as average predicted turnaround)
    if avg_turnaround is not None:
        avg_val_str = f"{avg_turnaround:.2f}d"
        avg_sub_str = "Average predicted turnaround"
    else:
        avg_val_str = "N/A"
        avg_sub_str = "No predictions in range"

    # Card 3: Latest Prediction
    if latest_pred and "predicted_days" in latest_pred and latest_pred["predicted_days"] is not None:
        latest_val_str = f"{float(latest_pred['predicted_days']):.2f}d"
        created_time = latest_pred.get("created_at")
        if isinstance(created_time, datetime):
            if created_time.date() == datetime.now().date():
                latest_sub_str = f"Today, {created_time.strftime('%H:%M')}"
            else:
                latest_sub_str = created_time.strftime("%d %b, %H:%M")
        else:
            latest_sub_str = "Most recent record"
    else:
        latest_val_str = "None"
        latest_sub_str = "No record saved"

    # Card 4: Model Validation R2
    # Display genuine validation score from existing evaluation results if available; else Unavailable.
    model_r2_val = "Unavailable"
    model_r2_sub = "Evaluation results not logged"

    # Metric Cards Row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    with m_col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-top">
                    <span class="metric-card-label">Total Predictions</span>
                    <div class="metric-card-icon">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
                            <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
                            <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
                        </svg>
                    </div>
                </div>
                <div class="metric-card-value">{total_val_str}</div>
                <div class="metric-card-sub">{total_sub_str}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m_col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-top">
                    <span class="metric-card-label">Average Turnaround</span>
                    <div class="metric-card-icon">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"></circle>
                            <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                    </div>
                </div>
                <div class="metric-card-value">{avg_val_str}</div>
                <div class="metric-card-sub">{avg_sub_str}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m_col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-top">
                    <span class="metric-card-label">Latest Prediction</span>
                    <div class="metric-card-icon">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                        </svg>
                    </div>
                </div>
                <div class="metric-card-value">{latest_val_str}</div>
                <div class="metric-card-sub">{latest_sub_str}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m_col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-top">
                    <span class="metric-card-label">Model Validation R²</span>
                    <div class="metric-card-icon">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                        </svg>
                    </div>
                </div>
                <div class="metric-card-value">{model_r2_val}</div>
                <div class="metric-card-sub">{model_r2_sub}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ----------------------------------------------------
    # Charts Section
    # ----------------------------------------------------
    chart_col1, chart_col2 = st.columns(2)

    # Prepare DataFrame for charts from real MongoDB records only
    chart_df = pd.DataFrame()
    if chart_records:
        parsed_records = []
        for i, r in enumerate(chart_records):
            c_at = r.get("created_at")
            c_at_str = c_at.strftime("%d %b %H:%M") if isinstance(c_at, datetime) else f"Record #{i+1}"
            parsed_records.append({
                "index": i + 1,
                "label": f"#{i+1} ({c_at.strftime('%H:%M') if isinstance(c_at, datetime) else ''})",
                "date_str": str(r.get("start_time", "")),
                "start_hour": int(r.get("start_hour", 0)),
                "predicted_days": round(float(r.get("predicted_days", 0.0)), 2),
                "created_at_str": c_at_str,
            })
        chart_df = pd.DataFrame(parsed_records)

    with chart_col1:
        st.markdown(
            """
            <div class="card-panel">
                <div class="card-panel-title">Predicted Turnaround Time Trend</div>
                <div class="card-panel-sub">Turnaround time trend across logged predictions</div>
            """,
            unsafe_allow_html=True
        )
        if not chart_df.empty and len(chart_df) >= 1:
            trend_chart = (
                alt.Chart(chart_df)
                .mark_line(
                    color="#198754",
                    strokeWidth=2,
                    point=alt.OverlayMarkDef(color="#198754", size=48, fill="#FFFFFF", strokeWidth=2)
                )
                .encode(
                    x=alt.X(
                        "label:N",
                        title="Prediction Sequence",
                        sort=None,
                        axis=alt.Axis(labelColor="#64748B", titleColor="#64748B", labelAngle=0)
                    ),
                    y=alt.Y(
                        "predicted_days:Q",
                        title="Predicted TAT (Days)",
                        scale=alt.Scale(zero=True),
                        axis=alt.Axis(labelColor="#64748B", titleColor="#64748B", gridColor="#F1F5F9")
                    ),
                    tooltip=[
                        alt.Tooltip("label:N", title="Sequence"),
                        alt.Tooltip("date_str:N", title="Start Date"),
                        alt.Tooltip("start_hour:Q", title="Start Hour"),
                        alt.Tooltip("predicted_days:Q", title="Predicted Days", format=".2f"),
                        alt.Tooltip("created_at_str:N", title="Created At"),
                    ]
                )
                .properties(height=210)
                .configure_view(strokeWidth=0)
            )
            st.altair_chart(trend_chart, use_container_width=True)
        else:
            st.markdown(
                """
                <div class="empty-state-box">
                    <div class="empty-state-title">No Prediction Data</div>
                    <div class="empty-state-desc">Generate predictions to visualize turnaround time trends over time.</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with chart_col2:
        st.markdown(
            """
            <div class="card-panel">
                <div class="card-panel-title">Prediction Distribution</div>
                <div class="card-panel-sub">Spread of predicted turnaround duration in days</div>
            """,
            unsafe_allow_html=True
        )
        if not chart_df.empty and len(chart_df) >= 1:
            dist_chart = (
                alt.Chart(chart_df)
                .mark_bar(
                    color="#198754",
                    cornerRadiusTopLeft=4,
                    cornerRadiusTopRight=4,
                    opacity=0.88
                )
                .encode(
                    x=alt.X(
                        "predicted_days:Q",
                        bin=alt.Bin(maxbins=8),
                        title="Turnaround Days",
                        axis=alt.Axis(labelColor="#64748B", titleColor="#64748B")
                    ),
                    y=alt.Y(
                        "count():Q",
                        title="Count",
                        axis=alt.Axis(labelColor="#64748B", titleColor="#64748B", gridColor="#F1F5F9", tickMinStep=1)
                    ),
                    tooltip=[
                        alt.Tooltip("count():Q", title="Frequency"),
                    ]
                )
                .properties(height=210)
                .configure_view(strokeWidth=0)
            )
            st.altair_chart(dist_chart, use_container_width=True)
        else:
            st.markdown(
                """
                <div class="empty-state-box">
                    <div class="empty-state-title">No Distribution Data</div>
                    <div class="empty-state-desc">Prediction distribution histogram will appear once records are created.</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # Recent Predictions Section
    # ----------------------------------------------------
    rec_head_col1, rec_head_col2 = st.columns([3.8, 1.2])

    with rec_head_col1:
        st.markdown('<div class="section-title">Recent Predictions</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Latest records stored in MongoDB</div>', unsafe_allow_html=True)

    with rec_head_col2:
        if st.button("View all →", key="btn_view_all_history", type="secondary", use_container_width=True):
            st.session_state.current_page = "Prediction History"
            st.query_params["page"] = "Prediction History"
            st.rerun()

    if recent_records:
        table_rows = []
        for r in recent_records:
            date_val = str(r.get("start_time", "N/A"))
            start_hour_val = f"{int(r.get('start_hour', 0)):02d}:00"
            tat_val = float(r.get("predicted_days", 0.0))
            tat_str = f"{tat_val:.2f} days"
            c_at = r.get("created_at")
            if isinstance(c_at, datetime):
                created_str = c_at.strftime("%d %b %Y, %H:%M")
            else:
                created_str = str(c_at) if c_at else "N/A"

            table_rows.append(
                f"""
                <tr>
                    <td>{date_val}</td>
                    <td>{start_hour_val}</td>
                    <td><span class="badge-pill-green">{tat_str}</span></td>
                    <td style="color: #64748B;">{created_str}</td>
                </tr>
                """
            )

        table_html = f"""
        <div class="recent-table-container">
            <table class="recent-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Start Hour</th>
                        <th>Predicted Days</th>
                        <th>Created At</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(table_rows)}
                </tbody>
            </table>
        </div>
        """
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <div class="empty-state-box">
                <div class="empty-state-title">No Recent Predictions</div>
                <div class="empty-state-desc">There are no prediction records recorded in MongoDB for this period.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

else:
    # ----------------------------------------------------
    # PLACEHOLDER FOR OTHER PAGES (Unchanged from Part 1)
    # ----------------------------------------------------
    page_descriptions = {
        "New Prediction": "Generate turnaround time prediction using the trained model",
        "Prediction History": "Historical turnaround time prediction records from MongoDB",
        "Model Performance": "Evaluation metrics and comparative model benchmarks",
        "Settings": "Application configuration and system preferences",
    }

    placeholder_html = f"""
    <div class="content-surface">
        <div class="content-header-title">{current_page}</div>
        <div class="content-header-desc">{page_descriptions.get(current_page, "")}</div>
        <div class="content-placeholder-box">
            <div class="placeholder-title">Content Placeholder</div>
            <div class="placeholder-detail">
                The shell and navigation system are initialized. The components for <strong>{current_page}</strong> will be implemented in subsequent parts.
            </div>
        </div>
    </div>
    """
    st.markdown(placeholder_html, unsafe_allow_html=True)
