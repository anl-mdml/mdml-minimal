#!/usr/bin/env python
import argparse

def main(args):
    topic = args.topic
    group = args.group

    import json
    import time
    import random
    from uuid import uuid4
    from confluent_kafka import DeserializingConsumer
    from confluent_kafka.serialization import StringDeserializer
    from confluent_kafka.schema_registry import SchemaRegistryClient
    from confluent_kafka.schema_registry.json_schema import JSONDeserializer

    # Might be better to grab the latest registered schema
    schemaRegistry_config = {
        "url": f"http://{args.schemaHost}:{args.schemaPort}"
    }
    client = SchemaRegistryClient(schemaRegistry_config)
    integer_schema = client.get_latest_version(f'{args.topic}-value').schema.schema_str

    json_deserializer = JSONDeserializer(integer_schema)

    string_deserializer = StringDeserializer('utf_8')

    consumer_conf = {
        'bootstrap.servers': f"{args.host}:{args.port}",
        'key.deserializer': string_deserializer,
        'value.deserializer': json_deserializer,
        'group.id': args.group,
        'auto.offset.reset': "earliest"
    }

    consumer = DeserializingConsumer(consumer_conf)
    consumer.subscribe([args.topic])

    times = []
    num_msgs = 0
    num_bytes = 0
    while True:
        try:
            # SIGINT can't be handled when polling, limit timeout to 1 second.
            msg = consumer.poll(1.0)
            # print(msg)/
            if msg is None:
                print("got none")
                continue
            arrived = time.time()
            d = msg.value()
            num_msgs += 1
            num_bytes += int(args.size)
            times.append([d['time'], arrived])
            print(f"got {num_msgs}")

        except KeyboardInterrupt:
            print(f"num bytes: {num_bytes}")
            print(f"num msgs: {num_msgs}")
            print(f"time from first to last: {times[-1][1]-times[0][0]} seconds")
            print(f"{(num_bytes/1000000)/(times[-1][1]-times[0][0])} MB/second")
            break

    consumer.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Admin tool to delete a Kafka Connector")
    parser.add_argument('-t', dest="topic", required=True,
                        help="Topic to consume")
    parser.add_argument('-g', dest="group", required=True,
                        help="Consumer group ID")
    parser.add_argument('-s', dest="size", required=True,
                        help="Size in bytes of the messages")
    parser.add_argument('-host', dest="host", default="merf.egs.anl.gov",
                        help="Hostname of the kafka broker [default: merf.egs.anl.gov]")
    parser.add_argument('-port', dest="port", default=9092,
                        help="Kafka broker port number [default: 9092]")
    parser.add_argument('--schema-host', dest="schemaHost", default="merf.egs.anl.gov",
                        help="Schema registry host [default: merf.egs.anl.gov]")
    parser.add_argument('--schema-port', dest="schemaPort", default=8081,
                        help="Schema registry port [default: 8081]")

    args = parser.parse_args()
    main(args)