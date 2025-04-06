from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.models.base import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_url = Column(String(255), nullable=False)
    hashtag = Column(String(100), nullable=False)  # Der Hashtag, durch den der Post gefunden wurde
    content = Column(Text, nullable=False)  # Der Kommentartext
    status = Column(String(50), default="pending")  # pending, success, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 