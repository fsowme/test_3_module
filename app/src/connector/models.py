from pydantic import BaseModel, Field, HttpUrl


class Config(BaseModel):
    topics: str
    confluent_topic_bootstrap_servers: str = Field(..., alias="confluent.topic.bootstrap.servers")
    prometheus_listener_url: HttpUrl = Field(..., alias="prometheus.listener.url")
    reporter_result_topic_replication_factor: int = Field(..., alias="reporter.result.topic.replication.factor")


class Connector(BaseModel):
    name: str
    config: Config
