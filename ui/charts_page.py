import streamlit as st
import os


def render_charts_layout():
    st.markdown(
        '<div class="main-header"> PIPELINE GRAPHICAL INTERFACES</div>',
        unsafe_allow_html=True,
    )

    pipeline_result = st.session_state.get("pipeline_result")
    if pipeline_result:
        shown = False
        if pipeline_result.get("heatmap_path"):
            st.markdown("### Correlation Heatmap")
            st.image(pipeline_result["heatmap_path"], use_column_width=True)
            shown = True

        if pipeline_result.get("trend_path"):
            st.markdown("### Trend Chart")
            st.image(pipeline_result["trend_path"], use_column_width=True)
            shown = True

        if not shown:
            st.info("No charts were generated for the current dataset.")
    else:
        st.info(
            "No dataset processed in this session. Upload a CSV to generate charts."
        )
