from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Automatisierungseinstellungen
    post_frequency = Column(Integer, default=3)  # Posts pro Woche
    daily_connection_limit = Column(Integer, default=39)
    interaction_interval = Column(Integer, default=60)  # Minuten zwischen Interaktionen
    auto_publish_posts = Column(Boolean, default=False)
    auto_approve_comments = Column(Boolean, default=False)
    
    # Zielgruppeneinstellungen
    target_industries = Column(JSON)  # Liste der Zielindustrien
    target_locations = Column(JSON)  # Liste der Zielstandorte
    target_company_sizes = Column(JSON)  # Liste der Zielunternehmensgrößen
    target_positions = Column(JSON)  # Liste der Zielpositionen
    target_seniority = Column(JSON)  # Liste der Zielsenioritätsstufen
    
    # Keyword-Einstellungen
    target_keywords = Column(JSON)  # Liste der Zielkeywords
    excluded_keywords = Column(JSON)  # Liste der ausgeschlossenen Keywords
    
    # Interaktionstypen
    interaction_types = Column(JSON)  # Liste der aktivierten Interaktionstypen
    
    # Beitragseinstellungen
    post_topics = Column(JSON)  # Liste der Beitragsthemen
    post_tones = Column(JSON)  # Liste der Beitragstöne
    post_lengths = Column(JSON)  # Liste der Beitragslängen
    post_hashtags = Column(JSON)  # Liste der Hashtags
    
    # Nachrichtenvorlagen
    message_templates = Column(JSON)  # Vorlagen für verschiedene Nachrichtentypen
    
    # Benachrichtigungseinstellungen
    notification_settings = Column(JSON)  # Benachrichtigungseinstellungen
    
    # Proxy-Einstellungen
    proxy_settings = Column(JSON)  # Proxy-Konfiguration
    
    # Browser-Einstellungen
    browser_settings = Column(JSON)  # Browser-Konfiguration
    
    # Rate-Limiting
    rate_limits = Column(JSON)  # Rate-Limiting-Einstellungen
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Beziehungen
    user = relationship("User", back_populates="settings") 