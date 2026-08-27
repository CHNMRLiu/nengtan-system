from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.database import Base

class CarbonReport(Base):
    __tablename__ = "carbon_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, unique=True, nullable=False, index=True)
    total_emission = Column(Numeric(18, 6), nullable=False, default=0)
    scope1 = Column(Numeric(18, 6), nullable=False, default=0)
    scope2 = Column(Numeric(18, 6), nullable=False, default=0)
    scope3 = Column(Numeric(18, 6), nullable=False, default=0)
    intensity_value = Column(Numeric(14, 6), nullable=False, default=0)
    product_intensity = Column(Numeric(14, 6), nullable=False, default=0)
    per_capita = Column(Numeric(14, 6), nullable=False, default=0)
    measures = Column(String(2000), nullable=False, default="")
    next_plan = Column(String(2000), nullable=False, default="")
    report_date = Column(String(20), nullable=False, default="")
    status = Column(String(20), nullable=False, default="草稿")
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<CarbonReport(id={self.id}, year={self.year})>"
