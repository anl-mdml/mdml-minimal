import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-n", help="name of the connector (i.e. mdml-<experiment>-<device>-psql-connector)",
                        dest="name", required=True)
parser.add_argument("-t", help="topic (i.e. mdml-exmaple-device1)",
                        dest="topic", required=True)
parser.add_argument("-m", help="MQTT topic (i.e. MDML/EXAMPLE/DEVICE1)",
                        dest="mqtt_topic", required=True)
parser.add_argument("-i", help="ID for MQTT client",
                        dest="clientID", required=True)
parser.add_argument("-p", help="password for mqtt user",
                        dest="password", required=True)
parser.add_argument("-s", help="MDML server",
                        dest="server", required=True)
parser.add_argument("--type", help="type of connector", dest="type", required=True)
args = parser.parse_args()

import json
import requests

KAFKA_CONNECT_URL = f"http://{args.server}:8083/connectors"
# CONNECTOR_NAME = "mdml-examples-psql-connector"
CONNECTOR_NAME = args.name

def configure_connector(args):
    """Calls Kafka Connect to create the Connector"""

    resp = requests.get(f"{KAFKA_CONNECT_URL}/{CONNECTOR_NAME}")
    if resp.status_code == 200:
        return

    if args.type == "source":
        resp = requests.post(
            KAFKA_CONNECT_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "name": CONNECTOR_NAME, #name of the connector
                    "config": {
                        "connector.class": "be.jovacon.kafka.connect.MQTTSourceConnector",
                        "mqtt.topic": args.mqtt_topic,
                        "kafka.topic": args.topic,
                        "mqtt.clientID": args.clientID,
                        "mqtt.broker": "tcp://mosquitto:1883",
                        "mqtt.qos": 2,
                        "mqtt.userName": "admin",
                        "mqtt.password": args.password,                
                        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
                        "key.converter.schemas.enable": False,
                        "value.converter": "org.apache.kafka.connect.storage.StringConverter",
                        "value.converter.schemas.enable": False,
                        # "value.converter": "io.confluent.connect.json.JsonSchemaConverter",
                        # "value.converter.schemas.enable": True,
                        "value.converter.schema.registry.url": "http://schema-registry:8081"
                    }
                }
            )
        )
    elif args.type == "sink":
        resp = requests.post(
            KAFKA_CONNECT_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "name": CONNECTOR_NAME, #name of the connector
                    "config": {
                        "connector.class": "be.jovacon.kafka.connect.MQTTSinkConnector",
                        "mqtt.topic": args.mqtt_topic,
                        "topics": args.topic,
                        "mqtt.clientID": args.clientID,
                        "mqtt.broker": "tcp://mosquitto:1883",
                        "mqtt.qos": 2,
                        "mqtt.userName": "admin",
                        "mqtt.password": args.password,                
                        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
                        "key.converter.schemas.enable": False,
                        "value.converter": "org.apache.kafka.connect.storage.StringConverter",
                        "value.converter.schemas.enable": False,
                        # "value.converter": "io.confluent.connect.json.JsonSchemaConverter",
                        # "value.converter.schemas.enable": True,
                        "value.converter.schema.registry.url": "http://schema-registry:8081"


                        # "connector.class":"be.jovacon.kafka.connect.MQTTSinkConnector",
                        # "mqtt.topic":"my_mqtt_topic",
                        # "topics":"my_kafka_topic",
                        # "mqtt.clientID":"my_client_id",
                        # "mqtt.broker":"tcp://127.0.0.1:1883",
                        # "key.converter":"org.apache.kafka.connect.storage.StringConverter",
                        # "key.converter.schemas.enable":false,
                        # "value.converter":"org.apache.kafka.connect.storage.StringConverter",
                        # "value.converter.schemas.enable":false
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
