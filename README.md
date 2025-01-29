# test_3_module

## Part 1

```shell
curl -X PUT \
-H "Content-Type: application/json" \
--data '{
"connector.class":"io.confluent.connect.jdbc.JdbcSourceConnector",
"tasks.max":"1",
"connection.url":"jdbc:postgresql://postgres:5432/customers?user=postgres-user&password=postgres-pw&useSSL=false",
"connection.attempts":"5",
"connection.backoff.ms":"50000",
"mode":"timestamp",
"timestamp.column.name":"updated_at",
"topic.prefix":"postgresql-jdbc-bulk-",
"table.whitelist": "users",
"poll.interval.ms": "200",
"batch.max.rows": 1000,
"producer.override.linger.ms": 100,
"producer.override.batch.size": 526000,
"transforms":"MaskField",
"transforms.MaskField.type":"org.apache.kafka.connect.transforms.MaskField$Value",
"transforms.MaskField.fields":"private_info",
"transforms.MaskField.replacement":"CENSORED",
"compression.type":"snappy",
"buffer.memory":"134217728"
}' \
http://localhost:8083/connectors/postgres-source/config
```

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
