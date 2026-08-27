from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.database import Base

class CarbonAsset(Base):
    __tablename__ = "carbon_assets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_type = Column(String(20), nullable=False, default="配额")
    year = Column(Integer, nullable=False, index=True)
    project_name = Column(String(200), nullable=False, default="")
    quantity = Column(Numeric(18, 6), nullable=False, default=0)
    used_quantity = Column(Numeric(18, 6), nullable=False, default=0)
    acquisition_date = Column(String(20), nullable=False, default="")
    expiry_date = Column(String(20), nullable=False, default="")
    status = Column(String(20), nullable=False, default="有效")
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<CarbonAsset(id={self.id}, type='{self.asset_type}')>"
