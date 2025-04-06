from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base

class PostStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    FAILED = "failed"

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    hashtags = Column(String)  # Als JSON-String gespeichert
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT)
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # LinkedIn-spezifische Felder
    linkedin_post_id = Column(String, unique=True)
    scheduled_time = Column(String)  # ISO Format
    
    # Metadaten
    engagement_metrics = Column(String)  # JSON als String: Likes, Kommentare, etc.
    ai_generated = Column(Boolean, default=False)
    ai_prompt = Column(Text)  # Der verwendete Prompt für die KI-Generierung

    # Beziehungen
    user = relationship("User", back_populates="posts")
    interactions = relationship("Interaction", back_populates="post") 