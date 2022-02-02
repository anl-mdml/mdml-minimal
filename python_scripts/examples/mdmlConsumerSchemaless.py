#!/usr/bin/env python
import argparse

def main(args):
    import mdml_client as mdml
    consumer = mdml.kafka_mdml_consumer_schemaless(
        topics = [args.topic],
        group = args.group,
        kafka_host = args.host,
        kafka_port = args.port)

    for msg in consumer.consume():
        print(msg)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Admin tool to delete a Kafka Connector")
    parser.add_argument('-t', dest="topic", required=True,
                        help="Topic to consume")
    parser.add_argument('-g', dest="group", required=True,
                        help="Consumer group ID")
    parser.add_argument('-host', dest="host", default="merf.egs.anl.gov",
                        help="Hostname of the kafka broker [default: merf.egs.anl.gov]")
    parser.add_argument('-port', dest="port", default=9092,
                        help="Kafka broker port number [default: 9092]")
    args = parser.parse_args()
    main(args)
