from __future__ import annotations

import re

from app.agents.intents import GENERAL
from app.evaluation.datasets import AgentCase
from app.evaluation.deepeval_adapter import compute_deepeval_metrics
from app.evaluation.metrics import jaccard


def _heuristic_intent(query: str) -> str:
    q = query.lower()
    if any(x in q for x in ["track order", "previous orders", "purchase"]):
        return "order_tracking"
    if any(x in q for x in ["checkout", "place order", "confirm order"]):
        return "checkout"
    if any(x in q for x in ["add", "remove", "cart", "quantity", "show my cart"]):
        return "cart"
    if any(x in q for x in ["symptom", "headache", "cold", "fever", "cough"]):
        return "symptom_analysis"
    if any(x in q for x in ["medicine", "sku", "alternative", "tablet", "capsule", "search"]):
        return "medicine_search"
    return GENERAL


def _heuristic_tools(query: str, intent: str) -> list[str]:
    q = query.lower()
    if intent == "checkout":
        return ["confirm_order"] if "confirmation id" in q or "confirm" in q else ["prepare_order"]
    if intent == "cart":
        if "add" in q or "put " in q:
            return ["add_to_cart"]
        if "remove" in q:
            return ["remove_from_cart"]
        if "quantity" in q or "change" in q or "update" in q:
            return ["update_cart"]
        if "show" in q or "view" in q:
            return ["view_cart"]
        return ["view_cart"]
    if intent == "order_tracking":
        return ["order_status"] if re.search(r"[0-9a-f]{8}-", q) else ["purchase_history"]
    if intent == "medicine_search":
        return ["alternative_medicine"] if "alternative" in q else ["search_medicine"]
    if intent == "symptom_analysis":
        return ["search_medicine", "product_details"]
    return []


def evaluate_agent(cases: list[AgentCase], *, live: bool = False) -> dict:
    rows = []
    for case in cases:
        if live:
            from app.agents.supervisor import classify_intent

            classification = classify_intent(case.query)
            predicted_intent = classification.primary_intent
        else:
            predicted_intent = _heuristic_intent(case.query)
        predicted_tools = _heuristic_tools(case.query, predicted_intent)
        expected_tools = set(case.expected_tools)
        predicted_tool_set = set(predicted_tools)
        row = {
            "id": case.id,
            "query": case.query,
            "expected_intent": case.expected_intent,
            "predicted_intent": predicted_intent,
            "routing_correct": 1.0 if predicted_intent == case.expected_intent else 0.0,
            "expected_tools": list(expected_tools),
            "predicted_tools": list(predicted_tool_set),
            "tool_selection_accuracy": jaccard(expected_tools, predicted_tool_set),
            "task_completion_accuracy": 1.0
            if (predicted_intent == case.expected_intent and expected_tools.issubset(predicted_tool_set))
            else 0.0,
        }
        rows.append(row)

    n = max(len(rows), 1)
    result = {
        "count": len(rows),
        "routing_accuracy": sum(r["routing_correct"] for r in rows) / n,
        "tool_selection_accuracy": sum(r["tool_selection_accuracy"] for r in rows) / n,
        "task_completion_accuracy": sum(r["task_completion_accuracy"] for r in rows) / n,
        "cases": rows,
    }
    result["deepeval"] = compute_deepeval_metrics(samples=rows)
    return result

