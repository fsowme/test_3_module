import asyncio
import logging
import os.path

from .consumers import ConsumerConfig, KafkaConsumer
from .settings import Settings
from .storages import BaseStorage

logger = logging.getLogger(__name__)

_BASE_FILE_PATH = 'persist'
_SETTINGS_FILE_NAME = 'settings.json'


class ManagerException(Exception):
    pass


class TopicsNotConfigured(ManagerException):
    pass


class KafkaConsumerManager:
    def __init__(self, storage: BaseStorage, consumer_config: ConsumerConfig):
        self.storage = storage
        self.consumer_config = consumer_config
        self.consumer = KafkaConsumer(config=self.consumer_config)
        self.settings_manager = Settings()

        self.topics = []
        self._task = None

    async def start(self, topics: list[str]):
        self.topics = topics

        if not self.topics:
            raise TopicsNotConfigured()

        if self._task is not None:
            await self.stop()

        self.topics = topics
        self._task = asyncio.create_task(self.consumer.run(self.topics))
        logger.info('Consumer started')

    async def add_topic(self, name: str, topic: str):
        await self.stop()

        _, topic = self.settings_manager.add_topic(name, topic)
        self.topics.append(topic)
        self._task = asyncio.create_task(self.consumer.run(self.topics))
        logger.info('Topics added')

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
            logger.info('Consumer stopped')

    async def process_message(self, topic: str, message: bytes):
        self.storage.save(_get_file_path(topic), message)

    def is_alive(self, connector):
        settings = self.settings_manager.get_settings()
        topic = settings[connector]
        return self._task is not None and not self._task.done() and topic in self.topics


def start_manager_from_file(manager: KafkaConsumerManager) -> None:
    topics = Settings().get_topics()
    if topics:
        manager.start(topics)
    else:
        logger.info('Topics not found, consumer not started')


def _get_file_path(name: str) -> str:
    return os.path.join(_BASE_FILE_PATH, name)
