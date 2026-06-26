import streamlit as st

st.set_page_config(
    page_title="AnalyticoGPT",
    page_icon="public/assets/logo.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "mobile_menu_open" not in st.session_state:
    st.session_state.mobile_menu_open = False

if "page" in st.query_params:
    requested = st.query_params["page"]
    valid_pages = [
        "Workspace Operations Hub",
        "Ingest Data",
        "Graphical Analytics",
        "AI Deep Insights",
        "Analysis Report",
    ]
    if requested in valid_pages and st.session_state.get("nav_page") != requested:
        st.session_state.nav_page = requested
        st.session_state.mobile_menu_open = False

mobile_open = st.session_state.mobile_menu_open

st.markdown(
    f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: #08090f !important;
        font-family: 'Space Grotesk', sans-serif !important;
        color: #f3f4f6 !important;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: #0d0e15 !important;
        border-right: 1px solid #1f293d !important;
    }}
    
    .main-header {{
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: -4rem;
        margin-bottom: 2rem;
        letter-spacing: -0.05em;
    }}
    
    .metric-card {{
        background: rgba(17, 18, 27, 0.8);
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, border-color 0.3s ease;
        margin-bottom: 1rem;
    }}
    
    .metric-card:hover {{
        transform: translateY(-5px);
        border-color: #6366f1;
    }}

    @media (max-width: 700px) {{
        .metric-card {{
            width: 100% !important;
            max-width: 100% !important;
            margin-left: 0 !important;
            margin-right: 0 !important;
        }}
    }}
    
    .metric-card h3 {{
        color: #a855f7 !important;
        font-size: 2.2rem !important;
        margin: 0;
        font-weight: 700;
    }}
    
    .metric-card p {{
        color: #9ca3af !important;
        margin: 0.5rem 0 0 0;
        font-size: 0.9rem;
    }}
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: visible; opacity: 0; pointer-events: none; height: 3rem; }}
    header {{ visibility: hidden !important; }}
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="collapsedControl"] {{ display: none !important; }}
    [data-testid="stSidebarCollapseButton"] {{ display: none !important; }}
    
    @media (max-width: 700px) {{
        html, body {{
            height: auto !important;
            overflow: auto !important;
        }}
        [data-testid="stAppViewContainer"] {{
            min-height: 100vh !important;
            overflow: auto !important;
            padding-bottom: 4rem !important;
        }}
        .block-container {{
            min-height: auto !important;
            overflow: visible !important;
        }}
    }}

    @media (min-width: 701px) {{
        [data-testid="stSidebar"][aria-expanded="false"] {{
            margin-left: 0 !important;
            transform: none !important;
            display: flex !important;
            min-width: 244px !important;
            width: 244px !important;
        }}
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) {{
            display: none !important;
        }}
    }}

    .nav-label {{
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.15em;
        color: #4b5563;
        text-transform: uppercase;
        padding: 0 0.25rem;
        margin-bottom: 0.5rem;
    }}

    .nav-btn {{
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
    }}

    .nav-btn:hover {{
        background: rgba(99, 102, 241, 0.08);
        border-color: rgba(99, 102, 241, 0.25);
        color: #e5e7eb;
    }}

    .nav-btn.active {{
        background: linear-gradient(135deg, rgba(99,102,241,0.18) 0%, rgba(168,85,247,0.12) 100%);
        border-color: rgba(99, 102, 241, 0.45);
        color: #a5b4fc;
        font-weight: 600;
    }}

    .nav-btn .icon {{
        font-size: 1rem;
        min-width: 1.25rem;
        text-align: center;
    }}

    .nav-divider {{
        height: 1px;
        background: #1f293d;
        margin: 1rem 0;
    }}

    @media (max-width: 700px) {{
        .main-header {{
            margin-top: -1rem !important;
        }}

        [data-testid="stSidebar"],
        [data-testid="stSidebar"][aria-expanded="false"],
        [data-testid="stSidebar"][aria-expanded="true"] {{
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            width: 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
            z-index: 10001 !important;
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            transform: none !important;
            margin: 0 !important;
            padding: 0 !important;
            background: rgba(13, 14, 21, 0.97) !important;
            backdrop-filter: blur(12px) !important;
            border-right: none !important;
            border-bottom: 1px solid #1f293d !important;
            {"height: 100% !important; max-height: 100% !important; inset: 0 !important; overflow-y: auto !important;" if mobile_open else "height: 5rem !important; max-height: 5rem !important; overflow: hidden !important;"}
        }}

        [data-testid="stSidebarHeader"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stLogoSpacer"] {{
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            overflow: hidden !important;
        }}

        [data-testid="stSidebarContent"] {{
            width: 100% !important;
            height: 100% !important;
            padding: 0.65rem 1rem !important;
            margin: 0 !important;
            overflow: {"visible" if mobile_open else "hidden"} !important;
        }}

        [data-testid="stSidebarUserContent"] {{
            width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }}

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
            display: grid !important;
            grid-template-columns: 1fr auto !important;
            grid-auto-rows: auto !important;
            grid-auto-flow: row dense !important;
            gap: 0.5rem !important;
            width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }}

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:first-child {{
            grid-column: 1 / 2 !important;
            width: auto !important;
            margin: 0 !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
        }}

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) {{
            grid-column: 2 / 3 !important;
            width: auto !important;
            margin: 0 !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-self: end !important;
        }}

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(n+3) {{
            grid-column: 1 / -1 !important;
            width: 100% !important;
        }}

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:first-child img,
        [data-testid="stSidebar"] [data-testid="stImage"] img {{
            height: 2.2rem !important;
            margin-top: 0.78rem;
            width: auto !important;
            max-height: 2.2rem !important;
            display: block !important;
            object-fit: contain !important;
        }}

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) {{
            flex: 0 0 auto !important;
            width: auto !important;
            margin: 0 !important;
            padding: 0 !important;
        }}

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) [data-testid="stButton"] {{
            width: auto !important;
            margin: 0 !important;
        }}

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) button,
        [data-testid="stSidebar"] button[key="mobile_menu_toggle"],
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) button p {{
            width: auto !important;
            min-width: 2.5rem !important;
            padding: 0.25rem 0.5rem !important;
            margin: 0 !important;
            background: transparent !important;
            border: none !important;
            color: #f3f4f6 !important;
            font-size: 1.6rem !important;
            line-height: 1 !important;
            box-shadow: none !important;
        }}

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) button:hover {{
            color: #a5b4fc !important;
            background: transparent !important;
            border: none !important;
        }}

        {"[data-testid=\"stSidebar\"] [data-testid=\"stVerticalBlock\"] > div:nth-child(n+3) { display: block !important; }" if mobile_open else "[data-testid=\"stSidebar\"] [data-testid=\"stVerticalBlock\"] > div:nth-child(n+3) { display: none !important; }"}

        [data-testid="stAppViewContainer"] {{
            margin-top: 5.25rem !important;
            margin-left: 0 !important;
            width: 100% !important;
            max-width: 100% !important;
            min-height: calc(100vh - 5.25rem) !important;
            overflow-y: auto !important;
            display: flex !important;
            flex-direction: column !important;
        }}

        [data-testid="stAppViewContainer"] > section.main {{
            width: 100% !important;
            max-width: 100% !important;
            flex: 1 !important;
            min-height: 100% !important;
        }}

        .block-container {{
            padding: 1rem 0.75rem 4rem 0.75rem !important;
            max-width: 100% !important;
            flex: 1 !important;
        }}

        .element-container {{
            width: 100% !important;
        }}

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(n+4) button,
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(n+4) .stButton > button {{
            width: 100% !important;
        }}
    }}
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

