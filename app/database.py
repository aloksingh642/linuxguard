import os

from sqlalchemy import create_engine
from app.models import Base


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///linuxguard.db"
)

engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)

print("Database initialized successfully.")
