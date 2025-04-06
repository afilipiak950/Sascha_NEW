from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base

class ContactStatus(str, enum.Enum):
    PENDING = "pending"
    CONNECTED = "connected"
    FOLLOWING = "following"
    REJECTED = "rejected"
    FAILED = "failed"

class TargetContact(Base):
    id = Column(Integer, primary_key=True, index=True)
    profile_url = Column(String, unique=True, nullable=False)
    name = Column(String)
    title = Column(String)
    company = Column(String)
    location = Column(String)
    status = Column(Enum(ContactStatus), default=ContactStatus.PENDING)
    
    # Suchkriterien
    keywords = Column(String)  # Komma-getrennte Keywords
    industry = Column(String)
    connection_degree = Column(String)  # 1st, 2nd, 3rd
    
    # Beziehungen
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="target_contacts")
    
    # Metadaten
    last_contact_attempt = Column(String)  # ISO Format
    error_message = Column(Text)
    notes = Column(Text)  # Für manuelle Notizen 