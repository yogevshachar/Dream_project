from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from database import Base

class NormalizedProcess(Base):
    __tablename__ = "normalized_process_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(TIMESTAMP)
    machine_id = Column(String)
    machine_name = Column(String)
    os = Column(String)
    process_name = Column(String)
    pid = Column(Integer)
    memory_kb = Column(Float)

