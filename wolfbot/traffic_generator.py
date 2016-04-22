#!/usr/bin/python

import sys
import paho.mqtt.client as paho
import json
import threading
import Queue
from time import sleep
from random import gauss
from random import randint
import numpy as np
import time


# queue of commands for inter thread communication
file_lock = threading.Lock()


# Create topic from bot_id
def get_topic(bot_id):
	return "wolfbot/" + bot_id + "/command"


# initialze a client and connect to the server
def prepare_mqttc(mqtt_host, bot_id, mqtt_port, command_q):
	# create a mqtt client
	mqttc = paho.Client(client_id="bot_" + bot_id, clean_session=True, userdata=command_q)
	mqttc.on_message = on_command
	mqttc.connect(host=mqtt_host, port=mqtt_port, keepalive=60)
	
	# subscribe to TOPIC
	topic = get_topic(bot_id)
	#print topic
	mqttc.subscribe(topic)
	
	return mqttc


# create request json
def create_pass_request(bot_id, bot_type, enter_lane, exit_lane):
	msg = {}
	msg["bot_id"] = bot_id
	msg["bot_type"] = bot_type
	msg["enter"] = enter_lane
	msg["exit"] = exit_lane
	msg["respond_to"] = get_topic(bot_id)
	
	return json.dumps(msg)


# create complete json
def create_complete_msg(bot_id, bot_type):
	msg = {}
	msg["bot_id"] = bot_id
	msg["bot_type"] = bot_type
	msg["status"] = "complete"
	
	return json.dumps(msg)


# The callback for when a PUBLISH message is received from the server.
def on_command(mqttc, userdata, msg):
	# userdata has the command_q
	command_q = userdata
	
	# parse the payload
	pass_comm = json.loads(msg.payload)
	
	# send a command to the driver thread
	if pass_comm["command"] == "go":
		command_q.put("GO_AT_RED")
	else :
		command_q.put("STOP_AT_RED")


# the driver function which controls the bot.
def driver(mqttc, bot_id, bot_type, entry_lane, exit_lane, command_q, log_fname):
	# check entry and exit lanes
	global file_lock
	logs  = []
	if entry_lane < 1 or entry_lane > 4 or exit_lane < 1 or exit_lane > 4 or entry_lane == exit_lane:
		print "Invalid entry or exit lane"
		return

	#journey_state : AT_SRC, NEED_BLACK, REQUEST, NEED_RED, WAITING, CROSSING, DEPARTING, AT_DEST
	journey_state = "REQUEST"
	
	# by default, stop at red
	command = "STOP_AT_RED"
	
	# loop to control the motion and sensors based on TIM command
	while (True):
		# check for any commands from master thread
		if command_q.empty() == False:
			command = command_q.get()
			
		# state machine using ifelse control
		if journey_state == "REQUEST":
			logs.append(bot_id)
			logs.append(bot_type)
			logs.append(int(time.time()))
			# at the start of the entry lane
			
			# request TIM to pass the intersection
			pass_req = create_pass_request(bot_id, bot_type, entry_lane, exit_lane)
			mqttc.publish("tim/jid_1/request", pass_req)
			journey_state = "WAITING"

		elif journey_state == "WAITING":
			# waiting at red line for a go command from TIM
			if command == "STOP_AT_RED":
				continue

			journey_state = "CROSSING"
			
		elif journey_state == "CROSSING":
			# sleep to simulate crossing
			sleep(3)
			logs.append(int(time.time()))
			journey_state = "COMPLETED"
			
		elif journey_state == "COMPLETED":
			complete_msg = create_complete_msg(bot_id, bot_type)
			mqttc.publish("tim/jid_1/complete", complete_msg)
			
			journey_state = "AT_DEST"
			
		elif journey_state == "AT_DEST":
			# log all the data
			file_lock.acquire()
			f = open(log_fname,'a')
			for i in range(0,4):
				f.write(str(logs[i]) + ",")
			f.write("\n")
			f.close()
			file_lock.release()

			# disconnect after reaching the destination
			mqttc.disconnect()
			
			print str(bot_id) + " COMPLETED"
			break


def generateSleepValues(n):
	return [randint(1,4) for x in range(n)]


def generateTrafficPerLane(enter_lane, n, log_fname):
	sleep_dur = generateSleepValues(n)

	for x in range(0, n):
		# create paramters for bot
		bot_id = str(enter_lane) + "_" + str(x)
		bot_type = "civilian"
		exit_lane = enter_lane
		while exit_lane == enter_lane:
			exit_lane = randint(1,4)

		# seaparate command queue for each bot
		command_q = Queue.Queue() # STOP_AT_RED, GO_AT_RED
		# separate mqtt client for each bot
		client = prepare_mqttc("localhost", bot_id, 1883, command_q)

		# create a thread for the driver function
		driver_thread = threading.Thread(target = driver, args = (client, bot_id, bot_type, enter_lane, exit_lane, command_q, log_fname))
		driver_thread.start()
		client.loop_forever()


# main function
def main():
	# check usage
	if len(sys.argv) != 3:
		print "usage : NUM_BOTS LOG_FILE"
		return
	
	n_bots = int(sys.argv[1])
	log_fname = sys.argv[2]

	threads = []

	for x in range(1, 5):
		thread = threading.Thread(target = generateTrafficPerLane, args = (x, n_bots, log_fname))
		thread.start()
		threads.append(thread)

	for thread in threads:
		thread.join()

	print "Simulation done"


if __name__ == "__main__":
	main()

