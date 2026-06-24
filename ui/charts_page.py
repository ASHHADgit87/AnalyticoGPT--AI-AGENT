import streamlit as st
import os

def render_charts_layout():
    st.markdown('<div class="main-header">📊 PIPELINE GRAPHICAL INTERFACES</div>', unsafe_allow_html=True)
    chart_dir = "outputs/charts"
    
    if os.path.exists(chart_dir):
        charts = [f for f in os.listdir(chart_dir) if f.endswith('.png')]
        if charts:
            for chart in charts:
                st.image(os.path.join(chart_dir, chart), use_column_width=True)
        else:
            st.info("No active PNG metrics rendered by visualization specialists yet.")
    else:
        st.info("Visualization directory workspace offline.")