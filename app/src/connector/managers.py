import asyncio
import enum
import json
import logging
import os.path

from .consumers import ConsumerConfig, KafkaConsumer, Message
from .settings import Settings
from .storages import BaseStorage, FileStorage

logger = logging.getLogger(__name__)

_BASE_FILE_PATH = 'persist'


class Status(enum.Enum):
    RUNNING = 'RUNNING'
    NOT_FOUND = 'NOT_FOUND'
    STOPPED = 'STOPPED'


class ManagerException(Exception):
    pass


class TopicsNotConfigured(ManagerException):
    pass


class KafkaConsumerManager:
    def __init__(self, storage: BaseStorage, consumer_config: ConsumerConfig):
        self.storage = storage
        self.consumer_config = consumer_config
        self.settings_manager = Settings()

        self._task = None
        self.consumer: KafkaConsumer | None = None
        self.topics = []

    async def start(self, topics: list[str]):
        self.topics = topics

        if not self.topics:
            raise TopicsNotConfigured()

        self.consumer = KafkaConsumer(self.consumer_config, self.topics)

        self.topics = topics
        self._create_task()
        logger.info('Consumer started')

    async def add_topic(self, name: str, topic: str):

        _, topic = self.settings_manager.add_topic(name, topic)
        self.topics.append(topic)
        self.consumer.topics = self.topics

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, RuntimeError):
                pass
            self._task = None
            logger.info('Consumer stopped')

    def _create_task(self):
        def message_handler(message: Message):
            self.storage.save(_get_file_path(message.topic), message.value)

        self._task = asyncio.create_task(self.consumer.run(message_handler=message_handler))

    def is_alive(self, connector):
        settings = self.settings_manager.get_settings()
        try:
            topic = settings[connector]
        except KeyError:
            return False
        return self.consumer and topic in self.topics

    def status(self, connector):
        settings = self.settings_manager.get_settings()
        if connector not in settings:
            return Status.NOT_FOUND

        if self.consumer and self._task and settings[connector] in self.topics:
            return Status.RUNNING

        return Status.STOPPED


async def start_manager_from_file(manager: KafkaConsumerManager) -> None:
    topics = Settings().get_topics()
    if topics:
        await manager.start(topics)
    else:
        logger.info('Topics not found, consumer not started')


MetricsType = dict[str, dict[str, str | int]]


def get_metrics_obj(connector_name: str) -> MetricsType:
    topic = Settings().topic_by_name(connector_name)
    metrics_raw = FileStorage().read(_get_file_path(topic))
    return json.loads(metrics_raw)


def _get_file_path(name: str) -> str:
    return os.path.join(_BASE_FILE_PATH, name)
