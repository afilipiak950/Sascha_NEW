from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from app.models.base import Base

class Connection(Base):
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True)
    profile_url = Column(String(255), nullable=False, unique=True)
    message = Column(Text, nullable=True)  # Verbindungsanfrage-Nachricht
    status = Column(String(50), default="pending")  # pending, sent, accepted, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    
    # Follow-up Tracking
    follow_up_sent = Column(Boolean, default=False)
    follow_up_message = Column(Text, nullable=True)
    follow_up_sent_at = Column(DateTime, nullable=True) 