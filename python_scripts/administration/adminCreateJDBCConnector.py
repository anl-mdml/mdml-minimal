import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-n", help="name of the connector (i.e. mdml-<experiment>-<device>-psql-connector)",
                        dest="name", required=True)
parser.add_argument("-t", help="topic regex (i.e. mdml-example-.* or mdml-exmaple-device1)",
                        dest="topic_regex", required=True)
parser.add_argument("-u", help="Database admin username",
                        dest="uname", required=True)
parser.add_argument("-p", help="Database admin password",
                        dest="passw", required=True)
parser.add_argument("-s", help="server name", dest="host", required=True)
args = parser.parse_args()

import json
import requests

KAFKA_CONNECT_URL = f"http://{args.host}:8083/connectors"
# CONNECTOR_NAME = "mdml-examples-psql-connector"
CONNECTOR_NAME = args.name

def configure_connector(args):
    """Calls Kafka Connect to create the Connector"""

    resp = requests.get(f"{KAFKA_CONNECT_URL}/{CONNECTOR_NAME}")
    if resp.status_code == 200:
        return

    resp = requests.post(
        KAFKA_CONNECT_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "name": CONNECTOR_NAME, #name of the connector
                "config": {
                    "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
                    "insert.mode": "insert", # use insert mode to insert into table
                    "tasks.max": 1,
                    "connection.url": f"jdbc:postgresql://postgres:5432/kafka",
                    "connection.user": args.uname,
                    "connection.password": args.passw,
                    "topics.regex": args.topic_regex, # regex for topic 
                    # "topics.regex": "mdml-example-.*", # regex for topic 
                    # "topics.regex": "mdml-example-device", # regex for topic 
                    "auto.create": True,
                    "auto.evolve": True,
                    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
                    # "key.converter": "org.apache.kafka.connect.json.JsonConverter",
                    "key.converter.schemas.enable": False,
                    "value.converter": "io.confluent.connect.json.JsonSchemaConverter",
                    # "value.converter": "org.apache.kafka.connect.json.JsonConverter",
                    "value.converter.schemas.enable": True,
                    "value.converter.schema.registry.url": f"http://{args.host}:8081"
                    # "auto.register.schemas": False,
                    # "use.latest.version": True
                }
            }
        )
    )
    try: 
        print(resp.text)
        resp.raise_for_status()
    except:
        print("FAILED. creating JDBC Connector")
        exit(1)
    print("connector created")

# delete connector with 
# curl -X DELETE http://merf.egs.anl.gov:8083/connectors/<connector-name>


if __name__ == "__main__":
    configure_connector(args)
