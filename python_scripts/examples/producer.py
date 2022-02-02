import json
import time
import random
from confluent_kafka import Producer

config = {
    'bootstrap.servers': 'merf.egs.anl.gov:9092',
}
producer = Producer(config)

for i in range(1000):
    schema = {
        "type": "struct",
        "fields": [
            {
                "type": "int32",
                "optional": False,
                "field": "id"
            },
            {
                "type": "double",
                "optional": False,
                "field": "time"
            },
            {
                "type": "int32",
                "optional": True,
                "field": "int1"
            },
            {
                "type": "int32",
                "optional": True,
                "field": "int2"
            },
            {
                "type": "int32",
                "optional": True,
                "field": "int3"
            },
        ],
        "optional": False,
        "name": "data"
    }
    dat = {
        "id": i,
        "time": time.time(),
        "int1": random.randint(0, 25),
        "int2": random.randint(25, 50),
        "int3": random.randint(50, 100)
    }
    val = {
        "schema": schema,
        "payload": dat
    }
    val_json = json.dumps(val)
    producer.produce('mdml-example1', value=val_json)
    # producer.produce('mdml-example1-duplicate', value=val_json)
    time.sleep(5)

producer.flush()

print("done")
