from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    username = Column(String(50), nullable=False, default="")
    module = Column(String(50), nullable=False, default="")
    action = Column(String(50), nullable=False, default="")
    ip = Column(String(50), nullable=False, default="")
    user_agent = Column(String(500), nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<OperationLog(id={self.id}, module='{self.module}')>"
