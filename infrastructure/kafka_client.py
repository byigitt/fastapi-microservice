import json
import os
from typing import Any, Callable, Dict, List
from confluent_kafka import Consumer, Producer, KafkaError

class KafkaClient:
    def __init__(self, bootstrap_servers: str = None):
        self.bootstrap_servers = bootstrap_servers or os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self._producer = None

    @property
    def producer(self):
        if self._producer is None:
            self._producer = Producer({
                'bootstrap.servers': self.bootstrap_servers,
                'client.id': f'python-producer-{os.getpid()}'
            })
        return self._producer

    def create_consumer(self, group_id: str, topics: List[str]):
        consumer = Consumer({
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })
        consumer.subscribe(topics)
        return consumer

    def publish_message(self, topic: str, key: str, value: Dict[str, Any]) -> None:
        """Publish a message to a Kafka topic"""
        try:
            self.producer.produce(
                topic=topic,
                key=key,
                value=json.dumps(value).encode('utf-8'),
                callback=self._delivery_report
            )
            # Wait for message to be delivered
            self.producer.flush()
        except Exception as e:
            print(f"Error publishing message to {topic}: {e}")

    def consume_messages(self, consumer: Consumer, handler: Callable[[str, Dict[str, Any]], None], timeout: float = 1.0):
        """Consume messages from Kafka topics"""
        try:
            while True:
                msg = consumer.poll(timeout)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event - not an error
                        continue
                    else:
                        print(f"Error: {msg.error()}")
                        break
                
                # Parse the message
                key = msg.key().decode('utf-8') if msg.key() else None
                try:
                    value = json.loads(msg.value().decode('utf-8'))
                    # Call the handler function with the message
                    handler(key, value)
                except json.JSONDecodeError:
                    print(f"Failed to decode JSON: {msg.value()}")
                except Exception as e:
                    print(f"Error processing message: {e}")
        except KeyboardInterrupt:
            print("Interrupted")
        finally:
            consumer.close()

    def _delivery_report(self, err, msg):
        """Delivery report handler called on successful or failed delivery"""
        if err is not None:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}") 