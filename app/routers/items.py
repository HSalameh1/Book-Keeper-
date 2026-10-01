from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.item import Item, Tag
from app.schemas.item import ItemCreate, ItemOut

router = APIRouter(prefix="/items", tags=["items"])


def _get_or_create_tags(db: Session, tag_names: list[str]) -> list[Tag]:
    tags: list[Tag] = []
    for raw in tag_names:
        name = raw.strip().lower()
        if not name:
            continue
        tag = db.query(Tag).filter(Tag.name == name).first()
        if tag is None:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags


@router.get("", response_model=list[ItemOut])
def list_items(
    type: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Item)
    if type:
        query = query.filter(Item.type == type)
    if q:
        query = query.filter(Item.title.ilike(f"%{q}%"))
    return query.order_by(Item.title).all()


@router.post("", response_model=ItemOut, status_code=201)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(Item)
        .filter(
            Item.title == payload.title,
            Item.creator == payload.creator,
            Item.type == payload.type,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Item already exists")

    item = Item(
        title=payload.title,
        creator=payload.creator,
        type=payload.type,
        description=payload.description,
    )
    item.tags = _get_or_create_tags(db, payload.tags)

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item