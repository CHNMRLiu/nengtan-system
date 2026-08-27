from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.database import Base

class ProductionData(Base):
    __tablename__ = "production_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, nullable=False, index=True)
    unit_id = Column(Integer, nullable=False, index=True)
    stat_date = Column(String(20), nullable=False)
    output = Column(Numeric(14, 4), nullable=False, default=0)
    output_unit = Column(String(20), nullable=False, default="吨")
    output_value = Column(Numeric(14, 2), nullable=False, default=0)
    period = Column(String(10), nullable=False, default="月")
    remark = Column(String(500), nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<ProductionData(id={self.id}, product_id={self.product_id})>"
