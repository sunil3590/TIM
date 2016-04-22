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
	for x in range(1,5):
		if (x == 1) and (enterLane == 1):
        		time.sleep(0)
		if (x == 1) and (enterLane == 2):
        		time.sleep(0.25)
		if (x == 1) and (enterLane == 3):
        		time.sleep(0.5)
		if (x == 1) and (enterLane == 4):
        		time.sleep(0.75)
        	if enterLane == 1:
                	bot_id = x
        	elif enterLane == 2:
                	bot_id = x+50
        	elif enterLane == 3:
                	bot_id = x+100
        	else:
                	bot_id = x+150
		exit_lane = enterLane
        	while exit_lane == enterLane:
			exit_lane = randint(1,4)

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
	#print msg.payload
	
	# parse the payload
	pass_comm = json.loads(msg.payload)
	
	# send a command to the driver thread
	if pass_comm["command"] == "go":
		command_q.put("GO_AT_RED")
	else :
		command_q.put("STOP_AT_RED")
		print("STOP")

# the driver function which controls the bot.
def driver(mqttc, bot_id, bot_type, entry_lane, exit_lane, command_q):
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
			logs.append(time.asctime(time.localtime(time.time())))
			# at the start of the entry lane
			
			# request TIM to pass the intersection
			pass_req = create_pass_request(bot_id, bot_type, entry_lane, exit_lane)
			mqttc.publish("tim/jid_1/request", pass_req)
			journey_state = "WAITING"
			print str(bot_id) + " REQUESTED"

		elif journey_state == "WAITING":
			# waiting at red line for a go command from TIM
			#print str(bot_id) + "WAITING"
			if command == "STOP_AT_RED":
				continue
			else :
				print ("GO " + bot_id)
			journey_state = "CROSSING"
			
		elif journey_state == "CROSSING":
			# sleep to simulate crossing
			#print str(bot_id) + " CROSSING"
			sleep(3)
			logs.append(time.asctime(time.localtime(time.time())))
			journey_state = "COMPLETED"
			
		elif journey_state == "COMPLETED":
			complete_msg = create_complete_msg(bot_id, bot_type)
			mqttc.publish("tim/jid_1/complete", complete_msg)
			print ("COMPLETED " + str(bot_id))
			
			journey_state = "AT_DEST"
			
		elif journey_state == "AT_DEST":
			file_lock.acquire()
			f = open("log.txt",'a')
			for i in range(0,4):
				f.write(str(logs[i])+" , ")
			f.write("\n")
			file_lock.release()
			#print ("AT_DEST " + str(bot_id))
                        
                        # disconnect after reaching the destination
			mqttc.disconnect()
			
			break


sleepRed = generateSleepValues()
sleepGreen = generateSleepValues()
sleepBlue = generateSleepValues()
sleepMagenta = generateSleepValues()

threadForLane1 = threading.Thread(target = generateTrafficPerLane, args = (1, sleepBlue))
threadForLane1.start()
threadForLane2 = threading.Thread(target = generateTrafficPerLane, args = (2, sleepGreen))
threadForLane2.start()
threadForLane3 = threading.Thread(target = generateTrafficPerLane, args = (3, sleepRed))
threadForLane3.start()
threadForLane4 = threading.Thread(target = generateTrafficPerLane, args = (4, sleepMagenta))
threadForLane4.start()

print "bye bye"

threadForLane1.join()
threadForLane2.join()
threadForLane3.join()
threadForLane4.join()

print "bye bye"
