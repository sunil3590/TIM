#!/usr/bin/python

import sys
import paho.mqtt.client as paho
import json
import threading
import Queue

# queue of commands for inter thread communication
command_q = Queue.Queue() # STOP_AT_RED, GO_AT_RED

# Create topic from bot_id
def get_topic(bot_id):
	return "wolfbot/" + bot_id + "/command"

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
	return json.dumps(req)

# create notify json
def create_notify_msg():
	msg = {}
	msg["status"] = "crossed"
	return json.dumps(msg)

# The callback for when a PUBLISH message is received from the server.
def on_command(client, userdata, msg):
	print msg.payload
	# parse the payload
	pass_comm = json.loads(msg.payload)
	if pass_comm["command"] == "go":
		command_q.put("GO_AT_RED")
	else:
		command_q.put("STOP_AT_RED")

# the driver function which controls the bot.
def driver(client, bot_id, entry_lane, exit_lane, command_q):
	bot_id = str(bot_id)
	#journey_state : AT_SRC, APPROACHING, WAITING, CROSSING, DEPARTING, AT_DEST
	journey_state = "AT_SRC"
	command = "STOP_AT_RED"
	while (True):
		if command_q.empty() == False:
			command = command_q.get()
		if journey_state == "AT_SRC":
			# print "AT_SRC"
			journey_state = "APPROACHING"
		elif journey_state == "APPROACHING":
			# print "APPROACHING"
			# TODO : handle all colors and the distance lines
			# request TIM to pass the intersection
			pass_req = create_pass_request(35, entry_lane, exit_lane, get_topic(bot_id))
			client.publish("tim/27606/request", pass_req)
			journey_state = "WAITING"
		elif journey_state == "WAITING":
			# print "WAITING"
			if command == "STOP_AT_RED":
				continue
			journey_state = "CROSSING"
		elif journey_state == "CROSSING":
			# print "CROSSING"
			notify_msg = create_notify_msg()
			client.publish("tim/27606/notify", notify_msg)
			journey_state = "DEPARTING"
		elif journey_state == "DEPARTING":
			# print "DEPARTING"
			# TODO :  go for a certain distance (18 inches?)
			journey_state = "AT_DEST"
		elif journey_state == "AT_DEST":
			# print "AT_DEST"
			# wait and disconnect after reaching the destination
			client.loop(2)
			client.disconnect()
			break

# main function
def main():
	# process command line arguments
	if len(sys.argv) != 4:
		print "Usage : python tim.py <BOT_ID> <ENTRY_LANE> <EXIT_LANE>"
		exit(1)

	bot_id = sys.argv[1]
	entry_lane = int(sys.argv[2])
	exit_lane = int(sys.argv[3])
	if exit_lane > 4 or exit_lane < 1:
		print "Invalid exit lane : 1 to 4"
		exit(1)
	if entry_lane > 4 or entry_lane < 1:
		print "Invalid exit lane : 1 to 4"
		exit(1)
	
	# get mqtt client
	client = prepare_client(bot_id)
	
	# create a thread for the driver function
	driver_thread = threading.Thread(target = driver, args = (client, bot_id, entry_lane, exit_lane, command_q))
	driver_thread.start()
	
	# Blocking call that processes network traffic, dispatches callbacks and
	# handles reconnecting.
	# Other loop*() functions are available that give a threaded interface and a
	# manual interface.
	client.loop_forever()
	
	print "Destination reached. Terminating"

if __name__ == "__main__":
	main()
