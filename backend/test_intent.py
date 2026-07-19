from agents.intent_agent import detect_intent

test_queries = [
    "My VPN is not connecting",
    "How many casual leaves do I get?",
    "What is the work from home policy?",
    "Hello",
]

if __name__ == "__main__":
    print("=" * 45)
    print("       Intent Agent - Test Results")
    print("=" * 45)
    for query in test_queries:
        intent = detect_intent(query)
        print(f"Query  : {query}")
        print(f"Intent : {intent}")
        print("-" * 45)
