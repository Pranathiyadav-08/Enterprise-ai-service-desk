import ollama
from config import settings

_VALID_INTENTS = {"HR_POLICY", "IT_SUPPORT", "COMPANY_POLICY", "GENERAL"}

_SYSTEM_PROMPT = """You are an intent classification engine for an enterprise service desk.

Classify the user query into EXACTLY ONE of these categories:
- HR_POLICY       → questions about leaves, salary, benefits, appraisals, attendance
- IT_SUPPORT      → issues with devices, software, VPN, network, passwords, access
- COMPANY_POLICY  → questions about work from home, office rules, code of conduct, travel policy
- GENERAL         → greetings, small talk, or anything that does not fit above categories

Examples:
User: My VPN is not connecting
Category: IT_SUPPORT

User: How many casual leaves do I get?
Category: HR_POLICY

User: What is the work from home policy?
Category: COMPANY_POLICY

User: Hello
Category: GENERAL

User: My laptop is not turning on
Category: IT_SUPPORT

User: What is the maternity leave policy?
Category: HR_POLICY

User: What are the office dress code rules?
Category: COMPANY_POLICY

Rules:
- Reply with ONLY the category name. No explanation, no punctuation, no extra words.
- If unsure, return GENERAL.
"""


def detect_intent(user_query: str) -> str:
    response = ollama.chat(
        model=settings.ollama_model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ],
    )
    intent = response["message"]["content"].strip().upper()
    return intent if intent in _VALID_INTENTS else "GENERAL"
