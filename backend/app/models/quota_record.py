from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.database import Base

class QuotaRecord(Base):
    __tablename__ = "quota_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(String(20), nullable=False)
    trade_type = Column(String(10), nullable=False, default="买入")
    quantity = Column(Numeric(18, 6), nullable=False, default=0)
    price = Column(Numeric(14, 2), nullable=False, default=0)
    total_amount = Column(Numeric(14, 2), nullable=False, default=0)
    market = Column(String(50), nullable=False, default="全国碳市场")
    remark = Column(String(500), nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<QuotaRecord(id={self.id}, type='{self.trade_type}')>"
