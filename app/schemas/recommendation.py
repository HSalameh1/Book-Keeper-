from datetime import datetime

from pydantic import BaseModel

from app.schemas.item import ItemOut


class RecommendationOut(BaseModel):
    id: int
    item: ItemOut
    score: float
    reason: str | None
    generated_at: datetime
    clicked: bool
    rated: bool

    class Config:
        from_attributes = True