from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request, Depends
from rabbitmq import get_publisher, RabbitMQPublisher
import json
from datetime import datetime

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post(
    "/",
    summary="Ingest raw OS process output",
    description="""
Receives a file containing the raw output of an OS process listing command (e.g., `ps auxww`, `tasklist`).
Metadata is provided as individual form fields. Extra optional metadata can be passed as a JSON string.
The data is validated and published to a RabbitMQ exchange (`pre_normalise`) for processing.
""",
    response_description="Status of ingestion"
)
async def upload_process_file(
    timestamp: str = Form(description="ISO timestamp of when the command was executed (YYYY-MM-DD HH:MM:SS.mmmmmm)",default='2025-06-09T15:00:00Z'),
    os: str = Form( description="Operating system name (e.g., 'linux', 'windows', 'macos')",default="linux"),
    command: str = Form( description="Command used to generate the output (e.g., 'ps auxww')",default="ps auxww"),
    machine_id: str = Form( description="Unique machine identifier"),
    machine_name: str = Form( description="Human-readable machine name",default="unknown"),
    extra: str = Form( description="Optional JSON string of extra metadata fields",default=''),
    file: UploadFile = File(..., description="Text file containing raw output of a process list command"),
    request: Request = None,
    publisher: RabbitMQPublisher = Depends(get_publisher)
):
    """
    Upload a raw OS process list output file with associated metadata.
    The file and metadata will be published to RabbitMQ for downstream normalization.
    """
    try:
        parsed_timestamp = datetime.fromisoformat(timestamp)
        extra_data = json.loads(extra) if extra else {}
    except (ValueError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")

    contents = await file.read()

    headers = {
        "timestamp": parsed_timestamp.isoformat(),
        "machine_id": machine_id,
        "machine_name": machine_name,
        "os": os,
        "command": command,
        **extra_data
    }

    await publisher.publish(body=contents, headers=headers)
    return {"status": "queued"}
