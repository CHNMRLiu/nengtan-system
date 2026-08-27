from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.database import Base

class ProductFootprint(Base):
    __tablename__ = "product_footprints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, nullable=False, index=True)
    functional_unit = Column(String(50), nullable=False, default="")
    boundary = Column(String(50), nullable=False, default="从摇篮到大门")
    raw_material = Column(Numeric(18, 6), nullable=False, default=0)
    production = Column(Numeric(18, 6), nullable=False, default=0)
    transport = Column(Numeric(18, 6), nullable=False, default=0)
    use_phase = Column(Numeric(18, 6), nullable=False, default=0)
    disposal = Column(Numeric(18, 6), nullable=False, default=0)
    total = Column(Numeric(18, 6), nullable=False, default=0)
    assessment_date = Column(String(20), nullable=False, default="")
    data_source = Column(String(500), nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<ProductFootprint(id={self.id}, product_id={self.product_id})>"
