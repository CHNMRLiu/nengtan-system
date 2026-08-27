from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class EnergyUnit(Base):
    __tablename__ = "energy_units"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, nullable=True)
    level = Column(Integer, nullable=False, default=1)
    area = Column(String(100), nullable=False, default="")
    responsible_person = Column(String(50), nullable=False, default="")
    phone = Column(String(20), nullable=False, default="")
    is_active = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<EnergyUnit(id={self.id}, name='{self.name}')>"
