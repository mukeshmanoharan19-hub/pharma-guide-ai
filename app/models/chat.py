from pydantic import BaseModel, Field

class ProductSuggestion(BaseModel):
    name: str
    description: str
    sku: str
    price: float
    image_url: str | None = None


class ChatResponse(BaseModel):
    answer: str
    productsSuggestions: list[ProductSuggestion] = Field(description="List of product suggestions related to the user's query. This field is optional and may be empty if no relevant products are found.")