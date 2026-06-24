from google import genai
from adk.adk_config import ADKConfig


def fetch_gemini_structural_completion(
    prompt: str, system_instruction: str = None
) -> str:
    ADKConfig.validate_config()
    client = genai.Client(api_key=ADKConfig.API_KEY)

    config_args = {"temperature": 0.15}
    if system_instruction:
        config_args["system_instruction"] = system_instruction

    response = client.models.generate_content(
        model=ADKConfig.MODEL_NAME, contents=prompt, config=config_args
    )
    return response.text
