from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_id = Column(
        Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    score = Column(Float, nullable=False)
    reason = Column(String, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    clicked = Column(Boolean, default=False, nullable=False)
    rated = Column(Boolean, default=False, nullable=False)

    item = relationship("Item")

    __table_args__ = (
        UniqueConstraint("user_id", "item_id", name="uq_user_recommendation"),
    )