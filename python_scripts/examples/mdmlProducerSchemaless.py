import time
import argparse
import mdml_client as mdml
import json

parser = argparse.ArgumentParser(description="Admin tool to delete a Kafka Connector")
parser.add_argument('-t', dest="topic", required=True,
                    help="Topic to consume")
# parser.add_argument('-g', dest="group", required=True,
#                     help="Consumer group ID")
parser.add_argument('-host', dest="host", default="merf.egs.anl.gov",
                    help="Hostname of the kafka broker [default: merf.egs.anl.gov]")
parser.add_argument('-port', dest="port", default=9092,
                    help="Kafka broker port number [default: 9092]")
args = parser.parse_args()

producer = mdml.kafka_mdml_producer_schemaless(
    topic = args.topic,
    kafka_host = args.host,
    kafka_port = args.port
)

try:
    # time.sleep(5)
    producer.produce(json.dumps({
        "time": time.time(),
        "int1": 1,
        "int2": 2
    }))
    producer.flush()
    print('sent')
except KeyboardInterrupt:
    print("done")
