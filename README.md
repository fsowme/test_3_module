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


## Part 2
