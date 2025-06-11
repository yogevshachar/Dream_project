import os
import asyncio
from aio_pika import connect_robust
from aio_pika.abc import AbstractIncomingMessage
from parser import ps, tasklist
from models import NormalizedProcess
from database import SessionLocal, Base, engine
from sqlalchemy.orm import Session
from datetime import datetime

Base.metadata.create_all(bind=engine)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_NAME = "process_input"

def get_parser(os_type: str, command: str):
    if os_type.lower().startswith("win") and "tasklist" in command.lower():
        return tasklist.parse_tasklist
    elif "ps" in command.lower():
        return ps.parse_ps
    return lambda _: []

def save_all(db_data):
    db: Session = SessionLocal()
    db.bulk_save_objects(db_data)
    db.commit()
    db.close()

async def handle_message(msg: AbstractIncomingMessage):
    async with msg.process():
        headers = msg.headers or {}
        raw_output = msg.body.decode("utf-8")

        os_type = headers.get("os", "unknown")
        command = headers.get("command", "")
        parser = get_parser(os_type, command)

        parsed_entries = parser(raw_output)

        objects = [
            NormalizedProcess(
                timestamp=datetime.fromisoformat(headers["timestamp"]),
                machine_id=headers.get("machine_id"),
                machine_name=headers.get("machine_name"),
                os=os_type,
                process_name=entry["process_name"],
                pid=entry["pid"],
                memory_kb=entry["memory_kb"]
            )
            for entry in parsed_entries
        ]

        if objects:
            save_all(objects)
            print(f"✅ Normalized {len(objects)} entries from {headers.get('machine_id')}")
        else:
            print(f"⚠️ No valid entries for {headers.get('machine_id')}")

async def consume():
    conn = await connect_robust(host=RABBITMQ_HOST,port=5672)
    channel = await conn.channel()
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    await queue.consume(handle_message)
    print(f"🧠 Normalizer listening on '{QUEUE_NAME}'...")
    return conn

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume())
    loop.run_forever()
