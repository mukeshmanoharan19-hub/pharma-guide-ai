"""Structured input/output schemas for all agent tools."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

# --------------------------------------------------------------------------- #
# Inputs
# --------------------------------------------------------------------------- #


class SearchMedicineInput(BaseModel):
    query: str = Field(..., description="Free-text medicine search query.")
    limit: int = Field(5, ge=1, le=25, description="Maximum results to return.")


class AlternativeMedicineInput(BaseModel):
    sku: str = Field(..., description="SKU of the reference medicine.")
    limit: int = Field(5, ge=1, le=25)


class StockAvailabilityInput(BaseModel):
    sku: str = Field(..., description="SKU to check availability for.")


class ProductDetailsInput(BaseModel):
    sku: str = Field(..., description="SKU of the product to fetch.")


class AddToCartInput(BaseModel):
    sku: str = Field(..., description="SKU of the medicine to add.")
    quantity: int = Field(1, ge=1, description="Units to add.")


class RemoveFromCartInput(BaseModel):
    sku: str = Field(..., description="SKU of the medicine to remove.")


class UpdateCartInput(BaseModel):
    sku: str = Field(..., description="SKU of the cart line to update.")
    quantity: int = Field(
        ..., ge=0, description="New quantity (0 removes the line)."
    )


class ViewCartInput(BaseModel):
    pass


class PrepareOrderInput(BaseModel):
    pass


class ConfirmOrderInput(BaseModel):
    confirmation_id: str = Field(
        ..., description="Checkout confirmation id from `prepare_order`."
    )


class CreateOrderInput(BaseModel):
    """Deprecated compatibility schema (kept for transition)."""

    pass


class OrderStatusInput(BaseModel):
    order_id: str = Field(..., description="Order identifier (UUID).")


class UserProfileInput(BaseModel):
    pass


class PurchaseHistoryInput(BaseModel):
    limit: int = Field(10, ge=1, le=50)


# --------------------------------------------------------------------------- #
# Outputs
# --------------------------------------------------------------------------- #


class MedicineSummary(BaseModel):
    sku: Optional[str] = None
    title: str
    final_price: Optional[float] = None
    prescription_req: Optional[bool] = None
    dosage_form: Optional[str] = None


class SearchMedicineOutput(BaseModel):
    results: List[MedicineSummary]
    count: int


class AlternativeMedicineOutput(BaseModel):
    reference_sku: str
    alternatives: List[MedicineSummary]
    count: int


class StockAvailabilityOutput(BaseModel):
    sku: str
    in_stock: bool
    available_quantity: int


class ProductDetailsOutput(BaseModel):
    sku: Optional[str] = None
    title: str
    description: Optional[str] = None
    compositions: Optional[str] = None
    salt_type: Optional[str] = None
    dosage_form: Optional[str] = None
    final_price: Optional[float] = None
    maximum_retail_price: Optional[float] = None
    prescription_req: Optional[bool] = None
    in_stock: bool = True


class CartItemOut(BaseModel):
    sku: Optional[str] = None
    title: Optional[str] = None
    quantity: int
    unit_price: Optional[float] = None
    line_total: float


class CartOut(BaseModel):
    cart_id: str
    items: List[CartItemOut]
    item_count: int
    total: float


class OrderItemOut(BaseModel):
    sku: Optional[str] = None
    title: Optional[str] = None
    quantity: int
    unit_price: Optional[float] = None
    line_total: float


class OrderOut(BaseModel):
    order_id: str
    status: str
    payment_status: str
    total_amount: float
    items: List[OrderItemOut]
    created_at: Optional[str] = None


class CheckoutConfirmationOut(BaseModel):
    confirmation_id: str
    items: List[CartItemOut]
    item_count: int
    total: float
    status: str
    expires_at: Optional[str] = None


class OrderSummary(BaseModel):
    order_id: str
    status: str
    payment_status: str
    total_amount: float
    created_at: Optional[str] = None


class PurchaseHistoryOutput(BaseModel):
    orders: List[OrderSummary]
    count: int


class UserProfileOutput(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    total_orders: int
