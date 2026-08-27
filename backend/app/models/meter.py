from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime
from app.database import Base

class Meter(Base):
    __tablename__ = "meters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    energy_type_id = Column(Integer, nullable=False)
    unit_id = Column(Integer, nullable=False)
    meter_type = Column(String(50), nullable=False, default="")
    installation_location = Column(String(200), nullable=False, default="")
    rated_voltage = Column(String(50), nullable=False, default="")
    current_ratio = Column(String(50), nullable=False, default="")
    voltage_ratio = Column(String(50), nullable=False, default="")
    accuracy = Column(String(20), nullable=False, default="")
    install_date = Column(String(20), nullable=False, default="")
    is_active = Column(Boolean, nullable=False, default=True)
    remark = Column(String(500), nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<Meter(id={self.id}, name='{self.name}')>"
