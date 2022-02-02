import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-n", help="topic name of the schema",
                        dest="name", required=True)
parser.add_argument("-s", help="MDML server",
                        dest="server", required=True)
args = parser.parse_args()

from confluent_kafka.schema_registry import SchemaRegistryClient
config = {
    "url": f"http://{args.server}:8081"
}
client = SchemaRegistryClient(config)

my_schema = client.get_latest_version(args.name+'-value')
print(my_schema.schema.schema_str)

