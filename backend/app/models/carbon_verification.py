from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.database import Base

class CarbonVerification(Base):
    __tablename__ = "carbon_verifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False, index=True)
    verification_agency = Column(String(200), nullable=False, default="")
    verifier = Column(String(50), nullable=False, default="")
    start_date = Column(String(20), nullable=False, default="")
    end_date = Column(String(20), nullable=False, default="")
    reported_emission = Column(Numeric(18, 6), nullable=False, default=0)
    verified_emission = Column(Numeric(18, 6), nullable=False, default=0)
    status = Column(String(20), nullable=False, default="待核查")
    conclusion = Column(String(2000), nullable=False, default="")
    evidence_hash = Column(String(200), nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<CarbonVerification(id={self.id}, year={self.year})>"
