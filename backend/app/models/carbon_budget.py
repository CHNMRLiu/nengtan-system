from sqlalchemy import Column, Integer, String, Numeric
from app.database import Base

class CarbonBudget(Base):
    __tablename__ = "carbon_budgets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=True)
    unit_id = Column(Integer, nullable=False)
    budget_carbon = Column(Numeric(18, 6), nullable=False, default=0)
    actual_carbon = Column(Numeric(18, 6), nullable=False, default=0)
    carbon_intensity = Column(Numeric(14, 6), nullable=False, default=0)
    intensity_type = Column(String(20), nullable=False, default="产值强度")
    planned_output = Column(Numeric(14, 4), nullable=False, default=0)
    remark = Column(String(500), nullable=False, default="")

    def __repr__(self):
        return f"<CarbonBudget(id={self.id}, year={self.year})>"
