import streamlit as st


def render_insights_layout():
    st.markdown(
        '<div class="main-header"> CRITICAL AI NARRATIVE INSIGHTS</div>',
        unsafe_allow_html=True,
    )

    pipeline_result = st.session_state.get("pipeline_result")
    if pipeline_result:
        insight_text = pipeline_result.get(
            "insight_text", "No narrative insights were generated."
        )
        st.markdown(insight_text)
    else:
        st.info(
            "No dataset has been uploaded yet. Upload a CSV in the Data Ingestion Engine to generate insights."
        )
