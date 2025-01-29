from contextlib import asynccontextmanager

from fastapi import FastAPI, Path

from .consumers import ConsumerConfig
from .managers import KafkaConsumerManager, start_manager_from_file, get_metrics
from .models import Connector
from .storages import FileStorage

KAFKA_BROKER = '127.0.0.1:9094'
CONSUMER_GROUP = 'connector_parody'

CONSUMER_CONFIG = ConsumerConfig(
    bootstrap__servers=KAFKA_BROKER,
    group__id=CONSUMER_GROUP,
    auto__offset__reset='earliest',
    enable__auto__commit=False,
)

consumer_manager = KafkaConsumerManager(FileStorage(), CONSUMER_CONFIG)


@asynccontextmanager
async def kafka_consumer_manager(app: FastAPI):
    await start_manager_from_file(manager=consumer_manager)

    yield

    await consumer_manager.stop()


application = FastAPI(lifespan=kafka_consumer_manager)


@application.post('/connectors')
async def create(new_connector: Connector):
    await consumer_manager.add_topic(new_connector.name, new_connector.config.topics)
    return new_connector


@application.put('/connectors/{connector_name}/config')
async def update(connector_name: str = Path(...), connector: Connector = ...):
    await consumer_manager.add_topic(connector_name, connector.config.topics)
    return connector


@application.get('/connectors/{connector_name}/status')
async def status(connector_name: str):
    state = "RUNNING" if consumer_manager.is_alive(connector_name) else "STOPPED"
    result = {
        "name": connector_name,
        "connector": {
            "state": state,
            "worker_id": "localhost:8000"
        },
        "tasks": [
            {
                "id": 0,
                "state": state,
                "worker_id": "localhost:8000"
            }
        ],
        "type": "sink"
    }
    return result

@application.get('/metrics/{connector_name}')
def get_metrics(connector_name: str):
    metrics = get_metrics(connector_name)
