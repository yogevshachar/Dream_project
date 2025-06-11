from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict

class MetadataSchema(BaseModel):
    timestamp: datetime
    machine_id: str
    machine_name: str
    os: str
    command: str
    extra: Optional[Dict[str, str]] = None
