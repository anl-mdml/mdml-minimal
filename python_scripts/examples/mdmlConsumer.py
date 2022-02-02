#!/usr/bin/env python
import argparse

def main(args):
    import mdml_client as mdml
    print(args.topic)
    consumer = mdml.kafka_mdml_consumer(
        topics = args.topic,
        group = args.group,
        kafka_host = args.host,
        kafka_port = args.port,
        schema_host = args.schemaHost,
        schema_port = args.schemaPort)
    i = 0
    for msg in consumer.consume(overall_timeout=-1):
        i += 1
        print(msg)
        #print(f"id: {msg['value']['int1']} num: {i}")
    consumer.close()
    print(f"{i} msgs consumed")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Admin tool to delete a Kafka Connector")
    parser.add_argument('-t', dest="topic", required=True,nargs='+',default=[],
                        help="Topic to consume")
    parser.add_argument('-g', dest="group", required=True,
                        help="Consumer group ID")
    parser.add_argument('-s', dest="host", required=True,
                        help="Hostname of the kafka broker")
    parser.add_argument('-port', dest="port", default=9092,
                        help="Kafka broker port number [default: 9092]")
    parser.add_argument('--schema-host', dest="schemaHost", default="merf.egs.anl.gov",
                        help="Schema registry host [default: merf.egs.anl.gov]")
    parser.add_argument('--schema-port', dest="schemaPort", default=8081,
                        help="Schema registry port [default: 8081]")
    args = parser.parse_args()
    main(args)
