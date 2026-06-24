import streamlit as st

st.set_page_config(
    page_title="AnalyticoGPT | Principal AI Agent Dashboard",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #08090f !important;
        font-family: 'Space Grotesk', sans-serif !important;
        color: #f3f4f6 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0d0e15 !important;
        border-right: 1px solid #1f293d !important;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
        letter-spacing: -0.05em;
    }
    
    .metric-card {
        background: rgba(17, 18, 27, 0.8);
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #6366f1;
    }
    
    .metric-card h3 {
        color: #a855f7 !important;
        font-size: 2.2rem !important;
        margin: 0;
        font-weight: 700;
    }
    
    .metric-card p {
        color: #9ca3af !important;
        margin: 0.5rem 0 0 0;
        font-size: 0.9rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

from ui.dashboard import render_dashboard_layout
from ui.upload_page import render_upload_layout
from ui.charts_page import render_charts_layout
from ui.insights_page import render_insights_layout
from ui.reports_page import render_reports_layout

st.sidebar.markdown(
    '<div style="text-align: center;"><h2 style="color:#6366f1;font-weight:700;margin-bottom:0;">ANALYTICO GPT</h2><p style="color:#6b7280;font-size:0.8rem;margin-top:0;">MULTI-AGENT CORE OPERATIONAL FRAMEWORK</p></div>',
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

navigation_option = st.sidebar.radio(
    "MANAGEMENT CONTROLS",
    [
        "Workspace Operations Hub",
        "Data Ingestion Engine",
        "Graphical Analytics",
        "AI Deep Insights",
        "Export Document Center",
    ],
)

if navigation_option == "Workspace Operations Hub":
    render_dashboard_layout()
elif navigation_option == "Data Ingestion Engine":
    render_upload_layout()
elif navigation_option == "Graphical Analytics":
    render_charts_layout()
elif navigation_option == "AI Deep Insights":
    render_insights_layout()
elif navigation_option == "Export Document Center":
    render_reports_layout()
