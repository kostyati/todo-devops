import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite://")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
