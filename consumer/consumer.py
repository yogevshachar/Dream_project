import asyncio
import os

from aio_pika import connect_robust, IncomingMessage
from database import SessionLocal, Base, engine
from sqlalchemy.orm import Session
from datetime import datetime

from model import RawCommandData

QUEUE_NAME = "raw_process_input"
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

Base.metadata.create_all(bind=engine)

def save_to_db(data: RawCommandData):
    db: Session = SessionLocal()
    db.add(data)
    db.commit()
    db.close()

async def handle_message(msg: IncomingMessage):
    async with msg.process():
        try:
            headers = msg.headers or {}
            raw_output = msg.body.decode("utf-8")

            record = RawCommandData(
                timestamp=datetime.fromisoformat(headers["timestamp"]),
                machine_id=headers.get("machine_id"),
                machine_name=headers.get("machine_name"),
                os=headers.get("os"),
                command=headers.get("command"),
                raw_output=raw_output,
                raw_metadata={k: v for k, v in headers.items()
                          if k not in {"timestamp", "machine_id", "machine_name", "os", "command"}}
            )

            save_to_db(record)
            print(f"✅ Saved raw process from {headers.get('machine_name','')}")
        except Exception as e:
            print(f"❌ Error: {e}")

async def consume():
    conn = await connect_robust(host=RABBITMQ_HOST,port=5672)
    channel = await conn.channel()
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    await queue.consume(handle_message, no_ack=False)
    print(f"📥 Listening to '{QUEUE_NAME}'...")
    return conn

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume())
    loop.run_forever()
