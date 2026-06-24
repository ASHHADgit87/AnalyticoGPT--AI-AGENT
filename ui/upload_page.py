import streamlit as st
from services.pipeline_service import PipelineService


def render_upload_layout():
    st.markdown(
        '<div class="main-header">⚡ DATA INGESTION ENGINE</div>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("Upload Target Tabular Dataset", type=["csv"])

    if uploaded_file is not None:
        if not uploaded_file.name.lower().endswith(".csv"):
            st.error("Invalid file type. Please upload a .csv file.")
            return

        try:
            file_bytes = uploaded_file.read()
            pipeline = PipelineService()
            with st.spinner("Processing dataset through the full pipeline..."):
                result = pipeline.run_full_pipeline(uploaded_file.name, file_bytes)

            st.session_state["pipeline_result"] = result
            st.success(
                f"Processed {uploaded_file.name} successfully through the full pipeline."
            )

            st.markdown("### Dataset Summary")
            st.write(result["metadata"].dict())

            if result["heatmap_path"]:
                st.markdown("### Correlation Heatmap")
                st.image(result["heatmap_path"], use_column_width=True)

            if result["trend_path"]:
                st.markdown("### Trend Chart")
                st.image(result["trend_path"], use_column_width=True)

            st.markdown("### Top Performers")
            st.write(result["top_performers"])

            st.markdown("### AI Narrative Insights")
            st.markdown(result["insight_text"])

            st.markdown("### Generated Report")
            st.write(result["report_path"])
            with open(result["report_path"], "rb") as pdf_file:
                st.download_button(
                    label="Download generated PDF report",
                    data=pdf_file,
                    file_name=result["report_path"].split("/")[-1],
                    mime="application/pdf",
                )
        except Exception as exc:
            st.error(f"Failed to process upload: {exc}")
