from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class UserItem(Base):
    __tablename__ = "user_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_id = Column(
        Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rating = Column(Integer, nullable=True)
    note = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="finished")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    item = relationship("Item")

    __table_args__ = (
        UniqueConstraint("user_id", "item_id", name="uq_user_item"),
        CheckConstraint(
            "rating IS NULL OR (rating >= 1 AND rating <= 5)",
            name="ck_rating_range",
        ),
        CheckConstraint(
            "status IN ('want_to_read', 'reading', 'finished', 'dropped')",
            name="ck_status_values",
        ),
    )