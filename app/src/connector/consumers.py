import asyncio
import logging

from confluent_kafka import Consumer

from .storages import BaseStorage

logger = logging.getLogger(__name__)


class ManagerException(Exception):
    pass


class TopicsNotConfigured(ManagerException):
    pass


class PollException(ManagerException):
    pass


class KafkaConsumerManager:
    _auto_commit = False
    _auto_reset = 'latest'
    _timeout = 1
    _topics_list_file = '_topics.json'

    def __init__(self, broker: str, group: str, storage: BaseStorage, skip_errors=True):
        self.broker = broker
        self.group_id = group
        self.storage = storage
        self.skip_errors = skip_errors

        self.topics = []
        self._task = None
        self._stop_event = asyncio.Event()

    async def start(self, topics: list[str]):
        if topics is not None:
            self.topics.extend(topics)

        if not self.topics:
            raise TopicsNotConfigured()

        if self._task is not None:
            await self.stop()

        self._task = asyncio.create_task(self._runner())
        logger.info('Consumer started')

    async def stop(self):
        if self._task:
            self._stop_event.set()
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        if self._stop_event.is_set():
            self._stop_event.clear()

        logger.info('Consumer stopped')

    async def _runner(self):
        config = {
            'bootstrap.servers': self.broker,
            'group.id': self.group_id,
            'auto.offset.reset': self._auto_reset,
            'enable.auto.commit': self._auto_commit,
        }
        consumer = Consumer(config)
        consumer.subscribe(self.topics)

        try:
            while not self._stop_event.is_set():
                msg = consumer.poll(self._timeout)
                if msg is None:
                    continue
                error = msg.error()
                if error:
                    if not self.skip_errors:
                        raise PollException()
                    logger.error("Error polling topics: %s", error)
                await self.process_message(msg.topic(), msg.value())
                consumer.commit(asynchronous=False)
        finally:
            consumer.close()

    async def process_message(self, topic: str, message: bytes):
        self.storage.save(topic, message)
