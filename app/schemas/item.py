from datetime import datetime

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    creator: str | None = None
    type: str = Field(pattern="^(book|manga|comic)$")
    description: str | None = None
    tags: list[str] = []


class TagOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ItemOut(BaseModel):
    id: int
    title: str
    creator: str | None
    type: str
    description: str | None
    created_at: datetime
    tags: list[TagOut] = []

    class Config:
        from_attributes = True