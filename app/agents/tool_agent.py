"""Generic tool-calling agent loop used by the specialist agents (Phase 5).

Given an LLM, a set of bound :class:`StructuredTool` instances, and a system
prompt, this runs a bounded reason→act loop:

    1. Ask the LLM (with tools bound). If it requests tool calls, execute them
       and feed the results back as ToolMessages.
    2. Repeat until the LLM responds without tool calls or the iteration cap is
       hit (in which case we ask for a plain-language wrap-up).

It also harvests product suggestions from catalog tool results so the response
payload can surface them to the UI.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from loguru import logger

MAX_AGENT_ITERATIONS = 5

# Tool results we can mine for product suggestions.
_PRODUCT_LIST_KEYS = {
    "search_medicine": "results",
    "alternative_medicine": "alternatives",
}


def _summary_to_product(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "sku": item.get("sku"),
        "title": item.get("title"),
        "price": item.get("final_price"),
        "prescription_req": item.get("prescription_req"),
        "dosage_form": item.get("dosage_form"),
    }


def _extract_products(tool_outputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Collect de-duplicated product suggestions from catalog tool results."""
    products: List[Dict[str, Any]] = []
    seen = set()

    def _add(item: Dict[str, Any]) -> None:
        product = _summary_to_product(item)
        key = product.get("sku") or product.get("title")
        if key and key not in seen:
            seen.add(key)
            products.append(product)

    for entry in tool_outputs:
        result = entry.get("result") or {}
        if not isinstance(result, dict) or not result.get("success"):
            continue
        data = result.get("data") or {}
        name = entry.get("name")

        list_key = _PRODUCT_LIST_KEYS.get(name)
        if list_key and isinstance(data.get(list_key), list):
            for item in data[list_key]:
                if isinstance(item, dict):
                    _add(item)
        elif name == "product_details" and isinstance(data, dict) and data.get("title"):
            _add(data)

    return products


def _invoke_tool(tool, args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return tool.invoke(args or {})
    except Exception as exc:  # tools normally self-wrap; this is defensive
        logger.exception(f"[tool:{getattr(tool, 'name', '?')}] invocation error: {exc}")
        return {"success": False, "error": str(exc)}


def run_tool_agent(
    *,
    llm,
    tools: List,
    system_prompt: str,
    query: str,
    history_text: Optional[str] = None,
    summary_text: Optional[str] = None,
    max_iterations: int = MAX_AGENT_ITERATIONS,
) -> Dict[str, Any]:
    """Run the tool-calling loop and return answer + tool_outputs + products."""
    tool_map = {t.name: t for t in tools}
    llm_with_tools = llm.bind_tools(tools) if tools else llm

    system = system_prompt.format(
        summary=summary_text or "None.",
        history=history_text or "None.",
    )
    messages: List[Any] = [SystemMessage(content=system), HumanMessage(content=query)]

    tool_outputs: List[Dict[str, Any]] = []
    final_text = ""

    for _ in range(max_iterations):
        ai: AIMessage = llm_with_tools.invoke(messages)
        messages.append(ai)

        tool_calls = getattr(ai, "tool_calls", None) or []
        if not tool_calls:
            final_text = ai.content if isinstance(ai.content, str) else str(ai.content)
            break

        for call in tool_calls:
            name = call.get("name")
            args = call.get("args", {}) or {}
            call_id = call.get("id")

            tool = tool_map.get(name)
            if tool is None:
                result: Dict[str, Any] = {
                    "success": False,
                    "error": f"Unknown tool '{name}'.",
                }
            else:
                result = _invoke_tool(tool, args)

            tool_outputs.append({"name": name, "args": args, "result": result})
            messages.append(
                ToolMessage(
                    content=json.dumps(result, default=str),
                    tool_call_id=call_id,
                )
            )
    else:
        # Iteration budget exhausted: ask for a plain-language wrap-up, no tools.
        try:
            wrap = llm.invoke(
                messages
                + [
                    HumanMessage(
                        content=(
                            "Summarise what you found for the user in plain "
                            "language. Do not call any more tools."
                        )
                    )
                ]
            )
            final_text = wrap.content if isinstance(wrap.content, str) else str(wrap.content)
        except Exception as exc:
            logger.warning(f"Tool agent wrap-up failed: {exc}")
            final_text = "I wasn't able to fully complete that request."

    if not final_text:
        final_text = "I wasn't able to generate a response."

    return {
        "answer": final_text,
        "tool_outputs": tool_outputs,
        "products": _extract_products(tool_outputs),
    }
