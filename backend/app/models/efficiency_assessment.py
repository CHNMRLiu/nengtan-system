from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.database import Base

class EfficiencyAssessment(Base):
    __tablename__ = "efficiency_assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_id = Column(Integer, nullable=False, index=True)
    stat_date = Column(String(20), nullable=False)
    energy_consumption = Column(Numeric(14, 4), nullable=False, default=0)
    output = Column(Numeric(14, 4), nullable=False, default=0)
    actual_value = Column(Numeric(14, 4), nullable=False, default=0)
    benchmark_value = Column(Numeric(14, 4), nullable=False, default=0)
    deviation = Column(Numeric(10, 2), nullable=False, default=0)
    level = Column(String(20), nullable=False, default="")
    remark = Column(String(500), nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<EfficiencyAssessment(id={self.id}, level='{self.level}')>"
