from datetime import datetime
from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, DateTime

@as_declarative()
class Base:
    id: Any
    __name__: str
    
    # Generiere Tabellennamen automatisch
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    # Gemeinsame Spalten für alle Modelle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False) 