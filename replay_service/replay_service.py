import os
import boto3
import time
import json
import requests
import threading
import multiprocessing

import logging
logging.basicConfig(filename="replay.log", level=logging.INFO)

import mdml_client as mdml
from adc_sdk.client import ADCClient

def replay_spawner(connection_config={}, threads=False):
    replays = {}
    consumer = mdml.kafka_mdml_consumer(["mdml-replay-service"], "mdml-replay-service", auto_offset_reset="latest", **connection_config)
    logging.info("Consumer created.")
    for msg in consumer.consume(overall_timeout=-1):
        logging.info(msg)
        # Message will contain experiment topic
        if threads:
            t = threading.Thread(target=replay_experiment, args=(msg,connection_config,))
            replays[msg['value']['experiment_id']] = t
            t.setDaemon(True)
            t.start()
        else:
            p = multiprocessing.Process(target=replay_experiment, args=(msg,connection_config,))
            replays[msg['value']['experiment_id']] = p
            p.daemon = True
            p.start()
            

def replay_experiment(msg, connection_config):
    exp_id = msg['value']['experiment_id']
    speed = int(msg['value']['speed'])
    log = open(f"replay_{exp_id}.log", "w")
    data = json.load(f"experiment_files/mdml-experiment-{exp_id}.json")
    topics = []
    producers = {}
    # Un-nest the time field for easy sorting
    for d in data:
        d['time'] = d['value']['time']
        # Build a list of topics
        if d['topic'] not in topics:
            topics.append(d['topic'])
    data = sorted(data, key=lambda k: k['time'])
    real_start_timestamp = data[0]['time']
    for d in data:
        d['time_diff'] = (d['time'] - real_start_timestamp)/speed
    # Create producers
    for topic in topics:
        producers[topic] = mdml.kafka_mdml_producer(topic, **connection_config)
    sim_start_timestamp = time.time()
    log.write(f"\nSTARTING SIMULATION {time.time()}\n")
    while len(data) > 0:
        if data[0]['time_diff'] <= time.time() - sim_start_timestamp:
            log.write(f"TIMEDIFF: {data[0]['time_diff']} SENT: {data[0]['value']}\n")
            producers[data[0]['topic']].produce(data[0]['value'])
            producers[data[0]['topic']].flush()
            del data[0]
    log.close()
    return


import os
host = os.environ['HOST']
schema_host = os.environ['SCHEMA_HOST']
connection_config = {
    'kafka_host': host,
    'schema_host': schema_host
}
logging.info(f"Starting replay service with connection config: {connection_config}")        
replay_spawner(connection_config, threads=False)
