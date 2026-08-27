from sqlalchemy import Column, Integer, String, Numeric
from app.database import Base

class EnergyFlowLink(Base):
    __tablename__ = "energy_flow_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_node_id = Column(Integer, nullable=False, index=True)
    target_node_id = Column(Integer, nullable=False, index=True)
    flow_value = Column(Numeric(14, 4), nullable=False, default=0)
    unit = Column(String(20), nullable=False, default="kWh")
    loss_rate = Column(Numeric(8, 2), nullable=False, default=0)
    remark = Column(String(500), nullable=False, default="")

    def __repr__(self):
        return f"<EnergyFlowLink(id={self.id})>"
