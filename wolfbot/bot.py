import paho.mqtt.client as mqtt
import json

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("TIM/CAR/C_ID/COMMAND")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("Topic: ", msg.topic, "Message: ", str(msg.payload))

#client to subscribe to topic
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

# request TIM to cross

jsonstr = '{"speed":35,"enter":"yellow","exit":"blue"}'
jsonReading = json.loads(jsonstr)

#mqttc to publish on a topic
mqttc = mqtt.Client("python_pub")
mqttc.connect("localhost", 1883)
mqttc.publish("TIM/J_ID/REQUEST", json.dumps(jsonReading))
mqttc.loop(2)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
