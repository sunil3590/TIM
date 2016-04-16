#!/usr/bin/python

import sys
import paho.mqtt.client as paho
import json
import threading
import Queue
import motion
import sensor
from time import sleep

# queue of commands for inter thread communication
command_q = Queue.Queue() # STOP_AT_RED, GO_AT_RED

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
def create_complete_msg(bot_id):
	msg = {}
	msg["bot_id"] = bot_id
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
	else:
		command_q.put("STOP_AT_RED")

# the driver function which controls the bot.
def driver(mqttc, bot_id, bot_type, entry_lane, exit_lane, command_q):
	# check entry and exit lanes
	if entry_lane < 1 or entry_lane > 4 or exit_lane < 1 or exit_lane > 4 or entry_lane == exit_lane:
		print "Invalid entry or exit lane"
		return

	# motion object to achieve line following
	bot_motion = motion.Motion()
	if bot_motion.valid == False:
		print "Error in creating Motion object"
		mqttc.disconnect()
		return

	# give time to manually align the bot
	print "Manually align the bot"
	sleep(3)
	
	# sensor object to read markings on road
	bot_sensor = sensor.Sensor()

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
		if journey_state == "AT_SRC":
			# at the start of the entry lane
			bot_motion.start()
			journey_state = "NEED_BLACK"
			
		elif journey_state == "NEED_BLACK":
			# moving on the entry lane up until red line, also make request to TIM
			# keep waiting till first black line
			if bot_sensor.is_Black() == False:
				continue
			journey_state = "REQUEST"

		elif journey_state == "REQUEST":
			# request TIM to pass the intersection
			pass_req = create_pass_request(bot_id, bot_type, entry_lane, exit_lane)
			mqttc.publish("tim/jid_1/request", pass_req)
			journey_state = "NEED_RED"

		elif journey_state == "NEED_RED":
			# keep waiting till you come across red line
			if bot_sensor.is_Red() == False:
				continue
			
			# stop the bot and go to wait state
			bot_motion.stop()
			journey_state = "WAITING"
			
		elif journey_state == "WAITING":
			# waiting at red line for a go command from TIM
			if command == "STOP_AT_RED":
				continue
			journey_state = "CROSSING"
			
		elif journey_state == "CROSSING":
			# left / right / straight logic
			diff = abs(entry_lane - exit_lane)
			if diff % 2 == 0:
				bot_motion.cross_straight()
			else:
				if entry_lane + exit_lane == 5 and abs(entry_lane - exit_lane) == 3:
					if entry_lane < exit_lane:
						bot_motion.cross_right()
					else:
						bot_motion.cross_left()
				else:
					if entry_lane > exit_lane:
						bot_motion.cross_right()
					else:
						bot_motion.cross_left()
			journey_state = "DEPARTING"
			
		elif journey_state == "DEPARTING":
			# start line following on the exit lane
			bot_motion.start()
			
			# wait for 2 seconds before notifying that the junction is empty
			# TODO :  caliberate
			sleep(2)
			complete_msg = create_complete_msg(bot_id)
			mqttc.publish("tim/jid_1/complete", complete_msg)
			
			# travel for 3 more sec on the exit lane bofore stopping
			# TODO :  caliberate
			sleep(3) # sleep because there is nothing else to do
			journey_state = "AT_DEST"
			
		elif journey_state == "AT_DEST":
			# on reaching the end of the exit lane
			bot_motion.stop()
			# disconnect after reaching the destination
			mqttc.disconnect()
			break


# main function
def main():
	# check usage
	if len(sys.argv) != 6 and len(sys.argv) != 7:
		print "Usage : python tim.py BOT_ID BOT_TYPE ENTRY_LANE EXIT_LANE MOSQUITTO_HOST <MOSQUITTO_PORT>"
		exit(1)
	
	# process command line arguments
	bot_id = sys.argv[1]
	bot_type = sys.argv[2]
	entry_lane = int(sys.argv[3])
	exit_lane = int(sys.argv[4])
	mqtt_host = sys.argv[5]
	if(len(sys.argv) == 7):
		mqtt_port = int(sys.argv[6])
	else:
		mqtt_port = 1883
	if bot_type != "civilian" and bot_type != "ems":
		print "Invalid bot type : civilian / ems"
		exit(1)
	if exit_lane > 4 or exit_lane < 1:
		print "Invalid exit lane : 1 to 4"
		exit(1)
	if entry_lane > 4 or entry_lane < 1:
		print "Invalid exit lane : 1 to 4"
		exit(1)
	
	# get mqtt client
	mqttc = prepare_mqttc(mqtt_host, bot_id, mqtt_port)
	
	# create a thread for the driver function
	driver_thread = threading.Thread(target = driver, args = (mqttc, bot_id, bot_type, entry_lane, exit_lane, command_q))
	driver_thread.start()
	
	# Blocking call that processes network traffic, dispatches callbacks and
	# handles reconnecting.
	# Other loop*() functions are available that give a threaded interface and a
	# manual interface.
	mqttc.loop_forever()
	
	print "Destination reached. Terminating"


if __name__ == "__main__":
	main()
