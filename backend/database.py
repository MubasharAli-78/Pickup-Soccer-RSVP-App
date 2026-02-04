"""
Database configuration for the RSVP system.
Uses SQLite for simplicity - easy to deploy and no external dependencies.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database file - stored in backend directory
SQLALCHEMY_DATABASE_URL = "sqlite:///./rsvp_system.db"

# Create engine with SQLite-specific settings
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session.
    Automatically closes session when request is complete.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
