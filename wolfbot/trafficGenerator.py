#!/usr/bin/python

import sys
import paho.mqtt.client as paho
import json
import threading
import Queue
#import motion
#import sensor
from time import sleep
from random import gauss
from random import randint
import numpy as np
import time


numberOfVehiclesInLane1 = 0
numberOfVehiclesInLane2 = 0
numberOfVehiclesInLane3 = 0
numberOfVehiclesInLane4 = 0

# queue of commands for inter thread communication
command_q = Queue.Queue() # STOP_AT_RED, GO_AT_RED

def generateSleepValues():
        values = []
        sleep = []
        values = np.random.normal(30,15,50)
        values.sort()

        sleep.append(round(values[0],2))

	sleep[0] = 0

        for x in range(1,50):
                sleep.append(round((values[x]-values[x-1]),1))
        return sleep

def generateTrafficPerLane(enterLane, sleep):
	for x in range(0,50):
        	time.sleep(sleep[x])
        	if enterLane == 1:
                	bot_id = x
        	elif enterLane == 2:
                	bot_id = x+50
        	elif enterLane == 3:
                	bot_id = x+100
        	else:
                	bot_id = x+150
		flag = True
        	while flag:
			exit_lane = randint(1,4)
			if exit_lane != enterLane :
				flag = False

        	# get mqtt client
        	client = prepare_mqttc("localhost",str(bot_id),1883)
        	bot_type = "civilian"

        	# create a thread for the driver function
        	driver_thread = threading.Thread(target = driver, args = (client, str(bot_id), bot_type, enterLane, exit_lane, command_q))
        	driver_thread.start()
        	client.loop_forever()

# Create topic from bot_id
def get_topic(bot_id):
	return "wolfbot/" + bot_id + "/command"

# initialze a client and connect to the server
def prepare_mqttc(mqtt_host, bot_id, mqtt_port):
	# create a mqtt client
	mqttc = paho.Client(client_id="bot_" + bot_id)
	mqttc.on_message = on_command
	mqttc.connect(host=mqtt_host, port=mqtt_port, keepalive=60)
	
	# subscribe to TOPIC
	topic = get_topic(bot_id)
	print topic
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
	print msg.payload
	
	# parse the payload
	pass_comm = json.loads(msg.payload)
	
	# send a command to the driver thread
	if pass_comm["command"] == "go":
		command_q.put("GO_AT_RED")
	elif pass_comm["command"] == "dec":
		command_q.put("DEC")
	else :
		command_q.put("STOP_AT_RED")

# the driver function which controls the bot.
def driver(mqttc, bot_id, bot_type, entry_lane, exit_lane, command_q):
	# check entry and exit lanes
	global numberOfVehiclesInLane1
	global numberOfVehiclesInLane2
	global numberOfVehiclesInLane3
	global numberOfVehiclesInLane4
	print entry_lane
	print exit_lane
	if entry_lane < 1 or entry_lane > 4 or exit_lane < 1 or exit_lane > 4 or entry_lane == exit_lane:
		print "Invalid entry or exit lane"
		return

	#journey_state : AT_SRC, NEED_BLACK, REQUEST, NEED_RED, WAITING, CROSSING, DEPARTING, AT_DEST
	journey_state = "AT_SRC"
	
	# by default, stop at red
	command = "STOP_AT_RED"
	
	# loop to control the motion and sensors based on TIM command
	while (True):
		# check for any commands from master thread
		if command_q.empty() == False:
			command = command_q.get()
			
		# state machine using ifelse control
		numberOfVehiclesAheadOfMe = 0
		if journey_state == "AT_SRC":
			print ("At source")
			# at the start of the entry lane
			#bot_motion.start()
			if entry_lane == 1:
				numberOfVehiclesAheadOfMe = numberOfVehiclesInLane1
				numberOfVehiclesInLane1 += 1
			elif entry_lane == 2 :
				numberOfVehiclesAheadOfMe = numberOfVehiclesInLane2
				numberOfVehiclesInLane2 += 1
			elif entry_lane == 3 :
				numberOfVehiclesAheadOfMe = numberOfVehiclesInLane3
				numberOfVehiclesInLane3 += 1
			elif entry_lane == 4 :
				numberOfVehiclesAheadOfMe = numberOfVehiclesInLane4
				numberOfVehiclesInLane4 += 1

			journey_state = "NEED_BLACK"
			
		elif journey_state == "NEED_BLACK":
			print ("Need Black")
			# moving on the entry lane up until red line, also make request to TIM
			# keep waiting till first black line
			if (numberOfVehiclesAheadOfMe != 0) and (command == "DEC") :
				numberOfVehiclesAheadOfMe -= 1
				if numberOfVehiclesAheadOfMe > 5 :
					continue
				else :
					journey_state = "REQUEST"
			elif numberOfVehiclesAheadOfMe == 0 :
				journey_state = "REQUEST"
			else :
				continue

		elif journey_state == "REQUEST":
			print ("Request")
			# request TIM to pass the intersection
			pass_req = create_pass_request(bot_id, bot_type, entry_lane, exit_lane)
			mqttc.publish("tim/jid_1/request", pass_req)
			journey_state = "NEED_RED"

		elif journey_state == "NEED_RED":
			print ("NEED RED")
			# keep waiting till you come across red line
			if (numberOfVehiclesAheadOfMe != 0) and (command == "DEC") :
				numberOfVehiclesAheadOfMe -= 1
				if numberOfVehiclesAheadOfMe != 0:
					continue
				else :
					journey_state = "WAITING"
			elif numberOfVehiclesAheadOfMe == 0 :
				journey_state = "WAITING"
			else :
				continue
			
		elif journey_state == "WAITING":
			print ("Waiting")
			# waiting at red line for a go command from TIM
			if command == "STOP_AT_RED":
				continue
			journey_state = "CROSSING"
			
		elif journey_state == "CROSSING":
			print ("CROSSING")
			# left / right / straight logic
			sleep(0.5)
			journey_state = "DEPARTING"
			
		elif journey_state == "DEPARTING":
			print ("Departin")
			sleep(1)
			complete_msg = create_complete_msg(bot_id, bot_type)
			mqttc.publish("tim/jid_1/complete", complete_msg)
			
			# travel for 3 more sec on the exit lane bofore stopping
			# TODO :  caliberate
			sleep(3) # sleep because there is nothing else to do
			journey_state = "AT_DEST"
			
		elif journey_state == "AT_DEST":
			# on reaching the end of the exit lane
			#bot_motion.stop()
			sleep(0.5)
			# disconnect after reaching the destination
			mqttc.disconnect()
			break


sleepRed = generateSleepValues()
sleepGreen = generateSleepValues()
sleepBlue = generateSleepValues()
sleepMagenta = generateSleepValues()
print(sleepBlue)
print(sleepGreen)
print(sleepRed)
print(sleepMagenta)

threadForLane1 = threading.Thread(target = generateTrafficPerLane, args = (1, sleepBlue))
threadForLane1.start()
threadForLane1 = threading.Thread(target = generateTrafficPerLane, args = (2, sleepGreen))
threadForLane1.start()
threadForLane1 = threading.Thread(target = generateTrafficPerLane, args = (3, sleepRed))
threadForLane1.start()
threadForLane1 = threading.Thread(target = generateTrafficPerLane, args = (4, sleepMagenta))
threadForLane1.start()

