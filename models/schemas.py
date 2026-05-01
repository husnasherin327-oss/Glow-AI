from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_history: List[ChatMessage] = Field(default_factory=list)
    skin_profile: Dict[str, Any] = Field(default_factory=dict)
    api_key: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "My skin is dry and I have acne on my cheeks",
                "conversation_history": [],
                "skin_profile": {}
            }
        }
    }


class KeyIngredient(BaseModel):
    name: str
    benefit: str


class ReviewSummary(BaseModel):
    positive: str
    negative: str


class BuyLink(BaseModel):
    store: str
    url: str


class ProductCard(BaseModel):
    name: str = "Unknown Product"
    brand: str = "Expert Choice"
    category: str = "Skincare"
    price_range: Optional[str] = None
    rating: Optional[str] = None
    key_ingredients: List[KeyIngredient] = []
    merits: List[str] = []
    demerits: List[str] = []
    review_summary: Optional[ReviewSummary] = None
    suitability_score: Optional[str] = None
    buy_links: List[BuyLink] = []


class SkinAnalysis(BaseModel):
    profile_summary: Optional[str] = None
    good_ingredients: List[str] = []
    avoid_ingredients: List[str] = []


class ChatResponse(BaseModel):
    type: str  # "chat" | "products" | "error"
    message: str
    skin_profile: Dict[str, Any] = {}
    skin_analysis: Optional[SkinAnalysis] = None
    products: Optional[List[ProductCard]] = None
