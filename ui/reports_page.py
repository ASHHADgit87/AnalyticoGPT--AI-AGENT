import streamlit as st
import os


def render_reports_layout():
    st.markdown(
        '<div class="main-header"> EXECUTIVE REPORT CORES</div>',
        unsafe_allow_html=True,
    )

    pipeline_result = st.session_state.get("pipeline_result")
    if pipeline_result and pipeline_result.get("report_path"):
        rep = pipeline_result["report_path"]
        if os.path.exists(rep):
            st.write(f" Generated Asset Reference: {os.path.basename(rep)}")
            with open(rep, "rb") as pdf_file:
                st.download_button(
                    label="Download Asset Report PDF",
                    data=pdf_file,
                    file_name=os.path.basename(rep),
                    mime="application/pdf",
                )
        else:
            st.info("The report file referenced by the session is missing on disk.")
    else:
        st.info(
            "No report generated in this session. Upload & process a dataset to generate a report."
        )
