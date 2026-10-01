from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user
from app.database import get_db
from app.models.item import Item
from app.models.recommendation import Recommendation
from app.models.user import User
from app.schemas.recommendation import RecommendationOut
from app.services import recommender

router = APIRouter(prefix="/me/recommendations", tags=["recommendations"])


@router.get("", response_model=list[RecommendationOut])
def get_my_recommendations(
    refresh: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns cached recommendations. Pass ?refresh=true to regenerate
    from the current library state.
    """
    if refresh:
        # Wipe old recommendations for this user and regenerate
        db.query(Recommendation).filter(
            Recommendation.user_id == current_user.id
        ).delete()

        scored = recommender.generate_recommendations(db, current_user.id)

        for item, score, reason in scored:
            db.add(
                Recommendation(
                    user_id=current_user.id,
                    item_id=item.id,
                    score=score,
                    reason=reason,
                )
            )
        db.commit()

    return (
        db.query(Recommendation)
        .options(joinedload(Recommendation.item).joinedload(Item.tags))
        .filter(Recommendation.user_id == current_user.id)
        .order_by(Recommendation.score.desc())
        .all()
    )


@router.post("/{rec_id}/click", response_model=RecommendationOut)
def mark_clicked(
    rec_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rec = (
        db.query(Recommendation)
        .filter(
            Recommendation.id == rec_id,
            Recommendation.user_id == current_user.id,
        )
        .first()
    )
    if rec is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.clicked = True
    db.commit()
    db.refresh(rec)
    return rec