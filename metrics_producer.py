import argparse
import json
import logging
import random
import time

import confluent_kafka as kafka

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


CONFIG = {
    'bootstrap.servers': 'localhost:9092',
    'acks': 'all',
    'retries': 3,
}


def produce(message: bytes, topic_name: str):
    producer = kafka.Producer(CONFIG)
    try:
        producer.produce(topic_name, value=message)
    except kafka.KafkaException as error:
        logger.error('Something went wrong, message:%s, error: %s', message, error)
        raise
    producer.flush()


def _create_messages(alloc: int, free: int, poll: int, total: int) -> str:
    message_pattern = {
        'Alloc': {
            'Type': 'gauge',
            'Name': 'Alloc',
            'Description': 'Alloc is bytes of allocated head objects.',
            'Value': alloc
        },
        'FreeMemory': {
            'Type': 'gauge',
            'Name': 'FreeMemory',
            'Description': 'RAM available for programs to allocate.',
            'Value': free
        },
        'PollCount': {
            'Type': 'counter',
            'Name': 'PollCount',
            'Description': 'PollCount is quantity of metrics collection iteration.',
            'Value': poll
        },
        'TotalMemory': {
            'Type': 'gauge',
            'Name': 'TotalMemory',
            'Description': 'Total amount of RAM on this system.',
            'Value': total
        },
    }
    return json.dumps(message_pattern)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('producer')
    parser.add_argument('topic_name', type=str, help='topic name')
    parsed = parser.parse_args()

    timeout = 1
    counter = 0
    while True:
        free = random.randint(1000000000, 9000000000)
        alloc = random.randint(10000000, 90000000)
        total = free + alloc + random.randint(1000000000, 9000000000)

        message = _create_messages(alloc, free, counter, total)
        produce(message.encode('utf8'), parsed.topic_name)

        counter += 1
        time.sleep(timeout)
