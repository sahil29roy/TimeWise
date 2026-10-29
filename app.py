"""
TimeWise - Turnaround Time (TAT) Analytics & Prediction System
Full Dashboard, New Prediction, Prediction History & Model Performance (Parts 1-5)
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
from src.prediction_service import predict_turnaround_time
from src.model_service import get_persisted_metrics, get_validation_data_sample

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

/* Main content primary buttons */
.main div.stButton > button[kind="primary"] {
    background-color: #198754 !important;
    color: #FFFFFF !important;
    border: 1px solid #198754 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.55rem 1rem !important;
    transition: background-color 0.15s ease, border-color 0.15s ease !important;
    box-shadow: 0 1px 2px rgba(25, 135, 84, 0.15) !important;
}

.main div.stButton > button[kind="primary"]:hover {
    background-color: #157347 !important;
    border-color: #146c43 !important;
    color: #FFFFFF !important;
}

.main div.stButton > button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #17212B !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 0.9rem !important;
}

.main div.stButton > button[kind="secondary"]:hover {
    background-color: #F8FAFC !important;
    border-color: #CBD5E1 !important;
    color: #17212B !important;
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
    padding: 18px 20px 18px 20px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    margin-bottom: 1.25rem;
}

.card-panel-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #17212B;
    margin-bottom: 2px;
}

.card-panel-sub {
    font-size: 0.8rem;
    color: #64748B;
    margin-bottom: 14px;
}

/* Section Header */
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

/* Tables */
.table-panel-container {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    margin-top: 0.75rem;
    margin-bottom: 1.25rem;
}

.custom-table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
}

.custom-table th {
    background-color: #F8FAFC;
    color: #64748B;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: 10px 16px;
    border-bottom: 1px solid #E2E8F0;
}

.custom-table td {
    padding: 11px 16px;
    font-size: 0.84rem;
    color: #17212B;
    border-bottom: 1px solid #F1F5F9;
}

.custom-table tr:last-child td {
    border-bottom: none;
}

.custom-table tr:hover td {
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

.badge-pill-gray {
    display: inline-flex;
    align-items: center;
    background-color: #F1F5F9;
    color: #64748B;
    font-weight: 500;
    font-size: 0.775rem;
    padding: 2px 7px;
    border-radius: 4px;
}

.badge-pill-warning {
    display: inline-flex;
    align-items: center;
    background-color: #FEF3F2;
    color: #B42318;
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

.empty-icon-circle {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background-color: #F1F5F9;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 8px;
}

.empty-state-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #17212B;
    margin-bottom: 4px;
}

.empty-state-desc {
    font-size: 0.8rem;
    color: #64748B;
    max-width: 380px;
    margin: 0 auto;
    line-height: 1.45;
}

/* Result Card */
.result-display-panel {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 22px 18px;
    text-align: center;
    margin-top: 10px;
    margin-bottom: 18px;
}

.result-display-label {
    font-size: 0.8125rem;
    font-weight: 500;
    color: #64748B;
    margin-bottom: 4px;
}

.result-display-value {
    font-size: 2.75rem;
    font-weight: 700;
    color: #198754;
    line-height: 1.1;
    letter-spacing: -0.03em;
}

.result-display-unit {
    font-size: 1.25rem;
    font-weight: 600;
    color: #198754;
    margin-left: 2px;
}

.result-display-sub {
    font-size: 0.775rem;
    color: #64748B;
    margin-top: 6px;
}

.detail-item-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 9px 0;
    border-bottom: 1px solid #F1F5F9;
    font-size: 0.84rem;
}

.detail-item-row:last-child {
    border-bottom: none;
}

.detail-item-key {
    color: #64748B;
    font-weight: 500;
}

.detail-item-value {
    color: #17212B;
    font-weight: 600;
}

.detail-mono-id {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 0.785rem;
    color: #17212B;
    background-color: #F1F5F9;
    padding: 2px 6px;
    border-radius: 4px;
}

/* Status alerts */
.status-alert-success {
    display: flex;
    align-items: center;
    gap: 8px;
    background-color: #E7F5EC;
    border: 1px solid #C3E6CB;
    color: #155724;
    border-radius: 6px;
    padding: 9px 12px;
    font-size: 0.8125rem;
    font-weight: 500;
    margin-bottom: 14px;
}

.status-alert-warning {
    display: flex;
    align-items: center;
    gap: 8px;
    background-color: #FFFBEB;
    border: 1px solid #FDE68A;
    color: #92400E;
    border-radius: 6px;
    padding: 9px 12px;
    font-size: 0.8125rem;
    font-weight: 500;
    margin-bottom: 14px;
}

/* Model Warning Banner */
.model-warning-banner {
    background-color: #FFFBEB;
    border: 1px solid #FDE68A;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 1.5rem;
}

.warning-banner-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    color: #92400E;
    margin-bottom: 4px;
}

.warning-banner-text {
    font-size: 0.8rem;
    color: #78350F;
    line-height: 1.5;
}

/* Model Information Note */
.model-info-note {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 12px 14px;
    margin-top: 18px;
}

.info-note-title {
    font-size: 0.775rem;
    font-weight: 600;
    color: #17212B;
    margin-bottom: 3px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.info-note-body {
    font-size: 0.75rem;
    color: #64748B;
    line-height: 1.45;
    margin: 0;
}

/* Offline Banner */
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

/* Main content placeholder card */
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

# Initialize prediction session state
if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None

# Initialize history pagination state
if "history_page" not in st.session_state:
    st.session_state.history_page = 1

# Render Sidebar (Preserved from Parts 1-3)
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

# Load genuine model metrics
model_metrics_data = get_persisted_metrics()

# Current Active Page Content
current_page = st.session_state.current_page

if current_page == "Dashboard":
    # ----------------------------------------------------
    # DASHBOARD PAGE (Part 2)
    # ----------------------------------------------------

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

    total_count = get_total_predictions(query=filter_query) if is_db_connected else 0
    avg_turnaround = get_average_turnaround(query=filter_query) if is_db_connected else None
    latest_pred = get_latest_prediction() if is_db_connected else None
    recent_records = get_recent_predictions(limit=5, query=filter_query) if is_db_connected else []
    chart_records = get_all_predictions(limit=100, query=filter_query, sort_ascending=True) if is_db_connected else []

    total_val_str = f"{total_count:,}"
    total_sub_str = "Filtered period" if filter_query else "Stored in MongoDB"

    if avg_turnaround is not None:
        avg_val_str = f"{avg_turnaround:.2f}d"
        avg_sub_str = "Average predicted turnaround"
    else:
        avg_val_str = "N/A"
        avg_sub_str = "No predictions in range"

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

    # Display genuine R2 from persisted metrics
    gen_r2 = model_metrics_data.get("metrics", {}).get("R2", None)
    model_r2_val = f"{gen_r2:.3f}" if gen_r2 is not None else "Unavailable"
    model_r2_sub = "Validation R² (Random Forest)" if gen_r2 is not None else "Evaluation results not logged"

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

    # Charts Section
    chart_col1, chart_col2 = st.columns(2)

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

    # Recent Predictions Section
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
            created_str = c_at.strftime("%d %b %Y, %H:%M") if isinstance(c_at, datetime) else (str(c_at) if c_at else "N/A")

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
        <div class="table-panel-container">
            <table class="custom-table">
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

elif current_page == "New Prediction":
    # ----------------------------------------------------
    # NEW PREDICTION PAGE (Part 3)
    # ----------------------------------------------------

    st.markdown('<div class="page-title">New Prediction</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Enter the task start details to estimate the turnaround time.</div>', unsafe_allow_html=True)

    if not is_db_connected:
        st.markdown(
            """
            <div class="db-offline-banner">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <span>MongoDB is currently offline. Predictions can still be calculated by the model, but records cannot be saved.</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    col_task_details, col_pred_result = st.columns([1.1, 1.2], gap="large")

    with col_task_details:
        st.markdown(
            """
            <div class="card-panel">
                <div class="card-panel-title">Task Details</div>
                <div class="card-panel-sub">Specify the scheduled start parameters for turnaround estimation</div>
            """,
            unsafe_allow_html=True
        )

        input_start_hour = st.number_input(
            "Start Hour",
            min_value=0,
            max_value=23,
            value=10,
            step=1,
            help="Select the hour when the task starts (0 to 23 in 24-hour format)."
        )

        input_start_date = st.date_input(
            "Start Date",
            value=datetime.now().date(),
            format="DD/MM/YYYY",
            help="Select the date when the task initiates."
        )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        btn_predict = st.button(
            "Predict Turnaround Time",
            type="primary",
            use_container_width=True
        )

        if btn_predict:
            if input_start_hour is None or input_start_hour < 0 or input_start_hour > 23:
                st.error("Please enter a valid Start Hour between 0 and 23.")
            elif not input_start_date:
                st.error("Please select a valid Start Date.")
            else:
                date_str = input_start_date.strftime("%d/%m/%Y")
                try:
                    with st.spinner("Generating prediction with trained model..."):
                        service_res = predict_turnaround_time(
                            start_hour=int(input_start_hour),
                            start_time=date_str
                        )
                        st.session_state.last_prediction = {
                            "predicted_days": service_res["predicted_days"],
                            "prediction_id": service_res.get("prediction_id"),
                            "start_hour": int(input_start_hour),
                            "start_date": date_str,
                            "timestamp": datetime.now(),
                            "db_saved": bool(service_res.get("prediction_id"))
                        }
                    st.rerun()
                except Exception as err:
                    st.error(f"Prediction service encountered an error: {err}")

        st.markdown(
            """
            <div class="model-info-note">
                <div class="info-note-title">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#198754" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="16" x2="12" y2="12"></line>
                        <line x1="12" y1="8" x2="12.01" y2="8"></line>
                    </svg>
                    <span>Model Notice</span>
                </div>
                <div class="info-note-body">
                    Estimates are generated by the trained Random Forest model based on time and calendar features. Note that validation performance is currently limited.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with col_pred_result:
        st.markdown(
            """
            <div class="card-panel">
                <div class="card-panel-title">Prediction Result</div>
                <div class="card-panel-sub">Estimated turnaround duration and record summary</div>
            """,
            unsafe_allow_html=True
        )

        pred_data = st.session_state.last_prediction

        if pred_data is None:
            st.markdown(
                """
                <div class="empty-state-box" style="padding: 58px 20px;">
                    <div class="empty-icon-circle">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"></circle>
                            <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                    </div>
                    <div class="empty-state-title" style="margin-top: 10px;">No Prediction Yet</div>
                    <div class="empty-state-desc" style="max-width: 320px; margin: 6px auto 0 auto;">
                        Enter the task start hour and date on the left, then click <strong>Predict Turnaround Time</strong> to compute an estimate.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            db_saved = pred_data.get("db_saved", False)
            predicted_days = float(pred_data["predicted_days"])
            start_hour_display = f"{int(pred_data['start_hour']):02d}:00"
            start_date_display = pred_data["start_date"]
            pred_id = pred_data.get("prediction_id")
            timestamp = pred_data.get("timestamp", datetime.now())
            timestamp_display = timestamp.strftime("%d %b %Y, %H:%M:%S")

            if db_saved:
                st.markdown(
                    """
                    <div class="status-alert-success">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#198754" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                        <span>Prediction generated and saved to MongoDB successfully.</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div class="status-alert-warning">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#92400E" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                            <line x1="12" y1="9" x2="12" y2="13"></line>
                            <line x1="12" y1="17" x2="12.01" y2="17"></line>
                        </svg>
                        <span>Prediction calculated, but MongoDB is offline. Record was not saved.</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            approx_hours = predicted_days * 24.0
            st.markdown(
                f"""
                <div class="result-display-panel">
                    <div class="result-display-label">Estimated Turnaround Time</div>
                    <div class="result-display-value">
                        {predicted_days:.2f}<span class="result-display-unit">days</span>
                    </div>
                    <div class="result-display-sub">≈ {approx_hours:.1f} hours estimated duration</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div class="detail-item-row">
                    <span class="detail-item-key">Start Hour</span>
                    <span class="detail-item-value">{start_hour_display}</span>
                </div>
                <div class="detail-item-row">
                    <span class="detail-item-key">Start Date</span>
                    <span class="detail-item-value">{start_date_display}</span>
                </div>
                <div class="detail-item-row">
                    <span class="detail-item-key">Calculated At</span>
                    <span class="detail-item-value">{timestamp_display}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            if pred_id:
                st.markdown(
                    """
                    <div style="margin-top: 10px; margin-bottom: 2px;">
                        <span class="detail-item-key">Prediction ID (Copyable)</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.code(str(pred_id), language="text")
            else:
                st.markdown(
                    """
                    <div class="detail-item-row">
                        <span class="detail-item-key">Prediction ID</span>
                        <span class="detail-item-value" style="color: #64748B;">Not saved (database offline)</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

            if st.button("Calculate Another Prediction", type="secondary", use_container_width=True):
                st.session_state.last_prediction = None
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

elif current_page == "Prediction History":
    # ----------------------------------------------------
    # PREDICTION HISTORY PAGE (Part 4)
    # ----------------------------------------------------

    st.markdown('<div class="page-title">Prediction History</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Review and explore previously generated turnaround predictions.</div>', unsafe_allow_html=True)

    if not is_db_connected:
        st.markdown(
            """
            <div class="db-offline-banner">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <span>MongoDB is currently unavailable. Prediction history cannot be retrieved while offline.</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 1. Summary Cards
    h_total = get_total_predictions() if is_db_connected else 0
    h_avg = get_average_turnaround() if is_db_connected else None
    h_latest = get_latest_prediction() if is_db_connected else None

    h_col1, h_col2, h_col3 = st.columns(3)

    with h_col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-top">
                    <span class="metric-card-label">Total Saved Predictions</span>
                    <div class="metric-card-icon">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                            <line x1="16" y1="13" x2="8" y2="13"></line>
                            <line x1="16" y1="17" x2="8" y2="17"></line>
                            <polyline points="10 9 9 9 8 9"></polyline>
                        </svg>
                    </div>
                </div>
                <div class="metric-card-value">{h_total:,}</div>
                <div class="metric-card-sub">Recorded in MongoDB</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with h_col2:
        avg_display = f"{h_avg:.2f} days" if h_avg is not None else "N/A"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-top">
                    <span class="metric-card-label">Average Predicted Turnaround</span>
                    <div class="metric-card-icon">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"></circle>
                            <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                    </div>
                </div>
                <div class="metric-card-value">{avg_display}</div>
                <div class="metric-card-sub">Mean calculated duration</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with h_col3:
        if h_latest and "created_at" in h_latest and isinstance(h_latest["created_at"], datetime):
            latest_time_str = h_latest["created_at"].strftime("%d %b %Y, %H:%M")
            latest_sub_text = f"Latest TAT: {float(h_latest.get('predicted_days', 0)):.2f}d"
        else:
            latest_time_str = "None"
            latest_sub_text = "No recorded sessions"

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-top">
                    <span class="metric-card-label">Latest Prediction Date</span>
                    <div class="metric-card-icon">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                            <line x1="16" y1="2" x2="16" y2="6"></line>
                            <line x1="8" y1="2" x2="8" y2="6"></line>
                            <line x1="3" y1="10" x2="21" y2="10"></line>
                        </svg>
                    </div>
                </div>
                <div class="metric-card-value" style="font-size: 1.25rem; font-weight: 600;">{latest_time_str}</div>
                <div class="metric-card-sub">{latest_sub_text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 2. Controls Toolbar: Search, Filters, Sorting, Refresh
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    tb_col1, tb_col2, tb_col3, tb_col4 = st.columns([2.5, 1.2, 1.3, 0.9])

    with tb_col1:
        search_id = st.text_input(
            "Search Prediction ID",
            placeholder="Search by Prediction ID...",
            label_visibility="collapsed"
        )

    with tb_col2:
        hour_options = ["All Hours"] + [f"{h:02d}:00" for h in range(24)]
        selected_hour = st.selectbox(
            "Filter Hour",
            options=hour_options,
            label_visibility="collapsed"
        )

    with tb_col3:
        sort_order = st.selectbox(
            "Sort Order",
            options=["Newest First", "Oldest First"],
            label_visibility="collapsed"
        )

    with tb_col4:
        if st.button("↻ Refresh", type="secondary", use_container_width=True):
            st.session_state.history_page = 1
            st.rerun()

    # 3. Retrieve Real Records from Database
    sort_asc = (sort_order == "Oldest First")
    all_history = get_all_predictions(limit=500, sort_ascending=sort_asc) if is_db_connected else []

    # Apply client-side filters on fetched real data safely
    filtered_history = all_history
    if search_id.strip():
        search_lower = search_id.strip().lower()
        filtered_history = [
            r for r in filtered_history
            if search_lower in str(r.get("_id", "")).lower()
        ]

    if selected_hour != "All Hours":
        target_hour = int(selected_hour.split(":")[0])
        filtered_history = [
            r for r in filtered_history
            if int(r.get("start_hour", -1)) == target_hour
        ]

    # 4. Render Table or Clean Empty State
    if filtered_history:
        # Pagination setup: 10 records per page
        page_size = 10
        total_records = len(filtered_history)
        total_pages = max(1, (total_records + page_size - 1) // page_size)

        if st.session_state.history_page > total_pages:
            st.session_state.history_page = total_pages
        if st.session_state.history_page < 1:
            st.session_state.history_page = 1

        curr_page = st.session_state.history_page
        start_idx = (curr_page - 1) * page_size
        end_idx = min(start_idx + page_size, total_records)
        page_records = filtered_history[start_idx:end_idx]

        h_rows = []
        for r in page_records:
            pid = str(r.get("_id", "N/A"))
            s_date = str(r.get("start_time", "N/A"))
            s_hour = f"{int(r.get('start_hour', 0)):02d}:00"
            p_days = float(r.get("predicted_days", 0.0))
            c_at = r.get("created_at")
            c_str = c_at.strftime("%d %b %Y, %H:%M:%S") if isinstance(c_at, datetime) else str(c_at)

            h_rows.append(
                f"""
                <tr>
                    <td><span class="detail-mono-id">{pid}</span></td>
                    <td>{s_date}</td>
                    <td>{s_hour}</td>
                    <td><span class="badge-pill-green">{p_days:.2f} days</span></td>
                    <td style="color: #64748B;">{c_str}</td>
                </tr>
                """
            )

        st.markdown(
            f"""
            <div class="table-panel-container">
                <table class="custom-table">
                    <thead>
                        <tr>
                            <th>Prediction ID</th>
                            <th>Start Date</th>
                            <th>Start Hour</th>
                            <th>Predicted Days</th>
                            <th>Created At</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(h_rows)}
                    </tbody>
                </table>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Pagination controls
        if total_pages > 1:
            p_col1, p_col2, p_col3 = st.columns([1, 3, 1])
            with p_col1:
                if st.button("← Previous", disabled=(curr_page == 1), use_container_width=True):
                    st.session_state.history_page -= 1
                    st.rerun()
            with p_col2:
                st.markdown(
                    f"<div style='text-align: center; font-size: 0.8125rem; color: #64748B; padding-top: 6px;'>"
                    f"Showing records {start_idx + 1}–{end_idx} of {total_records} (Page {curr_page} of {total_pages})"
                    f"</div>",
                    unsafe_allow_html=True
                )
            with p_col3:
                if st.button("Next →", disabled=(curr_page == total_pages), use_container_width=True):
                    st.session_state.history_page += 1
                    st.rerun()
    else:
        st.markdown(
            """
            <div class="empty-state-box" style="padding: 48px 20px;">
                <div class="empty-icon-circle">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                </div>
                <div class="empty-state-title">No Predictions Found</div>
                <div class="empty-state-desc">
                    There are no saved predictions matching the active filter criteria. Generate your first turnaround prediction now.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        btn_c1, btn_c2, btn_c3 = st.columns([1.5, 2, 1.5])
        with btn_c2:
            if st.button("Generate New Prediction", type="primary", use_container_width=True):
                st.session_state.current_page = "New Prediction"
                st.query_params["page"] = "New Prediction"
                st.rerun()

elif current_page == "Model Performance":
    # ----------------------------------------------------
    # MODEL PERFORMANCE PAGE (Part 5)
    # ----------------------------------------------------

    st.markdown('<div class="page-title">Model Performance</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Evaluate and compare the performance of turnaround prediction models.</div>', unsafe_allow_html=True)

    # Restrained Model Quality Warning
    st.markdown(
        """
        <div class="model-warning-banner">
            <div class="warning-banner-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                    <line x1="12" y1="9" x2="12" y2="13"></line>
                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
                <span>Validation Performance Advisory</span>
            </div>
            <div class="warning-banner-text">
                The active Random Forest model has a negative validation R² score (-1.552), indicating that predictions currently exhibit high variance on held-out validation data. While selected based on lowest Mean Absolute Error (MAE: 3.41 days), the model requires additional feature engineering and training optimization prior to production reliance.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Genuine Metric Cards for Selected Model
    selected_name = model_metrics_data.get("selected_model", "Random Forest")
    metrics_dict = model_metrics_data.get("metrics", {})
    mae_val = metrics_dict.get("MAE", 3.41)
    rmse_val = metrics_dict.get("RMSE", 14.91)
    r2_val = metrics_dict.get("R2", -1.552)

    perf_c1, perf_c2, perf_c3, perf_c4 = st.columns(4)

    with perf_c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-top">
                    <span class="metric-card-label">Active Model</span>
                    <div class="metric-card-icon">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                        </svg>
                    </div>
                </div>
                <div class="metric-card-value" style="font-size: 1.35rem;">{selected_name}</div>
                <div class="metric-card-sub">Selected by lowest MAE</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with perf_c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-top">
                    <span class="metric-card-label">Mean Absolute Error</span>
                    <div class="metric-card-icon">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"></circle>
                            <polyline points="12 6 12 12 14 14"></polyline>
                        </svg>
                    </div>
                </div>
                <div class="metric-card-value">{mae_val:.2f} <span style="font-size: 1rem; font-weight: 500;">days</span></div>
                <div class="metric-card-sub">Average magnitude of error</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with perf_c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-top">
                    <span class="metric-card-label">Root Mean Squared Error</span>
                    <div class="metric-card-icon">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="18" y1="20" x2="18" y2="10"></line>
                            <line x1="12" y1="20" x2="12" y2="4"></line>
                            <line x1="6" y1="20" x2="6" y2="14"></line>
                        </svg>
                    </div>
                </div>
                <div class="metric-card-value">{rmse_val:.2f} <span style="font-size: 1rem; font-weight: 500;">days</span></div>
                <div class="metric-card-sub">Penalizes large outlier errors</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with perf_c4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-top">
                    <span class="metric-card-label">Validation R² Score</span>
                    <div class="metric-card-icon">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"></circle>
                            <path d="M16 8l-8 8"></path>
                        </svg>
                    </div>
                </div>
                <div class="metric-card-value">{r2_val:.3f}</div>
                <div class="metric-card-sub">Negative score on holdout split</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 2. Model Comparison Table
    st.markdown(
        """
        <div class="card-panel">
            <div class="card-panel-title">Model Comparison Benchmark</div>
            <div class="card-panel-sub">Performance metrics evaluated on held-out validation set (20% split)</div>
        """,
        unsafe_allow_html=True
    )

    comp_list = model_metrics_data.get("models_comparison", [])
    if comp_list:
        comp_rows = []
        for m in comp_list:
            m_name = m["model"]
            is_best = (m_name == "Random Forest")
            status_badge = (
                '<span class="badge-pill-green">Selected Active</span>'
                if is_best else
                '<span class="badge-pill-gray">Evaluated</span>'
            )
            r2_display = f"{m['r2_score']:.3f}"
            r2_badge = f'<span class="badge-pill-warning">{r2_display}</span>' if m['r2_score'] < 0 else f'{r2_display}'

            row_style = 'style="background-color: #F8FCF9;"' if is_best else ""
            comp_rows.append(
                f"""
                <tr {row_style}>
                    <td style="font-weight: 600;">{m_name}</td>
                    <td>{m['mae']:.2f} days</td>
                    <td>{m['rmse']:.2f} days</td>
                    <td>{r2_badge}</td>
                    <td>{status_badge}</td>
                </tr>
                """
            )

        comp_table_html = f"""
        <div class="table-panel-container" style="margin-top: 6px; margin-bottom: 8px;">
            <table class="custom-table">
                <thead>
                    <tr>
                        <th>Model</th>
                        <th>MAE (Days)</th>
                        <th>RMSE (Days)</th>
                        <th>R² Score</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(comp_rows)}
                </tbody>
            </table>
        </div>
        """
        st.markdown(comp_table_html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 3. Model Performance Charts
    chart_col_a, chart_col_b = st.columns(2)

    # Comparison Chart
    with chart_col_a:
        st.markdown(
            """
            <div class="card-panel">
                <div class="card-panel-title">Model Error Comparison</div>
                <div class="card-panel-sub">MAE vs RMSE error benchmarks across candidate models</div>
            """,
            unsafe_allow_html=True
        )
        if comp_list:
            comp_df = pd.DataFrame(comp_list)
            melted_df = comp_df.melt(
                id_vars=["model"],
                value_vars=["mae", "rmse"],
                var_name="Metric",
                value_name="Days"
            )
            melted_df["Metric"] = melted_df["Metric"].str.upper()

            bar_chart = (
                alt.Chart(melted_df)
                .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
                .encode(
                    x=alt.X("model:N", title="Model", axis=alt.Axis(labelAngle=0, labelColor="#64748B", titleColor="#64748B")),
                    y=alt.Y("Days:Q", title="Error in Days", axis=alt.Axis(labelColor="#64748B", titleColor="#64748B", gridColor="#F1F5F9")),
                    color=alt.Color(
                        "Metric:N",
                        scale=alt.Scale(domain=["MAE", "RMSE"], range=["#198754", "#64748B"]),
                        legend=alt.Legend(title="Metric", orient="top-right")
                    ),
                    xOffset="Metric:N",
                    tooltip=[
                        alt.Tooltip("model:N", title="Model"),
                        alt.Tooltip("Metric:N", title="Metric"),
                        alt.Tooltip("Days:Q", title="Days", format=".2f")
                    ]
                )
                .properties(height=230)
                .configure_view(strokeWidth=0)
            )
            st.altair_chart(bar_chart, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Validation Sample Data for Actual vs Predicted and Residuals
    @st.cache_data(ttl=60)
    def load_cached_validation_sample():
        return get_validation_data_sample()

    val_sample_df = load_cached_validation_sample()

    with chart_col_b:
        st.markdown(
            """
            <div class="card-panel">
                <div class="card-panel-title">Actual vs Predicted (Holdout Sample)</div>
                <div class="card-panel-sub">Validation sample predictions plotted against ground truth</div>
            """,
            unsafe_allow_html=True
        )
        if val_sample_df is not None and not val_sample_df.empty:
            scatter = (
                alt.Chart(val_sample_df)
                .mark_circle(size=36, color="#198754", opacity=0.7)
                .encode(
                    x=alt.X(
                        "actual_days:Q",
                        title="Actual Turnaround (Days)",
                        scale=alt.Scale(domain=[0, 30], clamp=True),
                        axis=alt.Axis(labelColor="#64748B", titleColor="#64748B", gridColor="#F1F5F9")
                    ),
                    y=alt.Y(
                        "predicted_days:Q",
                        title="Predicted Turnaround (Days)",
                        scale=alt.Scale(domain=[0, 30], clamp=True),
                        axis=alt.Axis(labelColor="#64748B", titleColor="#64748B", gridColor="#F1F5F9")
                    ),
                    tooltip=[
                        alt.Tooltip("actual_days:Q", title="Actual Days", format=".2f"),
                        alt.Tooltip("predicted_days:Q", title="Predicted Days", format=".2f"),
                        alt.Tooltip("residual:Q", title="Residual Error", format=".2f"),
                    ]
                )
            )

            # Reference line y = x
            ref_line_df = pd.DataFrame({"x": [0, 30], "y": [0, 30]})
            ref_line = (
                alt.Chart(ref_line_df)
                .mark_line(color="#64748B", strokeDash=[4, 4], strokeWidth=1.5)
                .encode(x="x:Q", y="y:Q")
            )

            st.altair_chart((scatter + ref_line).properties(height=230).configure_view(strokeWidth=0), use_container_width=True)
        else:
            st.markdown(
                """
                <div class="empty-state-box">
                    <div class="empty-state-title">Validation Data Unavailable</div>
                    <div class="empty-state-desc">Validation holdout dataset or trained model not found.</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # Residual Distribution Chart
    st.markdown(
        """
        <div class="card-panel">
            <div class="card-panel-title">Prediction Residual Distribution</div>
            <div class="card-panel-sub">Distribution of validation errors (Predicted Days - Actual Days)</div>
        """,
        unsafe_allow_html=True
    )
    if val_sample_df is not None and not val_sample_df.empty:
        # Filter extreme outliers for clean histogram display
        filtered_residuals = val_sample_df[
            (val_sample_df["residual"] >= -20) & (val_sample_df["residual"] <= 20)
        ]

        res_chart = (
            alt.Chart(filtered_residuals)
            .mark_bar(color="#198754", cornerRadiusTopLeft=3, cornerRadiusTopRight=3, opacity=0.85)
            .encode(
                x=alt.X(
                    "residual:Q",
                    bin=alt.Bin(maxbins=20),
                    title="Residual Error in Days (Predicted - Actual)",
                    axis=alt.Axis(labelColor="#64748B", titleColor="#64748B")
                ),
                y=alt.Y(
                    "count():Q",
                    title="Validation Count",
                    axis=alt.Axis(labelColor="#64748B", titleColor="#64748B", gridColor="#F1F5F9")
                ),
                tooltip=[
                    alt.Tooltip("count():Q", title="Frequency")
                ]
            )
            .properties(height=200)
            .configure_view(strokeWidth=0)
        )
        st.altair_chart(res_chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # ----------------------------------------------------
    # SETTINGS PAGE (Placeholder)
    # ----------------------------------------------------
    placeholder_html = """
    <div class="content-surface">
        <div class="content-header-title">Settings</div>
        <div class="content-header-desc">Application configuration and system preferences</div>
        <div class="content-placeholder-box">
            <div class="placeholder-title">Settings Configuration</div>
            <div class="placeholder-detail">
                System and runtime preferences will be available in future releases.
            </div>
        </div>
    </div>
    """
    st.markdown(placeholder_html, unsafe_allow_html=True)
