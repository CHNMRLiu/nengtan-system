from sqlalchemy import Column, Integer, String, Numeric
from app.database import Base

class EnergyBudget(Base):
    __tablename__ = "energy_budgets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=True)
    energy_type_id = Column(Integer, nullable=False)
    unit_id = Column(Integer, nullable=False)
    budget_value = Column(Numeric(14, 4), nullable=False, default=0)
    actual_value = Column(Numeric(14, 4), nullable=False, default=0)
    unit_consumption = Column(Numeric(14, 4), nullable=False, default=0)
    planned_output = Column(Numeric(14, 4), nullable=False, default=0)
    source_type = Column(String(20), nullable=False, default="手工填写")
    remark = Column(String(500), nullable=False, default="")

    def __repr__(self):
        return f"<EnergyBudget(id={self.id}, year={self.year})>"
