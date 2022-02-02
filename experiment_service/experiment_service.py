import os
import json
import time
import boto3
import string
import random
import mdml_client as mdml
import threading
import multiprocessing
from adc_sdk.client import ADCClient

import logging
logging.basicConfig(
    filename="experiment.log", 
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %I:%M:%S %p %Z',
)

def experiment_spawner(connection_config={}, threads=False):
    experiments={}
    exp_consumer = mdml.kafka_mdml_consumer(["mdml-experiment-service"], "mdml-experiment-service", auto_offset_reset="latest", **connection_config)
    # Adding a producer to create a dashboard for easily determining which experiments are running
    experiment_status_schema = {
        "$schema": "http://merf.egs.anl.gov/mdml-experiment-status-schema#",
        "title": "ExperimentStatusSchema",
        "description": "Schema for Kafka MDML Experiment status updates",
        "type": "object",
        "properties": {
            "time": {
                "description": "Sent timestamp",
                "type": "number"
            },
            "experiment_id": {
                "description": "Argonne Data Cloud Sample ID",
                "type": "string"
            },
            "status": {
                "description": "Upload name",
                "type": "string"
            }
        },
        "required": [ "time", "status", "experiment_id" ]
    }
    status_producer = mdml.kafka_mdml_producer("mdml-experiment-status", schema=experiment_status_schema, **connection_config)
    for msg in exp_consumer.consume(overall_timeout=-1):
        logging.info(f"Message received: {msg}")
        if msg['value']['status'] == "on":
            try:
                experiment_start_time = msg['value']['mdml_time']
            except:
                experiment_start_time = time.time()

            logging.info(f"Experiment started: {msg}")
            #Message will contain topics to include under an experiment
            if threads:
                t = threading.Thread(target=experiment_task, args=(msg,connection_config,experiment_start_time,))
                experiments[msg['value']['experiment_id']] = t
                t.setDaemon(True)
                t.start()
                status_msg = {
                    'time': time.time(),
                    'experiment_id': msg['value']['experiment_id'],
                    'status': 'starting'
                }
                status_producer.produce(status_msg)
                status_producer.flush()

            else:
                p = multiprocessing.Process(target=experiment_task, args=(msg,connection_config,experiment_start_time,))
                experiments[msg['value']['experiment_id']] = p
                p.daemon = True
                p.start()
                status_msg = {
                    'time': time.time(),
                    'experiment_id': msg['value']['experiment_id'],
                    'status': 'starting'
                }
                status_producer.produce(status_msg)
                status_producer.flush()


