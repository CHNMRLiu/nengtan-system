from sqlalchemy import Column, Integer, String, Numeric, Boolean
from app.database import Base

class EnergyType(Base):
    __tablename__ = "energy_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    unit = Column(String(20), nullable=False)
    standard_coal_coefficient = Column(Numeric(10, 4), nullable=False, default=0)
    carbon_factor = Column(Numeric(14, 6), nullable=False, default=0)
    default_price = Column(Numeric(14, 2), nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<EnergyType(id={self.id}, name='{self.name}')>"
