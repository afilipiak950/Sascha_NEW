from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base

class InteractionType(str, enum.Enum):
    LIKE = "like"
    COMMENT = "comment"
    CONNECTION = "connection"
    MESSAGE = "message"
    SHARE = "share"

class InteractionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(InteractionType))
    status = Column(Enum(InteractionStatus), default=InteractionStatus.PENDING)
    target_id = Column(String)  # LinkedIn ID des Ziels
    target_name = Column(String)  # Name des Ziels
    target_title = Column(String)  # Titel/Position des Ziels
    content = Column(String, nullable=True)  # Für Kommentare und Nachrichten
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Beziehungen
    user = relationship("User", back_populates="interactions")
    post = relationship("Post", back_populates="interactions") 