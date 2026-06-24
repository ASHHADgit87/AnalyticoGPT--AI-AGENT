import streamlit as st
from services.dataset_service import DatasetService

def render_upload_layout():
    st.markdown('<div class="main-header">⚡ DATA INGESTION ENGINE</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Target Tabular Dataset", type=["csv"])
    
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        service = DatasetService()
        metadata = service.process_and_profile_upload(uploaded_file.name, file_bytes)
        st.session_state["dataset_metadata"] = metadata
        st.success(f"Ingested {metadata.file_name} successfully across multi-agent workspace pipeline context.")