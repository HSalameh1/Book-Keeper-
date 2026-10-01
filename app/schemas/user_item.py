from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.item import ItemOut


class UserItemCreate(BaseModel):
    item_id: int
    rating: int | None = Field(default=None, ge=1, le=5)
    note: str | None = None
    status: str = Field(
        default="finished",
        pattern="^(want_to_read|reading|finished|dropped)$",
    )


class UserItemUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    note: str | None = None
    status: str | None = Field(
        default=None,
        pattern="^(want_to_read|reading|finished|dropped)$",
    )


class UserItemOut(BaseModel):
    id: int
    item_id: int
    rating: int | None
    note: str | None
    status: str
    created_at: datetime
    item: ItemOut

    class Config:
        from_attributes = True