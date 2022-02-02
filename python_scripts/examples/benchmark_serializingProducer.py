#!/usr/bin/env python
import argparse

def main(args):
    import os
    import json
    import time
    import string
    import random
    from uuid import uuid4
    from confluent_kafka import SerializingProducer
    from confluent_kafka.serialization import StringSerializer
    from confluent_kafka.schema_registry import SchemaRegistryClient
    from confluent_kafka.schema_registry.json_schema import JSONSerializer

    def delivery_report(err, msg):
        """
        Reports the failure or success of a message delivery.
        Args:
            err (KafkaError): The error that occurred on None on success.
            msg (Message): The message that was produced or failed.
        Note:
            In the delivery report callback the Message.key() and Message.value()
            will be the binary format as encoded by any configured Serializers and
            not the same object that was passed to produce().
            If you wish to pass the original object(s) for key and value to delivery
            report callback we recommend a bound callback or lambda where you pass
            the objects along.
        """
        if err is not None:
            print(f"Delivery failed for User record {msg.key()}: {err}")
            return
        print(f'User record {msg.key()} successfully produced to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')

    with open("../../json_schemas/random_bytes.json","r") as f:
        schema_string = f.read()

    schema_registry_conf = {
        "url": f"http://{args.schemaHost}:{args.schemaPort}"
    }
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    json_serializer = JSONSerializer(schema_string, schema_registry_client)

    producer_config = {
        'bootstrap.servers': f'{args.host}:{args.port}',
        'key.serializer': StringSerializer('utf-8'),
        'value.serializer': json_serializer
    }
    producer = SerializingProducer(producer_config)

    print("Start producing data")

    i=0
    random_part = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k = int(args.sizeMessage)))
    # random_bytes = os.urandom(int(args.sizeMessage))
    start=time.time()
    while i < int(args.numMessages):
        try:
            dat = {
                'id': i,
                'time': time.time(),
                'random_bytes': random_part
            }
            producer.produce(topic=args.topic, key=(str(uuid4())),
                            value=dat, on_delivery=delivery_report)
            i += 1
            time.sleep(float(args.delay))
        except KeyboardInterrupt:
            print("Quitting producer loop")
            break
        except ValueError:
            print("invalid input")
            continue
    print("Flushing producer")
    producer.flush()
    stop = time.time()
    print(f"finished sending {i} messages in {stop-start} seconds")
    print(f"average {i/(stop-start)} msgs/sec")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Admin tool to delete a Kafka Connector")
    parser.add_argument('-t', dest="topic", required=True,
                        help="Name of the Kafka topic")
    parser.add_argument('-host', dest="host", default="merf.egs.anl.gov",
                        help="Hostname of the kafka broker [default: merf.egs.anl.gov]")
    parser.add_argument('-port', dest="port", default=9092,
                        help="Kafka broker port number [default: 9092]")
    parser.add_argument('-d', dest="delay", default=1,
                        help="Number of seconds to delay between each message [default: 1]")
    parser.add_argument('-n', dest="numMessages", default=1000,
                        help="Number of messages to send [default: 1000]")
    parser.add_argument('-s', dest="sizeMessage", default=100,
                        help="Size of the messages to send [default: 100]")
    parser.add_argument('--schema-host', dest="schemaHost", default="merf.egs.anl.gov",
                        help="Schema registry host [default: merf.egs.anl.gov]")
    parser.add_argument('--schema-port', dest="schemaPort", default=8081,
                        help="Schema registry port [default: 8081]")
    args = parser.parse_args()
    main(args)