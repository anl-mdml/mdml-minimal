from confluent_kafka import Consumer

consumerConfig = {
    'bootstrap.servers': 'merf.egs.anl.gov:9092',
    'group.id': 'foo',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(consumerConfig)

running = True

try:
    consumer.subscribe(['mdml-edbo-experiments'])
    # consumer.subscribe(['mdml-example1-jsonschema'])
    while running:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            print("error in message")
        else:
            print(f"TOPIC: {msg.topic()}")
            print(f"MESSAGE: {msg.value()}")
finally:
    consumer.close()
