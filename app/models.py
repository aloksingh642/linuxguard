from sqlalchemy import Column, Integer, Float, DateTime, String
from sqlalchemy.orm import declarative_base
from datetime import datetime


Base = declarative_base()


class Scan(Base):

    __tablename__ = "scans"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)

    total_size = Column(Float)
    used_size = Column(Float)
    free_size = Column(Float)
    usage_percent = Column(Float)
class CleanupAction(Base):

    __tablename__ = "cleanup_actions"

    id = Column(Integer, primary_key=True)
    file_path = Column(String)
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.now)
    status = Column(String)
