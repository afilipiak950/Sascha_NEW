from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, ForeignKey, Enum, Boolean
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
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    hashtags = Column(JSON, nullable=True)  # Liste von Hashtags
    status = Column(String(50), default="draft")  # draft, published, failed
    linkedin_post_id = Column(String(255), nullable=True)
    engagement_metrics = Column(JSON, nullable=True)  # Likes, Kommentare, etc.
    scheduled_for = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # LinkedIn-spezifische Felder
    scheduled_time = Column(String)  # ISO Format
    
    # Metadaten
    ai_generated = Column(Boolean, default=False)
    ai_prompt = Column(Text)  # Der verwendete Prompt für die KI-Generierung

    # Beziehungen
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="posts")
    interactions = relationship("Interaction", back_populates="post") 