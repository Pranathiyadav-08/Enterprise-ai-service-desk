import ollama
from config import settings


def generate_response(user_query: str, context: str | None = None) -> str:
    """Generate an Ollama response, optionally grounded in company context."""
    prompt = user_query
    if context is not None:
        prompt = f"""You are an Enterprise AI Assistant.

Answer ONLY using the provided company context.

If the answer is not found in the context,
reply:

"I couldn't find this information in the company knowledge base."

Company Context:

{context}

Employee Question:

{user_query}

Answer:
"""

    response = ollama.chat(
        model=settings.ollama_model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"]
