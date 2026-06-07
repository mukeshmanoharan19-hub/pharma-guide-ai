"""Medicine catalog tools.

Each core function is decorated with :func:`with_tool_handling` (logging +
retry) and returns a Pydantic output model, raising :class:`ToolException` on
invalid input or missing data. ``build_medicine_tools`` exposes them as
LangChain ``StructuredTool`` instances bound to a DB session.
"""

from __future__ import annotations

from typing import List

from langchain_core.tools import StructuredTool
from sqlalchemy.orm import Session

from app.models.medicine import Medicine
from app.services import medicine_service
from app.tools.base import ToolException, safe_call, with_tool_handling
from app.tools.schemas import (
    AlternativeMedicineInput,
    AlternativeMedicineOutput,
    MedicineSummary,
    ProductDetailsInput,
    ProductDetailsOutput,
    SearchMedicineInput,
    SearchMedicineOutput,
    StockAvailabilityInput,
    StockAvailabilityOutput,
)


def _to_summary(medicine: Medicine) -> MedicineSummary:
    return MedicineSummary(
        sku=medicine.sku,
        title=medicine.title,
        final_price=medicine_service.price_for(medicine),
        prescription_req=medicine.prescription_req,
        dosage_form=medicine.dosage_form,
    )


@with_tool_handling("search_medicine")
def search_medicine(
    db: Session, query: str, limit: int = 5
) -> SearchMedicineOutput:
    if not query or not query.strip():
        raise ToolException("query must not be empty.")
    medicines = medicine_service.search_medicines(db, query, limit)
    results = [_to_summary(m) for m in medicines]
    return SearchMedicineOutput(results=results, count=len(results))


@with_tool_handling("alternative_medicine")
def alternative_medicine(
    db: Session, sku: str, limit: int = 5
) -> AlternativeMedicineOutput:
    medicine = medicine_service.get_by_sku(db, sku)
    if medicine is None:
        raise ToolException(f"No medicine found for sku '{sku}'.")
    alternatives = medicine_service.find_alternatives(db, medicine, limit)
    summaries: List[MedicineSummary] = [_to_summary(m) for m in alternatives]
    return AlternativeMedicineOutput(
        reference_sku=sku, alternatives=summaries, count=len(summaries)
    )


@with_tool_handling("stock_availability")
def stock_availability(db: Session, sku: str) -> StockAvailabilityOutput:
    medicine = medicine_service.get_by_sku(db, sku)
    if medicine is None:
        raise ToolException(f"No medicine found for sku '{sku}'.")
    in_stock, quantity = medicine_service.stock_for(medicine)
    return StockAvailabilityOutput(
        sku=sku, in_stock=in_stock, available_quantity=quantity
    )


@with_tool_handling("product_details")
def product_details(db: Session, sku: str) -> ProductDetailsOutput:
    medicine = medicine_service.get_by_sku(db, sku)
    if medicine is None:
        raise ToolException(f"No medicine found for sku '{sku}'.")
    in_stock, _ = medicine_service.stock_for(medicine)
    return ProductDetailsOutput(
        sku=medicine.sku,
        title=medicine.title,
        description=medicine.description,
        compositions=medicine.compositions,
        salt_type=medicine.salt_type,
        dosage_form=medicine.dosage_form,
        final_price=medicine_service.price_for(medicine),
        maximum_retail_price=medicine.maximum_retail_price,
        prescription_req=medicine.prescription_req,
        in_stock=in_stock,
    )


def build_medicine_tools(db: Session) -> List[StructuredTool]:
    """Return the medicine tools bound to a DB session for agent use."""
    return [
        StructuredTool.from_function(
            name="search_medicine",
            description=(
                "Search the medicine catalog by name, composition, or salt. "
                "Returns matching products with price and prescription flag."
            ),
            args_schema=SearchMedicineInput,
            func=lambda query, limit=5: safe_call(
                search_medicine, db=db, query=query, limit=limit
            ),
        ),
        StructuredTool.from_function(
            name="alternative_medicine",
            description=(
                "Find alternative medicines that share the same composition or "
                "salt as the given SKU."
            ),
            args_schema=AlternativeMedicineInput,
            func=lambda sku, limit=5: safe_call(
                alternative_medicine, db=db, sku=sku, limit=limit
            ),
        ),
        StructuredTool.from_function(
            name="stock_availability",
            description="Check whether a medicine SKU is in stock.",
            args_schema=StockAvailabilityInput,
            func=lambda sku: safe_call(stock_availability, db=db, sku=sku),
        ),
        StructuredTool.from_function(
            name="product_details",
            description="Fetch full product details for a medicine SKU.",
            args_schema=ProductDetailsInput,
            func=lambda sku: safe_call(product_details, db=db, sku=sku),
        ),
    ]
