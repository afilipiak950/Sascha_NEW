from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import aiosqlite

# Bestimme den Datenbanktyp
is_sqlite = "sqlite" in settings.SQLALCHEMY_DATABASE_URI

if is_sqlite:
    # SQLite Engine (nicht async)
    from sqlalchemy import create_engine
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True,
        echo=True,
        connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # Async Session für Kompatibilität (wird nicht wirklich async sein)
    async_session = SessionLocal
    
    async def get_async_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

else:
    # PostgreSQL Async Engine
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

    async def get_async_db():
        async with async_session() as session:
            try:
                yield session
            finally:
                await session.close()

    # Sync Engine für Kompatibilität
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