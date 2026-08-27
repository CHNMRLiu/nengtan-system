from sqlalchemy import Column, Integer, String
from app.database import Base

class SystemConfig(Base):
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True)
    config_value = Column(String(500), nullable=False, default="")
    config_group = Column(String(50), nullable=False, default="")
    description = Column(String(200), nullable=False, default="")

    def __repr__(self):
        return f"<SystemConfig(id={self.id}, key='{self.config_key}')>"
