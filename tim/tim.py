#!/usr/bin/python

import sys
import paho.mqtt.client as paho
import json
import time
import Queue
from time import gmtime, strftime

# Global queue to hold requests for intersection
request_q = Queue.Queue()

# Create request topic from j_id
def get_request_topic(j_id):
	return "tim/" + j_id + "/request"


# Create notify topic from j_id
def get_notify_topic(j_id):
	return "tim/" + j_id + "/notify"


# initialze a client and connect to the server
def prepare_mqttc(mqtt_host, j_id, mqtt_port):
	# initialze a client and connect to the server
	mqttc = paho.Client(client_id="tim_" + j_id)
	mqttc.connect(host=mqtt_host, port=mqtt_port, keepalive=60)
	
	# subscribe to topics
	req_topic = get_request_topic(j_id)
	mqttc.subscribe(req_topic)
	mqttc.message_callback_add(req_topic, on_request)
	notify_topic = get_notify_topic(j_id)
	mqttc.subscribe(notify_topic)
	mqttc.message_callback_add(notify_topic, on_notify)
	
	return mqttc


def create_pass_response(command):
    res = {}
    res["command"] = command
    return json.dumps(res)


# The callback for when a request message is received
def on_request(mqttc, userdata, msg):
	print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + msg.payload)

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


# The callback for when a notify message is received
def on_notify(mqttc, userdata, msg):
	print msg.payload
	
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
	if len(sys.argv) != 2 and len(sys.argv) != 3:
		print("Usage : python tim.py MOSQUITTO_HOST <MOSQUITTO_PORT>")
		exit(1)
	mqtt_host = sys.argv[1]
	if(len(sys.argv) == 3):
		mqtt_port = int(sys.argv[2])
	else:
		mqtt_port = 1883

	# get a client
	mqttc = prepare_mqttc(mqtt_host, "JID_1", mqtt_port)
	
	# Blocking call that processes network traffic, dispatches callbacks and
	# handles reconnecting.
	# Other loop*() functions are available that give a threaded interface and a
	# manual interface.
	mqttc.loop_forever()


if __name__ == "__main__":
	main()
