from agents.supervisor_agent import route_request

test_queries = [
    "My VPN is not connecting",
    "How many sick leaves do I get?",
    "What is the reimbursement policy?",
    "Hello",
]

if __name__ == "__main__":
    print("=" * 50)
    print("      Supervisor Agent - Routing Results")
    print("=" * 50)
    for query in test_queries:
        result = route_request(query)
        print(f"Query          : {query}")
        print(f"Intent         : {result['intent']}")
        print(f"Assigned Agent : {result['assigned_agent']}")
        print("-" * 50)
