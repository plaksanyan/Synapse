from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    created_at: datetime
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
class DeckCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    settings: dict = Field(default_factory=dict)
class DeckUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    settings: dict | None = None
class DeckOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    name: str
    settings: dict
    created_at: datetime
class CardCreate(BaseModel):
    front: str = Field(min_length=1)
    back: str = Field(min_length=1)
    format: Literal["text", "markdown", "cloze"] = "text"
class CardUpdate(BaseModel):
    front: str | None = Field(default=None, min_length=1)
    back: str | None = Field(default=None, min_length=1)
    format: Literal["text", "markdown", "cloze"] | None = None
class CardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    deck_id: int
    front: str
    back: str
    format: str
    created_at: datetime
class ImportRequest(BaseModel):
    text: str = Field(min_length=1)
    format: str | None = None
class ReviewCreate(BaseModel):
    card_id: int
    rating: int = Field(ge=1, le=4)
    response_time_ms: int = Field(ge=0)
class ReviewOut(BaseModel):
    card_id: int
    w: float
    lambda_forget: float
    last_reviewed_at: datetime
    next_review_at: datetime
    interval_days: float
class SyncOut(BaseModel):
    since: datetime
    decks: list[DeckOut]
    cards: list[CardOut]
    weights: list[dict]
    reviews: list[dict]
