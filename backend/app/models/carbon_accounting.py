from sqlalchemy import Column, Integer, String, Numeric
from app.database import Base

class CarbonAccounting(Base):
    __tablename__ = "carbon_accounting"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False)
    activity_data = Column(Numeric(18, 6), nullable=False, default=0)
    unit = Column(String(20), nullable=False, default="")
    emission_factor = Column(Numeric(14, 6), nullable=False, default=0)
    emission = Column(Numeric(18, 6), nullable=False, default=0)
    data_source = Column(String(50), nullable=False, default="手工录入")
    remark = Column(String(500), nullable=False, default="")

    def __repr__(self):
        return f"<CarbonAccounting(id={self.id}, year={self.year}, month={self.month})>"
