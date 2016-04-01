#!/usr/bin/python

import sys
import paho.mqtt.client as mqtt
import json

# The callback for when a PUBLISH message is received from the server.
def on_command(client, userdata, msg):
	print msg.payload

# process command line arguments
if len(sys.argv) != 2:
	print("Usage : python tim.py <BOT_ID>")
bot_id = str(sys.argv[1])

# TOPIC to subscribe to
topic = "tim/wolfbot/" + bot_id + "/command"
print topic

# initialze a client and connect to the server
client = mqtt.Client(client_id="bot_" + bot_id)
client.on_message = on_command
client.connect(host="localhost", port=1883, keepalive=60)
client.subscribe(topic)

# create request json
jsonstr = '{"speed":35,"enter":"yellow","exit":"blue"}'
jsonReading = json.loads(jsonstr)

# request TIM to cross
client.publish("tim/27606/request", "{speed:35,enter:yellow,exit:blue}")
client.loop(2)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
