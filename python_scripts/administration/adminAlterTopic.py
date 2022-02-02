import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-t", help="topic to create",
                        dest="topic", required=True)
parser.add_argument("-p", help="number of partitions",
                        dest="partitions", default=1)
parser.add_argument("-r", help="retention in ms",
                        dest="retention", default=604800000)
parser.add_argument("-s", help="MDML server",
                        dest="server", required=True)
args = parser.parse_args()

from confluent_kafka.admin import AdminClient, NewTopic, ConfigResource

config = {
    "bootstrap.servers": f"{args.server}:9092"
}
client = AdminClient(config)

topic = NewTopic(
    topic = args.topic,
    num_partitions = int(args.partitions),
    config = {
        'retention.ms': str(args.retention)
    })

res = client.alter_configs([topic])

for topic, fut in res.items():
    try:
        if fut.result() is None:
            print(f"Topic: {topic} successfully created.")
    except Exception as e:
        print(e)
