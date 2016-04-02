#!/usr/bin/python

import sys
import paho.mqtt.client as paho
import json

# Create topic from bot_id
def get_topic(bot_id):
	return "tim/wolfbot/" + bot_id + "/command"

# The callback for when a PUBLISH message is received from the server.
def on_command(client, userdata, msg):
	print msg.payload

# create request json
def create_pass_request(speed, enter, exit, topic):
	req = {}
	req["speed"] = speed
	req["enter"] = enter
	req["exit"] = exit
	req["respond_to"] = topic
	return req

# initialze a client and connect to the server
def prepare_client(bot_id):
	client = paho.Client(client_id="bot_" + bot_id)
	client.on_message = on_command
	client.connect(host="localhost", port=1883, keepalive=60)
	# TOPIC to subscribe to
	topic = get_topic(bot_id)
	print topic
	client.subscribe(topic)
	return client

# process command line arguments
if len(sys.argv) != 2:
	print("Usage : python tim.py <BOT_ID>")
bot_id = str(sys.argv[1])

# get mqtt client
client = prepare_client(bot_id)

# create a dummy request to pass an intersection
pass_req = create_pass_request(35, "yellow", "blue", get_topic(bot_id))

# request TIM to cross
client.publish("tim/27606/request", json.dumps(pass_req))
client.loop(2)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
