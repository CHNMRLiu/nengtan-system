from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.database import Base

class ManualEntry(Base):
    __tablename__ = "manual_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    energy_type_id = Column(Integer, nullable=False, index=True)
    unit_id = Column(Integer, nullable=False, index=True)
    meter_id = Column(Integer, nullable=True)
    entry_date = Column(String(20), nullable=False)
    consumption = Column(Numeric(14, 4), nullable=False, default=0)
    unit_price = Column(Numeric(14, 2), nullable=False, default=0)
    cost = Column(Numeric(14, 2), nullable=False, default=0)
    standard_coal = Column(Numeric(14, 4), nullable=False, default=0)
    carbon_emission = Column(Numeric(18, 6), nullable=False, default=0)
    data_source = Column(String(50), nullable=False, default="手工录入")
    recorder = Column(String(50), nullable=False, default="")
    remark = Column(String(500), nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<ManualEntry(id={self.id})>"
