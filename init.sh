docker compose stop connector
#
docker compose exec kafka-0 kafka-topics.sh \
  --delete --topic metrics-default --bootstrap-server localhost:9092
docker compose exec kafka-0 kafka-topics.sh \
  --create --topic metrics-default --partitions 3 --replication-factor 3 \
  --bootstrap-server localhost:9092 --config min.insync.replicas=2
#
docker compose start connector
