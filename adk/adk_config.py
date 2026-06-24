import os
from dotenv import load_dotenv

load_dotenv()


class ADKConfig:
    MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    API_KEY = os.getenv("GOOGLE_API_KEY")

    @classmethod
    def validate_config(cls):
        if not cls.API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is missing")
