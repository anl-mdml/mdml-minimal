import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-i", help="ID of the schema", dest="id", required=True)
parser.add_argument("-s", help="MDML server", dest="server", required=True)
args = parser.parse_args()

from confluent_kafka.schema_registry import SchemaRegistryClient
config = {
    "url": f"http://{args.server}:8081"
}
client = SchemaRegistryClient(config)
subject = client.get_schema(args.id)
print(subject.schema_str)