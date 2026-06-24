import streamlit as st
import os


def render_reports_layout():
    st.markdown(
        '<div class="main-header">📋 SYSTEM REVENUE & EXECUTIVE REPORT CORES</div>',
        unsafe_allow_html=True,
    )
    report_dir = "outputs/reports"

    if os.path.exists(report_dir):
        reports = [f for f in os.listdir(report_dir) if f.endswith(".pdf")]
        if reports:
            for rep in reports:
                st.write(f"📄 Generated Asset Reference: {rep}")
                with open(os.path.join(report_dir, rep), "rb") as pdf_file:
                    st.download_button(
                        label="Download Asset Report PDF",
                        data=pdf_file,
                        file_name=rep,
                        mime="application/pdf",
                    )
        else:
            st.info("No corporate asset reports compiled yet.")
    else:
        st.info("Report manager workspaces initialization pending pipeline completion.")
