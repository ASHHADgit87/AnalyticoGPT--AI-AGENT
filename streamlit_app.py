import streamlit as st

st.set_page_config(
    page_title="AnalyticoGPT",
    page_icon="public/assets/logo.svg",
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
        margin-top: -3rem;
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
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden !important; }
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; }

    [data-testid="stSidebar"][aria-expanded="false"] {
        margin-left: 0 !important;
        transform: none !important;
        display: flex !important;
        min-width: 244px !important;
        width: 244px !important;
    }

    /* ── SIDEBAR NAV ── */
    .nav-label {
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.15em;
        color: #4b5563;
        text-transform: uppercase;
        padding: 0 0.25rem;
        margin-bottom: 0.5rem;
    }

    .nav-btn {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        width: 100%;
        padding: 0.65rem 1rem;
        margin-bottom: 0.3rem;
        border-radius: 10px;
        border: 1px solid transparent;
        background: transparent;
        color: #9ca3af;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.875rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: left;
    }

    .nav-btn:hover {
        background: rgba(99, 102, 241, 0.08);
        border-color: rgba(99, 102, 241, 0.25);
        color: #e5e7eb;
    }

    .nav-btn.active {
        background: linear-gradient(135deg, rgba(99,102,241,0.18) 0%, rgba(168,85,247,0.12) 100%);
        border-color: rgba(99, 102, 241, 0.45);
        color: #a5b4fc;
        font-weight: 600;
    }

    .nav-btn .icon {
        font-size: 1rem;
        min-width: 1.25rem;
        text-align: center;
    }

    .nav-divider {
        height: 1px;
        background: #1f293d;
        margin: 1rem 0;
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

st.sidebar.image("public/assets/logo1.svg", use_container_width=True)
st.sidebar.markdown("---")

pages = [
    ("Workspace Operations Hub", "", "Overview & metrics"),
    ("Ingest Data", "", "Upload & clean data"),
    ("Graphical Analytics", "", "Charts & trends"),
    ("AI Deep Insights", "", "LLM-powered analysis"),
    ("Analysis Report", "", "Reports & exports"),
]

if "nav_page" not in st.session_state:
    st.session_state.nav_page = pages[0][0]

st.sidebar.markdown('<p class="nav-label">Management</p>', unsafe_allow_html=True)

for page_name, icon, subtitle in pages:
    is_active = st.session_state.nav_page == page_name
    active_cls = "active" if is_active else ""
    clicked = st.sidebar.button(
        page_name,
        key=f"nav_{page_name}",
        use_container_width=True,
    )
    if clicked:
        st.session_state.nav_page = page_name
        st.rerun()


st.sidebar.markdown(
    f"""
<style>
div[data-testid="stSidebar"] button {{
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 10px !important;
    color: #9ca3af !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    padding: 0.65rem 1rem !important;
    margin-bottom: 0.3rem !important;
    text-align: left !important;
    transition: all 0.2s ease !important;
}}
div[data-testid="stSidebar"] button:hover {{
    background: rgba(99, 102, 241, 0.08) !important;
    border-color: rgba(99, 102, 241, 0.25) !important;
    color: #e5e7eb !important;
}}
div[data-testid="stSidebar"] button[kind="secondary"]:nth-of-type({pages.index((st.session_state.nav_page, *[p[1:] for p in pages if p[0]==st.session_state.nav_page][0])) + 1}) {{
    background: linear-gradient(135deg, rgba(99,102,241,0.18) 0%, rgba(168,85,247,0.12) 100%) !important;
    border-color: rgba(99, 102, 241, 0.45) !important;
    color: #a5b4fc !important;
    font-weight: 600 !important;
}}
</style>
""",
    unsafe_allow_html=True,
)

st.sidebar.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)

navigation_option = st.session_state.nav_page

if navigation_option == "Workspace Operations Hub":
    render_dashboard_layout()
elif navigation_option == "Ingest Data":
    render_upload_layout()
elif navigation_option == "Graphical Analytics":
    render_charts_layout()
elif navigation_option == "AI Deep Insights":
    render_insights_layout()
elif navigation_option == "Analysis Report":
    render_reports_layout()
