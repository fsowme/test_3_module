import argparse
import json
import logging
import random
import time

import confluent_kafka as kafka

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


CONFIG = {
    'bootstrap.servers': '127.0.0.1:9094',
    'acks': 'all',
    'retries': 3,
}


def produce(message_raw: bytes, topic_name: str):
    producer = kafka.Producer(CONFIG)
    try:
        producer.produce(topic_name, value=message_raw)
    except kafka.KafkaException as error:
        logger.error('Something went wrong, message:%s, error: %s', message_raw, error)
        raise
    producer.flush()


def _create_messages(alloc_val: int, free_val: int, poll_val: int, total_val: int) -> str:
    message_pattern = {
        'Alloc': {
            'Type': 'gauge',
            'Name': 'Alloc',
            'Description': 'Alloc is bytes of allocated head objects.',
            'Value': alloc_val
        },
        'FreeMemory': {
            'Type': 'gauge',
            'Name': 'FreeMemory',
            'Description': 'RAM available for programs to allocate.',
            'Value': free_val
        },
        'PollCount': {
            'Type': 'counter',
            'Name': 'PollCount',
            'Description': 'PollCount is quantity of metrics collection iteration.',
            'Value': poll_val
        },
        'TotalMemory': {
            'Type': 'gauge',
            'Name': 'TotalMemory',
            'Description': 'Total amount of RAM on this system.',
            'Value': total_val
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
