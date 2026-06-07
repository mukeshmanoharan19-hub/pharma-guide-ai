"""Central registry for agent tools.

``build_all_tools`` returns every tool bound to the request context (DB session
and user). Specialized agents in later phases select subsets by name via
``TOOL_CATALOG``.
"""

from __future__ import annotations

from typing import Dict, List

from langchain_core.tools import StructuredTool
from sqlalchemy.orm import Session

from app.tools.commerce_tools import build_commerce_tools
from app.tools.medicine_tools import build_medicine_tools
from app.tools.user_tools import build_user_tools

# Tool names grouped by domain, for agent-to-tool wiring in later phases.
TOOL_CATALOG: Dict[str, List[str]] = {
    "medicine": [
        "search_medicine",
        "alternative_medicine",
        "stock_availability",
        "product_details",
    ],
    "commerce": [
        "add_to_cart",
        "remove_from_cart",
        "update_cart",
        "view_cart",
        "create_order",
        "order_status",
    ],
    "user": [
        "user_profile",
        "purchase_history",
    ],
}


def build_all_tools(db: Session, user_id: int) -> List[StructuredTool]:
    """Build every tool bound to the given DB session and user."""
    return [
        *build_medicine_tools(db),
        *build_commerce_tools(db, user_id),
        *build_user_tools(db, user_id),
    ]


def build_tools_by_names(
    db: Session, user_id: int, names: List[str]
) -> List[StructuredTool]:
    """Build only the named tools (used by specialized agents)."""
    wanted = set(names)
    return [t for t in build_all_tools(db, user_id) if t.name in wanted]


def get_tool_map(db: Session, user_id: int) -> Dict[str, StructuredTool]:
    """Return a name -> tool mapping for direct invocation."""
    return {t.name: t for t in build_all_tools(db, user_id)}
