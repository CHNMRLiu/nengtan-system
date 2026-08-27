from sqlalchemy import Column, Integer, String
from app.database import Base

class EnergyFlowNode(Base):
    __tablename__ = "energy_flow_nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    node_type = Column(String(20), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)
    remark = Column(String(500), nullable=False, default="")

    def __repr__(self):
        return f"<EnergyFlowNode(id={self.id}, name='{self.name}')>"
