from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, default="")
    credit_code = Column(String(50), nullable=False, default="")
    industry = Column(String(100), nullable=False, default="")
    address = Column(String(300), nullable=False, default="")
    contact = Column(String(50), nullable=False, default="")
    phone = Column(String(20), nullable=False, default="")
    scale = Column(String(50), nullable=False, default="")
    established_date = Column(String(20), nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}')>"
