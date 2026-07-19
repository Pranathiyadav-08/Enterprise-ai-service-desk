from agents.intent_agent import detect_intent

_INTENT_ROUTING: dict[str, str] = {
    "HR_POLICY":      "HR Agent",
    "IT_SUPPORT":     "IT Agent",
    "COMPANY_POLICY": "Policy Agent",
    "GENERAL":        "General Agent",
}


def route_request(user_query: str) -> dict:
    intent = detect_intent(user_query)
    return {
        "intent":         intent,
        "assigned_agent": _INTENT_ROUTING[intent],
    }
