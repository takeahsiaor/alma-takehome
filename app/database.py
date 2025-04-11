import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, DateTime, String
from sqlalchemy.orm import sessionmaker, declarative_base


SQLALCHEMY_DATABASE_URL = "sqlite:///./leads.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Default primary keys to be uuids instead of ints
class UuidBase:
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Future enhancement to modify the default query manager wrapper to respect soft deletes by default
    deleted_at = Column(DateTime, nullable=True)


Base = declarative_base(cls=UuidBase)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