def experiment_task(msg, connection_config, experiment_start_time):
    exp_id = msg['value']['experiment_id']
    log = open(f"mdml-experiment-{exp_id}.log", "w")
    log.write("Experiment started.\n")
    # First check if this experiment should continue an old one
    try:
        _, exp_msgs = mdml.get_experiment_data(exp_id, os.environ['ADC_SDL_TOKEN'])
    except:
        exp_msgs = []
    # Create consumers for the experiment's topics
    topics = msg['value']['topics']
    raw_topics = topics.copy()
    topics.append("mdml-experiment-service")
    exp_producer = mdml.kafka_mdml_producer_schemaless(f"mdml-experiment-{exp_id}", **{"kafka_host": connection_config['kafka_host']})
    exp_consumer = mdml.kafka_mdml_consumer(topics, f"mdml-experiment-{exp_id}", auto_offset_reset="latest", **connection_config)
    upload_url_schema = {
        "$schema": "http://merf.egs.anl.gov/mdml-experiment-upload-urls-schema#",
        "title": "ExperimentUploadURLSchema",
        "description": "Schema for Kafka MDML Experiment upload URL list",
        "type": "object",
        "properties": {
            "time": {
                "description": "Sent timestamp",
                "type": "number"
            },
            "id": {
                "description": "Argonne Data Cloud Sample ID",
                "type": "string"
            },
            "name": {
                "description": "Upload name",
                "type": "string"
            },
            "user_name": {
                "description": "Upload user name",
                "type": "string"
            },
            "user_email": {
                "description": "Upload user email",
                "type": "string"
            },
            "url": {
                "description": "Upload URL",
                "type": "string"
            }
        },
        "required": [ "time", "name", "user_name", "user_email", "url", "id" ]
    }
    url_producer = mdml.kafka_mdml_producer("mdml-experiment-upload-urls", schema=upload_url_schema, **connection_config)
    experiment_status_schema = {
        "$schema": "http://merf.egs.anl.gov/mdml-experiment-status-schema#",
        "title": "ExperimentStatusSchema",
        "description": "Schema for Kafka MDML Experiment status updates",
        "type": "object",
        "properties": {
            "time": {
                "description": "Sent timestamp",
                "type": "number"
            },
            "experiment_id": {
                "description": "Argonne Data Cloud Sample ID",
                "type": "string"
            },
            "status": {
                "description": "Upload name",
                "type": "string"
            }
        },
        "required": [ "time", "status", "experiment_id" ]
    }
    status_producer = mdml.kafka_mdml_producer("mdml-experiment-status", schema=experiment_status_schema, **connection_config)
    log.write("Producer & consumer created.\n")
    num_msgs = 0
    log.write("Starting consumer...\n")
    status_msg = {
        'time': time.time(),
        'experiment_id': exp_id,
        'status': 'active'
    }
    status_producer.produce(status_msg)
    status_producer.flush()
    for msg in exp_consumer.consume(overall_timeout=-1, verbose=False):
        if msg['topic'] == "mdml-experiment-service":
            print(f"STOP MSG: {msg}")
            if msg['value']['status'] == "off" and msg['value']['experiment_id'] == exp_id:
                exp_producer.flush()
                experiment_stop_time = msg['value']['mdml_time']
                log.write(f"Experiment stopped: {msg}")
                break
        else:
            num_msgs += 1
            log.write(json.dumps(msg))
            exp_producer.produce(json.dumps(msg))
            exp_msgs.append(msg)
            # Determine optimal strategy for flushing 
            if num_msgs % 500 == 0:
                exp_producer.flush()
    exp_consumer.close()
    
    # Send status tag
    closing_status_msg = {
        'time': time.time(),
        'experiment_id': exp_id,
        'status': 'closing'
    }
    status_producer.produce(closing_status_msg)
    status_producer.flush()
    # Create data file
    with open(f"mdml-experiment-{exp_id}.json", "w") as f:
        json.dump(exp_msgs, f)

    # Upload to BIS StorageGrid
    try:
        # Load credentials for StorageGrid 
        access_key = os.environ['STORAGE_GRID_ACCESS_KEY']
        secret_key = os.environ['STORAGE_GRID_SECRET_KEY']
        
        # Create boto3 client
        s3 = boto3.client('s3', 
            region_name='us-east-1',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url='https://s3.it.anl.gov:18082')
        s3.upload_file(
            Filename=f"./mdml-experiment-{exp_id}.json",
            Bucket="mdml-experiments",
            Key=f"mdml-experiment-{exp_id}.json")
    except:
        log.write(f"\nFailed to upload experiment {exp_id} to BIS StorageGrid.")
    # Send status tags
    completed_status_msg = {
        'time': time.time(),
        'experiment_id': exp_id,
        'status': 'completed'
    }
    status_producer.produce(completed_status_msg)
    status_producer.flush()
    
    ### Verifying experiment data
    # Create random group to pull all data
    group = ''.join(random.choices(string.ascii_uppercase + string.digits, k=24))
    verify_consumer = mdml.kafka_mdml_consumer(raw_topics, group, **connection_config)
    verify_msgs = []
    print(f"start: {experiment_start_time}")
    for msg in verify_consumer.consume(overall_timeout=60, verbose=False):
        if experiment_start_time <= msg['value']['mdml_time'] and experiment_stop_time >= msg['value']['mdml_time']:
            print(msg)
            verify_msgs.append(msg)
    print(f"stop: {experiment_stop_time}")

    if len(exp_msgs) < len(verify_msgs):
        print(f"Verify step found {len(verify_msgs) - len(exp_msgs)} new messages")
        log.write("Verify step found new messages.")
        # Recreate data file
        with open(f"mdml-experiment-{exp_id}.json", "w") as f:
            json.dump(verify_msgs, f)
        try:
            s3.upload_file(
                Filename=f"./mdml-experiment-{exp_id}.json",
                Bucket="mdml-experiments",
                Key=f"mdml-experiment-{exp_id}.json")
        except:
            log.write(f"\nFailed to upload experiment {exp_id} to BIS StorageGrid.")
    elif len(exp_msgs) > len(verify_msgs):
        print("Verify cannot find all messages. VERY WEIRD!")
        log.write("Verify cannot find all messages. VERY WEIRD!")
    else:
        print("Verify step completed with no issues found.")
        log.write("Verify step completed with no issues found.")

    # Upload to Argonne Data Cloud                
    try:
        client = ADCClient(os.environ['ADC_SDL_TOKEN'])
        log.write(f"Upload experiment")
        with open(f"mdml-experiment-{exp_id}.json", 'rb') as f:
            # ADC MDML Experiment Study ID - U3R1ZHlOb2RlOjMx
            sample = client.create_sample(f,"U3R1ZHlOb2RlOjMx",f"MDML experiment {exp_id}")
        log.write(f"Sample response: {sample}")
        d = {
            "time": time.time(),
            "id": sample['sample']['id'],
            "name": sample['sample']['name'],
            "user_name": sample['sample']['user']['name'],
            "user_email": sample['sample']['user']['email'],
            "url": sample['sample']['url'],
        }
        url_producer.produce(d)
        url_producer.flush()
    except:
        log.write(f"\nFailed to upload experiment {exp_id} to Argonne Discovery Cloud")

    # Send status tags
    inactive_status_msg = {
        'time': time.time(),
        'experiment_id': exp_id,
        'status': 'inactive'
    }
    status_producer.produce(inactive_status_msg)
    status_producer.flush()
    # Remove temp file
    # os.remove(f"mdml-experiment-{exp_id}.json")
    log.close()

import os
host = os.environ['HOST']
schema_host = os.environ['SCHEMA_HOST']
connection_config = {
    'kafka_host': host,
    'schema_host': schema_host
}
logging.info(f"Starting experiment service with connection config: {connection_config}")        
experiment_spawner(connection_config)