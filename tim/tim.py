#!/usr/bin/python

import sys
import paho.mqtt.client as paho

# The callback for when a PUBLISH message is received from the server.
def on_request(client, userdata, msg):
    print msg.payload
    # send a command to wolfbot
    # TODO : extract data from payload, dont hard code the bot id
    client.publish("tim/wolfbot/1/command", "STOP")
    client.loop(2)

# process command line arguments
if len(sys.argv) != 2:
    print("Usage : python tim.py <POSTAL_CODE>")
postal = str(sys.argv[1])

# TOPIC to subscribe to
topic = "tim/" + postal + "/request"
print topic

# initialze a client and connect to the server
client = paho.Client(client_id="tim_" + postal + "_sub")
client.on_message = on_request
client.connect(host="localhost", port=1883, keepalive=60)
client.subscribe(topic)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()