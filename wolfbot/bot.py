#!/usr/bin/python

import sys
import paho.mqtt.client as paho
import json
import threading

# Create topic from bot_id
def get_topic(bot_id):
	return "tim/wolfbot/" + bot_id + "/command"

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

# create request json
def create_pass_request(speed, enter_lane, exit_lane, topic):
	req = {}
	req["speed"] = speed
	req["enter"] = enter_lane
	req["exit"] = exit_lane
	req["respond_to"] = topic
	return req

# The callback for when a PUBLISH message is received from the server.
def on_command(client, userdata, msg):
	print msg.payload
	# parse the payload
	pass_comm = json.loads(msg.payload)
	if pass_comm["command"] == "GO":
		bot_state = "BOT_GO"
	else:
		bot_state = "BOT_STOP"

# the driver function which controls the bot accroding to the bot_state variable
def driver(client, bot_id, exit_lane):
	# create a dummy request to pass an intersection
	pass_req = create_pass_request(35, "yellow", exit_lane, get_topic(bot_id))
	
	# request TIM to cross
	client.publish("tim/27606/request", json.dumps(pass_req))
	
	# wait and disconnect after reaching the destination
	client.loop(2)
	client.disconnect()

# main function
def main():
	# process command line arguments
	if len(sys.argv) != 3:
		print "Usage : python tim.py <BOT_ID> <EXIT_LANE>"
		exit(1)
	bot_id = str(sys.argv[1])
	exit_lane = str(sys.argv[2])
	if exit_lane != "green" and exit_lane != "blue" and exit_lane != "yellow" and exit_lane != "magenta":
		print "Invalid exit lane : green, blue, yellow, magenta"
		exit(1)
	
	# get mqtt client
	client = prepare_client(bot_id)
	
	# create a thread for the driver function
	driver_thread = threading.Thread(target = driver, args = (client, bot_id, exit_lane))
	driver_thread.start()
	
	# Blocking call that processes network traffic, dispatches callbacks and
	# handles reconnecting.
	# Other loop*() functions are available that give a threaded interface and a
	# manual interface.
	client.loop_forever()
	
	print "Destination reached. Terminating"

if __name__ == "__main__":
	main()