from sqlalchemy import Column, Integer, String, Numeric, Boolean
from app.database import Base

class EfficiencyIndicator(Base):
    __tablename__ = "efficiency_indicators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    energy_type_id = Column(Integer, nullable=False)
    benchmark_value = Column(Numeric(14, 4), nullable=False, default=0)
    target_value = Column(Numeric(14, 4), nullable=False, default=0)
    unit = Column(String(20), nullable=False, default="")
    is_active = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<EfficiencyIndicator(id={self.id}, name='{self.name}')>"
