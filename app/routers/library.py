from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.item import Item
from app.models.user import User
from app.models.user_item import UserItem
from app.schemas.user_item import UserItemCreate, UserItemOut, UserItemUpdate

router = APIRouter(prefix="/me/library", tags=["library"])


@router.get("", response_model=list[UserItemOut])
def list_my_library(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(UserItem)
        .filter(UserItem.user_id == current_user.id)
        .order_by(UserItem.created_at.desc())
        .all()
    )


@router.post("", response_model=UserItemOut, status_code=201)
def add_to_library(
    payload: UserItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.query(Item).filter(Item.id == payload.item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    existing = (
        db.query(UserItem)
        .filter(
            UserItem.user_id == current_user.id,
            UserItem.item_id == payload.item_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Item already in library")

    entry = UserItem(
        user_id=current_user.id,
        item_id=payload.item_id,
        rating=payload.rating,
        note=payload.note,
        status=payload.status,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.patch("/{entry_id}", response_model=UserItemOut)
def update_library_entry(
    entry_id: int,
    payload: UserItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entry = (
        db.query(UserItem)
        .filter(
            UserItem.id == entry_id,
            UserItem.user_id == current_user.id,
        )
        .first()
    )
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")

    if payload.rating is not None:
        entry.rating = payload.rating
    if payload.note is not None:
        entry.note = payload.note
    if payload.status is not None:
        entry.status = payload.status

    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=204)
def delete_library_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entry = (
        db.query(UserItem)
        .filter(
            UserItem.id == entry_id,
            UserItem.user_id == current_user.id,
        )
        .first()
    )
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")

    db.delete(entry)
    db.commit()