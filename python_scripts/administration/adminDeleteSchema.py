#!/usr/bin/env python
import argparse

def main(args):
    from confluent_kafka.schema_registry import SchemaRegistryClient
    config = {
        "url": f"http://{args.server}:{args.port}"
    }
    client = SchemaRegistryClient(config)

    res = client.delete_subject(args.topic+'-value')#, permanent=True)
    print(f"version deleted {res}")
    
    
    # # delete schema with 
    # # curl -X DELETE http://localhost:8081/subjects/<schema-name>
    # import os
    # os.system(f"curl -X DELETE http://{args.server}:{args.port}/subjects/{args.topic}-value")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Admin tool to delete a schema in the Schema Registry")
    parser.add_argument('-t', dest="topic", required=True,
                        help="Kafka Topic for which to delete the schema")
    parser.add_argument('-s', dest="server", required=True,
                        help="Schema Registry server")
    parser.add_argument('-p', dest="port", default=8081,
                        help="Schema Registry port number")
    main(parser.parse_args())