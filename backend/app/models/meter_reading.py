from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.database import Base

class MeterReading(Base):
    __tablename__ = "meter_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    meter_id = Column(Integer, nullable=False, index=True)
    reading_time = Column(String(20), nullable=False)
    last_reading = Column(Numeric(14, 4), nullable=False, default=0)
    current_reading = Column(Numeric(14, 4), nullable=False, default=0)
    consumption = Column(Numeric(14, 4), nullable=False, default=0)
    unit_price = Column(Numeric(14, 2), nullable=False, default=0)
    cost = Column(Numeric(14, 2), nullable=False, default=0)
    standard_coal = Column(Numeric(14, 4), nullable=False, default=0)
    carbon_emission = Column(Numeric(18, 6), nullable=False, default=0)
    recorder = Column(String(50), nullable=False, default="")
    remark = Column(String(500), nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<MeterReading(id={self.id}, meter_id={self.meter_id})>"
