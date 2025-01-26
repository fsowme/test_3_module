import json
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .consumers import KafkaConsumerManager
from .storages import FileStorage

KAFKA_BROKER = ''
CONSUMER_GROUP = ''
PERSIST_PATH = 'persist'
TOPICS_FILE = os.path.join(PERSIST_PATH, '_topics')
DEFAULT_TOPIC = 'metrics-default'

consumer_manager = KafkaConsumerManager(
    broker=KAFKA_BROKER, group=CONSUMER_GROUP, storage=FileStorage(PERSIST_PATH), skip_errors=True
)


@asynccontextmanager
async def kafka_consumer_manager(app: FastAPI):
    try:
        with open(TOPICS_FILE, 'r') as f:
            topics = json.loads(f.read())
    except FileNotFoundError:
        topics = [DEFAULT_TOPIC]

    if topics:
        await consumer_manager.start(topics)
    yield

    await consumer_manager.stop()


application = FastAPI(lifespan=kafka_consumer_manager)
