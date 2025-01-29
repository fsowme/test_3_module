from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from .consumers import ConsumerConfig
from .managers import KafkaConsumerManager, Status, get_metrics_obj, start_manager_from_file
from .models import Connector
from .storages import FileStorage

KAFKA_BROKER = 'kafka-0:9092'
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
templates = Jinja2Templates(directory="connector/templates")


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
    state = consumer_manager.status(connector_name)
    if state == Status.NOT_FOUND:
        raise HTTPException(status_code=404)

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


@application.get('/metrics/{connector_name}', response_class=HTMLResponse)
def get_metrics(request: Request, connector_name: str):
    metrics = get_metrics_obj(connector_name)
    return templates.TemplateResponse('prometheus.html', {'request': request, 'metrics': metrics})
