from sqlalchemy import Column, Integer, String, Numeric
from app.database import Base

class SupplierCarbonData(Base):
    __tablename__ = "supplier_carbon_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, nullable=False, index=True)
    year = Column(Integer, nullable=False)
    material_name = Column(String(100), nullable=False, default="")
    quantity = Column(Numeric(14, 4), nullable=False, default=0)
    unit = Column(String(20), nullable=False, default="")
    emission_factor = Column(Numeric(14, 6), nullable=False, default=0)
    emission = Column(Numeric(18, 6), nullable=False, default=0)
    data_source = Column(String(50), nullable=False, default="默认因子")

    def __repr__(self):
        return f"<SupplierCarbonData(id={self.id}, supplier_id={self.supplier_id})>"
