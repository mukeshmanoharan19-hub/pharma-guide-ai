"""Example natural language queries to exercise each registered tool.

These can be fed to the tool_agent or supervisor for end-to-end testing.
"""

QUERIES = {
    "search_medicine": [
        "Search for paracetamol tablets",
        "Find medicines with salt paracetamol",
        "Show me products containing dolo",
    ],
    "alternative_medicine": [
        "What are alternatives to PARA-500?",
        "Find substitutes for DOLO-500",
    ],
    "stock_availability": [
        "Is PARA-500 in stock?",
        "Check availability of OOS-1",
    ],
    "product_details": [
        "Give me full details of PARA-500",
        "What is the price and description of DOLO-500?",
    ],
    "add_to_cart": [
        "Add 2 units of PARA-500 to my cart",
        "Put DOLO-500 in the cart",
    ],
    "remove_from_cart": [
        "Remove PARA-500 from my cart",
    ],
    "update_cart": [
        "Change quantity of PARA-500 to 3",
        "Set DOLO-500 quantity to 0",
    ],
    "view_cart": [
        "Show my cart",
        "What's in my cart right now?",
    ],
    "create_order": [
        "Place an order from my cart",
        "Checkout now",
    ],
    "order_status": [
        "What's the status of order <order_id>?",
    ],
    "user_profile": [
        "Show my profile",
        "What is my email and order count?",
    ],
    "purchase_history": [
        "Show my recent purchases",
        "List my last 5 orders",
    ],
}

def print_all_queries():
    for tool, qs in QUERIES.items():
        print(f"\n## {tool}")
        for q in qs:
            print(f"- {q}")


if __name__ == "__main__":
    print_all_queries()
