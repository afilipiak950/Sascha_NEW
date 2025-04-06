from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Erstelle eine asynchrone Sessionmaker-Instanz
async_session = sessionmaker(
    class_=AsyncSession,
    expire_on_commit=False
) 