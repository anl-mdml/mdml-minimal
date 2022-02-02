import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-t", help="topic to delete",
                        dest="topic", required=True)
parser.add_argument("-s", help="MDML server",
                        dest="server", required=True)
args = parser.parse_args()

from confluent_kafka.admin import AdminClient

config = {
    "bootstrap.servers": f"{args.server}:9092"
}
client = AdminClient(config)

res = client.delete_topics([args.topic], operation_timeout=10.0)

for topic, fut in res.items():
    try:
        if fut.result() is None:
            print(f"Topic: {topic} successfully deleted.")
    except Exception as e:
        print(e)
