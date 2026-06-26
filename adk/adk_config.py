import os
import streamlit as st


class ADKConfig:
    MODEL_NAME = "gemini-2.5-flash"

    API_KEY = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))

    @classmethod
    def validate_config(cls):
        if not cls.API_KEY:
            raise ValueError("GOOGLE_API_KEY is missing (Streamlit Secrets not set)")
