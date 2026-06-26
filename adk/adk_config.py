import os
import streamlit as st


class ADKConfig:
    MODEL_NAME = "gemini-2.5-flash"

    @staticmethod
    def _get_api_key():
        env_key = os.getenv("GOOGLE_API_KEY")
        if env_key:
            return env_key
        try:
            return st.secrets.get("GOOGLE_API_KEY")
        except Exception:
            return None

    API_KEY = _get_api_key()

    @classmethod
    def validate_config(cls):
        if not cls.API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY is missing (set in .env or Streamlit secrets)"
            )
