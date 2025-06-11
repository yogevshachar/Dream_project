import os
from contextlib import asynccontextmanager

from aio_pika import connect_robust, ExchangeType
from fastapi import FastAPI

from rabbitmq import RabbitMQPublisher
from routers import ingest

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to RabbitMQ
    connection = await connect_robust(host=RABBITMQ_HOST, port=5672)
    channel = await connection.channel()
    exchange = await channel.declare_exchange("pre_normalise", ExchangeType.TOPIC,durable=True)
    app.state.rabbit_connection = connection
    app.state.rabbit_publisher = RabbitMQPublisher(exchange)
    yield
    # shutdown: Disconnect from RabbitMQ
    app.state.rabbit_connection.close()



app = FastAPI(debug=True, lifespan=lifespan)

app.include_router(ingest.router)

@app.get('/')
def is_alive():
    return 'alive'
