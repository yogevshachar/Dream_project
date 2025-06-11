from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, JSON
from database import Base

class RawCommandData(Base):
    __tablename__ = "raw_command_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(TIMESTAMP)
    machine_id = Column(String)
    machine_name = Column(String)
    os = Column(String)
    command = Column(String)
    raw_output = Column(Text)
    raw_metadata = Column(JSON)
