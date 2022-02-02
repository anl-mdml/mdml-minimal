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
    # Pull data from BIS StorageGrid
    try:
        bucket = "mdml-experiments"
        # Load credentials for StorageGrid 
        access_key = os.environ['STORAGE_GRID_ACCESS_KEY']
        secret_key = os.environ['STORAGE_GRID_SECRET_KEY']
        # Create boto3 client
        s3 = boto3.client('s3', 
            region_name='us-east-1',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url='https://s3.it.anl.gov:18082')
        download_resp = s3.download_file(
            Bucket=bucket,
            Key=f"mdml-experiment-{exp_id}.json", 
            Filename=f"{exp_id}.json"
        )
        if download_resp is not None:
            raise Exception("Experiment file could not be downloaded")
        with open(f"{exp_id}.json") as f:
            data = json.load(f)
    except:
        print("Error pulling data from StorageGrid")
        log.write("Error pulling data from StorageGrid")
        return
    # # Pull from Argonne Data Cloud             
    # try:
    #     client = ADCClient(os.environ['ADC_SDL_TOKEN'])
    #     # ADC MDML Experiment Study ID - U3R1ZHlOb2RlOjMx
    #     sample = client.get_sample(adc_sample_id)
    #     res = requests.get(sample['sample']['url'], verify=False)                
    #     log.write(res.text)
    #     data = res.json()
    #     log.write(json.dumps(data))
    # except:
    #     log.write()

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