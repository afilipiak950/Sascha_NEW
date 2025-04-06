from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Async Engine und Session
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=True
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Async Dependency
async def get_async_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# Sync Engine und Session für Kompatibilität
from sqlalchemy import create_engine
sync_engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI.replace("postgresql+asyncpg", "postgresql"),
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 