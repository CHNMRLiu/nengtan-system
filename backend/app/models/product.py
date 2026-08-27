from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    unit = Column(String(20), nullable=False, default="吨")
    output_unit = Column(String(20), nullable=False, default="吨")
    is_active = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}')>"
