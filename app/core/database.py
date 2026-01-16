"""
Database setup and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

from app.core.config import settings

Base = declarative_base()

# Ensure the data directory exists before creating engine
if "sqlite" in settings.database_url and ":memory:" not in settings.database_url:
    db_path = settings.database_url.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

# Database setup
engine = create_engine(
    settings.database_url,
    connect_args=(
        {"check_same_thread": False}
        if (
            "sqlite" in settings.database_url
            and ":memory:" not in settings.database_url
        )
        else {}
    ),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all tables in the database."""
    # Import all models to ensure they're registered with Base
    from app.models import Account, Transaction, User, Card  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
