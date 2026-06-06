from pydantic import BaseModel

class ProductSuggestion(BaseModel):
    name: str
    description: str
    sku: str
    price: float
    image_url: str | None = None


class ChatResponse(BaseModel):
    answer: str
    productsSuggestions: list[ProductSuggestion] = []