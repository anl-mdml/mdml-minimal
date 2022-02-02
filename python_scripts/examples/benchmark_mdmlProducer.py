import time
import argparse
import mdml_client as mdml


parser = argparse.ArgumentParser(description="Admin tool to delete a Kafka Connector")
parser.add_argument('-t', dest="topic", required=True,
                    help="Topic to consume")
parser.add_argument('-s', dest="size", required=True,
                    help="Size of the data filler in the message")
parser.add_argument('-f', dest="flush", required=True,
                    help="Flush every N messages")
parser.add_argument('-host', dest="host", default="merf.egs.anl.gov",
                    help="Hostname of the kafka broker [default: merf.egs.anl.gov]")
parser.add_argument('-port', dest="port", default=9092,
                    help="Kafka broker port number [default: 9092]")
parser.add_argument('--schema-host', dest="schemaHost", default="merf.egs.anl.gov",
                    help="Schema registry host [default: merf.egs.anl.gov]")
parser.add_argument('--schema-port', dest="schemaPort", default=8081,
                    help="Schema registry port [default: 8081]")
args = parser.parse_args()

data_schema = {
    "$schema": "http://merf.egs.anl.gov/mdml-test-benchmark-data-schema#",
    "title": "Producer test",
    "description": "Schema for benchmark testing",
    "type": "object",
    "properties": {
        "time": {
            "description": "Unix time the data point",
            "type": "number"
        },
        "data": {
            "description": "filler data",
            "type": "string"
        },
        "msgid": {
            "description": "msg ID",
            "type": "number"
        }
    },
    "required": [ "time", "data", "msgid" ]
}

producer = mdml.kafka_mdml_producer(
    topic = args.topic,
    schema = data_schema,
    kafka_host = args.host,
    kafka_port = args.port,
    schema_host = args.schemaHost,
    schema_port = args.schemaPort
)

i=0
try:
    while True:
        i+=1
        producer.produce({
            "time": time.time(),
            "data": "A"*int(args.size),
            "msgid": i
        })
        if i%int(args.flush) == 0:
            producer.flush()
            print("flushed")
except KeyboardInterrupt:
    producer.flush()
    print(f"sent {i} messages")