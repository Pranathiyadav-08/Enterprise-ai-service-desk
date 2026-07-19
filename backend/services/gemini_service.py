import google.generativeai as genai
from config import settings

genai.configure(api_key=settings.gemini_api_key)

_model = genai.GenerativeModel(model_name=settings.gemini_model)


def generate_response(user_message: str) -> str:
    response = _model.generate_content(user_message)
    return response.text
