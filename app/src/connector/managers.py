import asyncio
import json
import logging
import os.path

from .consumers import ConsumerConfig, KafkaConsumer, Message
from .settings import Settings
from .storages import BaseStorage, FileStorage

logger = logging.getLogger(__name__)

_BASE_FILE_PATH = 'persist'


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
        self._create_task()
        logger.info('Consumer started')

    async def add_topic(self, name: str, topic: str):
        await self.stop()

        _, topic = self.settings_manager.add_topic(name, topic)
        self.topics.append(topic)
        self._create_task()
        logger.info('Topics added')

    def _create_task(self):
        def message_handler(message: Message):
            self.storage.save(_get_file_path(message.topic), message.value)

        self._task = asyncio.create_task(self.consumer.run(self.topics, message_handler=message_handler))

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
            logger.info('Consumer stopped')

    def is_alive(self, connector):
        settings = self.settings_manager.get_settings()
        topic = settings[connector]
        return self._task is not None and not self._task.done() and topic in self.topics


async def start_manager_from_file(manager: KafkaConsumerManager) -> None:
    topics = Settings().get_topics()
    if topics:
        await manager.start(topics)
    else:
        logger.info('Topics not found, consumer not started')


MetricsType = dict[str, dict[str, str|int]]


def get_metrics(connector_name: str) -> MetricsType:
    topic = Settings().topic_by_name(connector_name)
    metrics_raw = FileStorage().read(_get_file_path(topic))
    return json.loads(metrics_raw)


def _get_file_path(name: str) -> str:
    return os.path.join(_BASE_FILE_PATH, name)
