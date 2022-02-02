import mdml_client as mdml
# import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe

# client = mqtt.Client()
# client.username_pw_set("admin", "adminpass")
# Connect to Mosquitto broker
# client.connect("merf.egs.anl.gov", 1883, 60)
# client.loop_start()

# client.publish("MDML/EDBO/EXPERIMENTS", "test message")

# print("sent one message")

def on_message_print(client, userdata, message):
    print("%s %s" % (message.topic, message.payload))
    print(type(message.payload))
    print(message.payload.decode('utf-8'))

subscribe.callback(on_message_print, "MDML/EDBO/EXPERIMENTS", hostname="merf.egs.anl.gov", 
                    auth={"username":'admin', "password":'adminpass'})


# client.disconnect()