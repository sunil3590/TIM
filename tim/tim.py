#!/usr/bin/python

import sys
import paho.mqtt.client as paho
import json
import time
import Queue
import threading
import copy

# which algo should TIM run?
algo = "Q" # just a random initialization, will be over written

# used when algo is Q
request_q = Queue.Queue()
# used when algo is PQ
lane_pq = Queue.PriorityQueue()
lane_request_qs = [Queue.Queue() for i in range(4)]
# used to store details about the bot that is currently crossing
cur_crossing = -1

# lock to access queue
lock = threading.Lock()


# Create request topic from j_id
def get_request_topic(j_id):
	return "tim/" + j_id + "/request"


# Create complete topic from j_id
def get_complete_topic(j_id):
	return "tim/" + j_id + "/complete"


# initialze a client and connect to the server
def prepare_mqttc(mqtt_host, j_id, mqtt_port):
	# initialze a client and connect to the server
	mqttc = paho.Client(client_id="tim_" + j_id)
	mqttc.connect(host=mqtt_host, port=mqtt_port, keepalive=60)
	
	# subscribe to request topic
	req_topic = get_request_topic(j_id)
	mqttc.subscribe(req_topic)
	mqttc.message_callback_add(req_topic, on_request)
	# subscribe to complete topic
	complete_topic = get_complete_topic(j_id)
	mqttc.subscribe(complete_topic)
	mqttc.message_callback_add(complete_topic, on_complete)
	
	return mqttc


# response to be sent to bot
def make_response(command):
    res = {}
    res["command"] = command
    return json.dumps(res)


# define bot priority
def get_bot_priority(bot_type):
	if bot_type == "ems":
		return 100
	else:
		return 1


# print PQ
def print_pq(pq):
	lanes = []
	while pq.empty() == False:
		lane = pq.get()
		print str(lane[0]) + " " + str(lane[1]) + " " + str(lane[2])
		lanes.append(lane)

	for lane in lanes:
		pq.put(lane)


# send GO to top req in the queue
def send_go_top_q(mqttc):
	# take lock
	lock.acquire()

	# if there are no pending requests
	if request_q.empty() == True:
		return -1;

	# get the top request from queue
	req = request_q.get()

	# release lock
	lock.release()

	# send the GO command
	mqttc.publish(req["respond_to"], make_response("go"))
	print(req["respond_to"] + " : GO")

	# return the bot id as the current owner of junction
	return req["bot_id"]


# add a req to priority queue algo data structs
def add_req_to_pq(req):
	global lane_pq

	# take lock
	lock.acquire()

	# add request to the lanes req queue
	lane_request_qs[req["enter"] - 1].put(req)

	# priority of bot
	bot_priority = get_bot_priority(req["bot_type"])

	# update priority of lanes
	new_lane_pq = Queue.PriorityQueue()
	while lane_pq.empty() == False:
		lane = lane_pq.get()
		if lane[2] == req["enter"]:
			new_lane_pq.put((lane[0] - bot_priority, lane[1], lane[2]))
		else:
			new_lane_pq.put(lane)
	lane_pq = new_lane_pq

	# print_pq(lane_pq)

	# release lock
	lock.release()


# send GO to top req in the priority queue
def send_go_top_pq(mqttc):
	global lane_pq

	# take lock
	lock.acquire()

	# get the top priority lane and its req queue
	lane = lane_pq.get()
	lane_req_q = lane_request_qs[lane[2] - 1]

	# if there are no pending requests
	if lane_req_q.empty() == True:
		lane_pq.put(lane)
		return -1;

	# get the top request from queue
	req = lane_req_q.get()

	# priority of bot
	bot_priority = get_bot_priority(req["bot_type"])

	# send the GO command
	mqttc.publish(req["respond_to"], make_response("go"))
	print(req["respond_to"] + " : GO")

	# update priority of lanes
	lane_pq.put((lane[0] + bot_priority, lane[1], lane[2]))

	# TODO : deal with, busy lane hogging the junction

	# release lock
	lock.release()

	# return the bot id as the current owner of junction
	return req["bot_id"]


# The callback for when a request message is received
def on_request(mqttc, userdata, msg):
	print(msg.payload)
	global cur_crossing

	# parse the payload
	req = json.loads(msg.payload)

	if algo == "Q":
		# add request to q
		request_q.put(req)

		# send GO if junction is empty
		if cur_crossing == -1:
			cur_crossing = send_go_top_q(mqttc)
		# else send STOP
		else:
			mqttc.publish(req["respond_to"], make_response("stop"))
			print(req["respond_to"] + " : STOP")

	elif algo == "PQ":
		# add request to q of the lane
		add_req_to_pq(req)

		# send GO if junction is empty
		if cur_crossing == -1:
			cur_crossing = send_go_top_pq(mqttc)
		# else send STOP
		else:
			mqttc.publish(req["respond_to"], make_response("stop"))
			print(req["respond_to"] + " : STOP")


# The callback for when a complete message is received
def on_complete(mqttc, userdata, msg):
	print msg.payload
	global cur_crossing

	# parse the payload
	complete = json.loads(msg.payload)

	if algo == "Q":
		# send GO to next req in q
		cur_crossing = send_go_top_q(mqttc)
	elif algo == "PQ":
		# send GO to next req in pq
		cur_crossing = send_go_top_pq(mqttc)


# main function
def main():
	# process command line arguments
	if len(sys.argv) != 3 and len(sys.argv) != 4:
		print "Usage : python tim.py ALGO MOSQUITTO_HOST <MOSQUITTO_PORT>"
		exit(1)
	global algo
	algo = sys.argv[1]
	if (algo != "Q" and algo != "PQ"):
		print "ALGO has to be Q or PQ"
	mqtt_host = sys.argv[2]
	if(len(sys.argv) == 4):
		mqtt_port = int(sys.argv[3])
	else:
		mqtt_port = 1883

	# (priority, secondary priority, lane id)
	lane_pq.put((0, 1, 1))
	lane_pq.put((0, 2, 2))
	lane_pq.put((0, 3, 3))
	lane_pq.put((0, 4, 4))

	# get a client
	mqttc = prepare_mqttc(mqtt_host, "jid_1", mqtt_port)
	
	# Blocking call that processes network traffic, dispatches callbacks and
	# handles reconnecting.
	# Other loop*() functions are available that give a threaded interface and a
	# manual interface.
	mqttc.loop_forever()


if __name__ == "__main__":
	main()
