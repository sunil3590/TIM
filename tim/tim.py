#!/usr/bin/python

import sys
import paho.mqtt.client as paho
import json
import time
import Queue
from time import gmtime, strftime

# which algo should TIM run?
algo = "Q" # just a random initialization, will be over written

# Global queue to hold requests for intersection
request_q = Queue.Queue()
cur_crossing = []

# Create request topic from j_id
def get_request_topic(j_id):
	return "tim/" + j_id + "/request"


# Create crossing topic from j_id
def get_crossing_topic(j_id):
	return "tim/" + j_id + "/crossing"

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
	# subscribe to crossing topic
	cross_topic = get_crossing_topic(j_id)
	mqttc.subscribe(cross_topic)
	mqttc.message_callback_add(cross_topic, on_crossing)
	# subscribe to complete topic
	complete_topic = get_complete_topic(j_id)
	mqttc.subscribe(complete_topic)
	mqttc.message_callback_add(complete_topic, on_complete)
	
	return mqttc


# response to be sent to bot
def create_pass_response(command):
    res = {}
    res["command"] = command
    return json.dumps(res)


# The callback for when a request message is received
def on_request(mqttc, userdata, msg):
	print(msg.payload)

	# parse the payload
	pass_req = json.loads(msg.payload)

	# send the intial default command to STOP
	pass_res = create_pass_response("stop")
	mqttc.publish(pass_req["respond_to"], pass_res)

	# send GO if no other requests are prending
	if request_q.empty() == True:
		# TODO : although Q is empty, the junction may not be
		# as the previous bot may be in the process of crossing
		# send the GO command
		pass_res = create_pass_response("go")
		mqttc.publish(pass_req["respond_to"], pass_res)
	else: # put request on queue
		request_q.put(pass_req)


# The callback for when a crossing message is received
def on_crossing(mqttc, userdata, msg):
	print msg.payload

	# parse the payload
	crossing = json.loads(msg.payload)

	# add the bot to the currently crossing list
	cur_crossing.append(crossing["bot_id"])


# The callback for when a complete message is received
def on_complete(mqttc, userdata, msg):
	print msg.payload

	# parse the payload
	complete = json.loads(msg.payload)

	# remove the bot from the currently crossing list
	cur_crossing.remove(complete["bot_id"])
	
	# send GO to any pending request
	if request_q.empty() == False:
		# get the top request from queue
		pass_req = request_q.get()
		# send the GO command
		pass_res = create_pass_response("go")
		mqttc.publish(pass_req["respond_to"], pass_res)


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

	# get a client
	mqttc = prepare_mqttc(mqtt_host, "jid_1", mqtt_port)
	
	# Blocking call that processes network traffic, dispatches callbacks and
	# handles reconnecting.
	# Other loop*() functions are available that give a threaded interface and a
	# manual interface.
	mqttc.loop_forever()


if __name__ == "__main__":
	main()
