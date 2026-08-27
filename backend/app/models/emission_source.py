from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class EmissionSource(Base):
    __tablename__ = "emission_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    scope = Column(String(20), nullable=False, default="范围1")
    category = Column(String(50), nullable=False, default="")
    carbon_factor_id = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)
    remark = Column(String(500), nullable=False, default="")

    def __repr__(self):
        return f"<EmissionSource(id={self.id}, name='{self.name}')>"