toggle_icon = "✕" if st.session_state.mobile_menu_open else "☰"
if st.sidebar.button(toggle_icon, key="mobile_menu_toggle"):
    st.session_state.mobile_menu_open = not st.session_state.mobile_menu_open
    st.rerun()

st.sidebar.markdown("---")

pages = [
    ("Workspace Operations Hub", "", "Overview & metrics"),
    ("Ingest Data", "", "Upload & clean data"),
    ("Graphical Analytics", "", "Charts & trends"),
    ("AI Deep Insights", "", "LLM-powered analysis"),
    ("Analysis Report", "", "Reports & exports"),
]
page_names = [page[0] for page in pages]
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
        st.query_params["page"] = page_name
        st.session_state.mobile_menu_open = False
        st.rerun()


st.sidebar.markdown(
    f"""
<style>
div[data-testid="stSidebar"] button:nth-of-type(n+2) {{
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
div[data-testid="stSidebar"] button:nth-of-type(n+2):hover {{
    background: rgba(99, 102, 241, 0.08) !important;
    border-color: rgba(99, 102, 241, 0.25) !important;
    color: #e5e7eb !important;
}}
div[data-testid="stSidebar"] button[kind="secondary"]:nth-of-type({pages.index((st.session_state.nav_page, *[p[1:] for p in pages if p[0]==st.session_state.nav_page][0])) + 2}) {{
    background: linear-gradient(135deg, rgba(99,102,241,0.18) 0%, rgba(168,85,247,0.12) 100%) !important;
    border-color: rgba(99, 102, 241, 0.45) !important;
    color: #a5b4fc !important;
    font-weight: 600 !important;
}}
@media (max-width: 700px) {{
    div[data-testid="stSidebar"] button:nth-of-type(1) {{
        font-size: 1.6rem !important;
        padding: 0.25rem 0.5rem !important;
        color: #f3f4f6 !important;
        width: auto !important;
        min-width: 2.5rem !important;
    }}
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
