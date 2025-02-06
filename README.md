# test_3_module

## Part 1

| Эксперимент | batch.size | linger.ms | compression.type | buffer.memory | batch.max.rows | Source Record Write Rate (кops/sec) |
|------------:|-----------:|----------:|-----------------:|--------------:|---------------:|------------------------------------:|
|           1 |        500 |      1000 |                - |      33554432 |            100 |                                   5 |
|           2 |     526000 |       100 |           snappy |     134217728 |           1000 |                                 162 |

1. Если данные падают батчами, как в примере с созданием за раз 9 млн записей, то лучше всего поднять batch.size,
batch.max.rows - это поможет убрать лишний оверхед в виде заголовков пакетов, времени на подтверждение доставки и
прочий мусор, тут узкое место сеть и диск.
2. Если данные приходят постепенно, то есть два пути:
   1. Если нужно получать данные близко к реальному времени, то придется уменьшать linger.ms и batch.max.rows и
   мирится с просадками производительности
   2. Второй вариант если не нужно в реальном времени получать данные, можно в разумных приделах увеличить linger.ms и
   batch.max.rows



## Part 2
1. Создадим 3 топика (metrics-1, metrics-2, metrics-3) и запустим на них продюсеров
```shell
python metrics_producer.py metrics-1
python metrics_producer.py metrics-2
python metrics_producer.py metrics-3
```
2. Создадим консьюмера в нашем серсисе-"коннекторе" и подпишем на 3 топика
```shell
curl -sS -X POST -H 'Content-Type: application/json' --data @conn_configs/config_1.json http://localhost:8000/connectors
curl -sS -X POST -H 'Content-Type: application/json' --data @conn_configs/config_2.json http://localhost:8000/connectors
curl -sS -X POST -H 'Content-Type: application/json' --data @conn_configs/config_3.json http://localhost:8000/connectors
```
3. Метрики доступны по адресам
```
localhost:8000/metrics/prometheus-connector-1
localhost:8000/metrics/prometheus-connector-2
localhost:8000/metrics/prometheus-connector-3
```
4. Статус доступен по адресам
```
localhost:8000/connectors/prometheus-connector-1/status
localhost:8000/connectors/prometheus-connector-2/status
localhost:8000/connectors/prometheus-connector-3/status
```

## Part 3
1. Лог создания коннектора
```
kafka-connect-1  | [2025-02-06 14:28:53,545] INFO Creating connector pg-connector of type io.debezium.connector.postgresql.PostgresConnector (org.apache.kafka.connect.runtime.Worker)
kafka-connect-1  | [2025-02-06 14:28:53,561] INFO SourceConnectorConfig values: 
kafka-connect-1  |      config.action.reload = restart
kafka-connect-1  |      connector.class = io.debezium.connector.postgresql.PostgresConnector
kafka-connect-1  |      errors.log.enable = false
kafka-connect-1  |      errors.log.include.messages = false
kafka-connect-1  |      errors.retry.delay.max.ms = 60000
kafka-connect-1  |      errors.retry.timeout = 0
kafka-connect-1  |      errors.tolerance = none
kafka-connect-1  |      exactly.once.support = requested
kafka-connect-1  |      header.converter = null
kafka-connect-1  |      key.converter = null
kafka-connect-1  |      name = pg-connector
kafka-connect-1  |      offsets.storage.topic = null
kafka-connect-1  |      predicates = []
kafka-connect-1  |      tasks.max = 1
kafka-connect-1  |      topic.creation.groups = []
kafka-connect-1  |      transaction.boundary = poll
kafka-connect-1  |      transaction.boundary.interval.ms = null
kafka-connect-1  |      transforms = [unwrap, mask]
kafka-connect-1  |      value.converter = null
kafka-connect-1  |  (org.apache.kafka.connect.runtime.SourceConnectorConfig)
```
