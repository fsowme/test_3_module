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
(kafka_test_3) ➜  test_3_module git:(main) ✗ curl -X POST -H 'Content-Type: application/json' --data @connector.json http://localhost:8083/connectors | jq                   
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  1843  100   904  100   939   2768   2875 --:--:-- --:--:-- --:--:--  5636
{
  "name": "pg-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "postgres-user",
    "database.password": "postgres-pw",
    "database.dbname": "customers",
    "database.server.name": "customers",
    "table.whitelist": "public.customers",
    "transforms": "unwrap,mask",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.unwrap.drop.tombstones": "false",
    "transforms.unwrap.delete.handling.mode": "rewrite",
    "transforms.mask.type": "org.apache.kafka.connect.transforms.MaskField$Value",
    "transforms.mask.fields": "private_info",
    "transforms.mask.replacement": "CENSORED",
    "topic.prefix": "customers",
    "topic.creation.enable": "true",
    "topic.creation.default.replication.factor": "-1",
    "topic.creation.default.partitions": "-1",
    "skipped.operations": "none",
    "name": "pg-connector"
  },
  "tasks": [],
  "type": "source"
}
```

2. Пример сообщения в топике
```
{
	"schema": {
		"type": "struct",
		"fields": [
			{
				"type": "int32",
				"optional": false,
				"field": "id"
			},
			{
				"type": "string",
				"optional": true,
				"field": "name"
			},
			{
				"type": "string",
				"optional": true,
				"field": "private_info"
			},
			{
				"type": "string",
				"optional": true,
				"field": "__deleted"
			}
		],
		"optional": false,
		"name": "customers.public.users.Value"
	},
	"payload": {
		"id": 1,
		"name": "Alex",
		"private_info": "CENSORED",
		"__deleted": "false"
	}
}
```
