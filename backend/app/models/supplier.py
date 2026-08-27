from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.database import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    credit_code = Column(String(50), nullable=False, default="")
    contact_person = Column(String(50), nullable=False, default="")
    phone = Column(String(20), nullable=False, default="")
    category = Column(String(50), nullable=False, default="原材料")
    risk_level = Column(String(10), nullable=False, default="低")
    address = Column(String(300), nullable=False, default="")
    total_emission = Column(Numeric(18, 6), nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<Supplier(id={self.id}, name='{self.name}')>"
