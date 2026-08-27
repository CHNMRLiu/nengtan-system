from sqlalchemy import Column, Integer, String, Numeric, Boolean
from app.database import Base

class CarbonFactor(Base):
    __tablename__ = "carbon_factors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    factor_value = Column(Numeric(14, 6), nullable=False, default=0)
    unit = Column(String(50), nullable=False, default="")
    source = Column(String(200), nullable=False, default="")
    effective_date = Column(String(20), nullable=False, default="")
    is_active = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<CarbonFactor(id={self.id}, name='{self.name}')>"
