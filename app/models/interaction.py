from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class InteractionType(str, Enum):
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)  # like, comment
    target_url = Column(String(255), nullable=False)  # URL des Ziel-Posts
    content = Column(Text, nullable=True)  # Kommentartext, falls vorhanden
    status = Column(String(50), default="pending")  # pending, success, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Optional: Beziehung zum Post, falls es sich um eine Interaktion mit einem eigenen Post handelt
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    post = relationship("Post", back_populates="interactions") 