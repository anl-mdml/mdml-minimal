import asyncio
import requests
import json

KAFKA_CONNECT_URL = "http://merf.egs.anl.gov:8083/connectors"
CONNECTOR_NAME = "file_stream_connector"

def configure_connector():
    """Calls Kafka Connect to create a Connector"""
    resp = requests.get(f"{KAFKA_CONNECT_URL}/{CONNECTOR_NAME}")
    if resp.status_code == 200:
        return
    else:
        print(f'{resp.status_code}')

    #
    #
    #
    #
    #
    resp = requests.post(
        KAFKA_CONNECT_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "name": CONNECTOR_NAME,
                "config": {
                    "connector.class": "FileStreamSource", # the java class, see the docs 
                    "topic": "MDML_log_stream_topic", # topic the connector will write new lines to
                    "tasks.max": 1, #number of tasks to run in parallel
                    "file": f"/tmp/{CONNECTOR_NAME}.log", # file that will be the source
                    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
                    "key.converter.schemas.enable": "false",
                    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
                    "value.converter.schemas.enable": "false",
                }
            }
        )
    )

    # Success?
    resp.raise_for_status()
    print("Connector created")

async def log():
    """Continually appends to the end of a file"""
    with open(f"/tmp/{CONNECTOR_NAME}.log", "w") as f:
        iteration = 0
        while True:
            f.write(f"line number {iteration}\n")
            f.flush()
            await asyncio.sleep(5.0)
            iteration += 1

async def log_task():
    """Runs log task"""
    task = asyncio.create_task(log())
    configure_connector()
    await task

def run():
    """Run everything"""
    try:
        asyncio.run(log_task())
    except KeyboardInterrupt:
        print("shut down")

if __name__ == "__main__":
    run()