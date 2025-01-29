import asyncio
import dataclasses
import logging
from typing import Callable

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


class KafkaConsumer:
    _timeout = 0.1

    def __init__(self, config: ConsumerConfig, topics: list[str]):
        self.config = config
        self.consumer = Consumer(self.config.to_dict())
        self.topics = topics

    async def run(self, message_handler: Callable[[Message], None]):
        self.consumer.subscribe(self.topics)
        try:
            while True:
                await asyncio.sleep(0)

                if self.topics != self.consumer.list_topics():
                    self.consumer.subscribe(self.topics)

                msg = self.consumer.poll(self._timeout)

                if msg is None:
                    continue

                error = msg.error()
                if error:
                    logger.error("Error polling topics: %s", error)
                    continue

                value = msg.value()
                if isinstance(value, bytes):
                    value = value.decode()
                message = Message(topic=msg.topic(), key=msg.key(), value=value)

                message_handler(message)

                self.consumer.commit(asynchronous=False)
        finally:
            self.consumer.close()
