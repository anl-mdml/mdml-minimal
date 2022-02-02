import mdml_client as mdml
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.username_pw_set("admin", "adminpass")
# Connect to Mosquitto broker
client.connect("merf.egs.anl.gov", 1883, 60)
client.loop_start()

client.publish("MDML/EDBO/EXPERIMENTS", "test message")

print("sent one message")
import time
time.sleep(2)
client.disconnect()
