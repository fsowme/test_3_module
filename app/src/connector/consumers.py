import asyncio
import dataclasses
import logging

from confluent_kafka import Consumer

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class ConsumerConfig:
    bootstrap__servers: str
    group__id: str
    auto__offset__reset: str
    enable__auto__commit: bool

    def to_dict(self) -> dict:
        return {
            field.name.replace('__', '.'): getattr(self, field.name)
            for field in dataclasses.fields(self)
        }


@dataclasses.dataclass
class Message:
    topic: str
    key: str
    value: str


class ConsumerException(Exception):
    pass


class KafkaConsumer:
    _timeout = 0.1

    def __init__(self, config: ConsumerConfig):
        self.config = config
        self.consumer = Consumer(self.config.to_dict())

    async def run(self, topics: list[str]):
        self.consumer.subscribe(topics)

        while True:
            msg = await self.consumer.poll(self._timeout)

            if msg is None:
                continue

            error = msg.error()
            if error:
                logger.error("Error polling topics: %s", error)
                continue

            yield Message(topic=msg.topic(), key=msg.key(), value=msg.value())
            await asyncio.sleep(0)

    async def commit(self):
        await self.consumer.commit(asynchronous=False)

    def __enter__(self) -> 'KafkaConsumer':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.consumer.close()
