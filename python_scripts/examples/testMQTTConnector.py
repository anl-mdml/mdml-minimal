import json
import time
import mdml_client as mdml
import paho.mqtt.subscribe as subscribe

data_schema = {
    "$schema": "http://merf.egs.anl.gov/mdml-mqtt-test-connector-data-schema#",
    "title": "MQTT_TEST",
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
    topic = "mdml-test-mqtt-connector",
    schema = data_schema)

producer.produce({
    "time": time.time(),
    "int1": 1,
    "int2": 2
})
producer.flush()

print("sent kafka message")

def on_message_print(client, userdata, message):
    dat = json.loads(message.payload.decode('utf-8'))
    print(dat)

subscribe.callback(on_message_print, "MDML/TEST/MQTT/CONNECTOR", hostname="merf.egs.anl.gov", 
                    auth={"username":'admin', "password":'adminpass'})
