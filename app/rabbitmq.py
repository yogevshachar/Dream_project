

from aio_pika import Message, DeliveryMode

from fastapi import FastAPI,Request


class RabbitMQPublisher:
    def __init__(self, exchange):
        self.exchange = exchange

    async def publish(self, body: bytes, headers: dict):
        message = Message(
            body=body,
            delivery_mode=DeliveryMode.PERSISTENT,
            headers=headers
        )
        await self.exchange.publish(message, routing_key="")



def get_publisher(request: Request) -> RabbitMQPublisher:
    return request.app.state.rabbit_publisher