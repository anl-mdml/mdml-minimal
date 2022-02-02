#!/usr/bin/env python
import argparse

def main(args):
    import time
    import mdml_client as mdml
    consumer = mdml.kafka_mdml_consumer(
        topics = [args.topic],
        group = args.group,
        kafka_host = args.host,
        kafka_port = args.port,
        schema_host = args.schemaHost,
        schema_port = args.schemaPort)
    i = 0
    msgs = []
    try:
        for msg in consumer.consume():
            i += 1
            received = time.time()
            msg['value']['received'] = received
            msg['value']['received_id'] = i
            msgs.append(msg)
    except KeyboardInterrupt:
        print("cancelling...")
    finally:
        print(f"Total msgs received: {len(msgs)}")
        send_times = []
        for msg in msgs:
            send_times.append(msg['value']['received']-msg['value']['time'])
        avg_send_time = sum(send_times)/len(send_times)
        print(f"Average send time: {avg_send_time}")
        print(f"Average send rate: {int(args.size)/avg_send_time}")
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="benchmark consumer")
    parser.add_argument('-t', dest="topic", required=True,
                        help="Topic to consume")
    parser.add_argument('-g', dest="group", required=True,
                        help="Consumer group ID")
    parser.add_argument('-s', dest="size", required=True,
                        help="size of filler data")
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
