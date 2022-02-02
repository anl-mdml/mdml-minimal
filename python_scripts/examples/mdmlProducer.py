import time
import argparse
import mdml_client as mdml

parser = argparse.ArgumentParser(description="Admin tool to delete a Kafka Connector")
parser.add_argument('-t', dest="topic", required=True,
                    help="Topic to consume")
# parser.add_argument('-g', dest="group", required=True,
#                     help="Consumer group ID")
parser.add_argument('-s', dest="host", required=True,
                    help="Hostname of the kafka broker")
parser.add_argument('-port', dest="port", default=9092,
                    help="Kafka broker port number [default: 9092]")
parser.add_argument('--schema-host', dest="schemaHost", default="merf.egs.anl.gov",
                    help="Schema registry host [default: merf.egs.anl.gov]")
parser.add_argument('--schema-port', dest="schemaPort", default=8081,
                    help="Schema registry port [default: 8081]")
args = parser.parse_args()

data_schema = {
    "$schema": "http://merf.egs.anl.gov/mdml-test-producer-data-schema#",
    "title": "Producer test",
    "description": "Schema for testing the MQTT connector",
    "type": "object",
    "properties": {
        "time": {
            "description": "Unix time the data point",
            "type": "number"
        },
        "int1": {
            "description": "number of CPU cores",
            "type": "number"
        },
        "int2": {
            "description": "average percent usage of CPU",
            "type": "number"
        }
    },
    "required": [ "time", "int1", "int2" ]
}

producer = mdml.kafka_mdml_producer(
    topic = args.topic,
    schema = data_schema,
    kafka_host = args.host,
    kafka_port = args.port,
    schema_host = args.schemaHost,
    schema_port = args.schemaPort
)

try:
    # time.sleep(5)
    for _ in range(25):
        producer.produce({
            "time": time.time(),
            "int1": 1,
            "int2": 2
        }, key="testing-compacted-topics-2")
        time.sleep(5)
        producer.flush()
    print('sent')
except KeyboardInterrupt:
    print("done")
