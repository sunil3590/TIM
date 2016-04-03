#!/usr/bin/python

import sys
import paho.mqtt.client as paho
import json
import time

# Create topic from bot_id
def get_topic(postal):
	return "tim/" + postal + "/request"

# initialze a client and connect to the server
def prepare_client(postal):
    # initialze a client and connect to the server
    client = paho.Client(client_id="tim_" + postal + "_sub")
    client.on_message = on_request
    client.connect(host="localhost", port=1883, keepalive=60)
    # TOPIC to subscribe to
    topic = get_topic(postal)
    print topic
    client.subscribe(topic)
    return client
    
def create_pass_response(command):
    res = {}
    res["command"] = command
    return json.dumps(res)

# The callback for when a PUBLISH message is received from the server.
def on_request(client, userdata, msg):
	print msg.payload
	# parse the payload
	pass_req = json.loads(msg.payload)
	# send the intial default command to STOP
	pass_res = create_pass_response("STOP")
	client.publish(pass_req["respond_to"], pass_res)
	# send the GO command
	pass_res = create_pass_response("GO")
	client.publish(pass_req["respond_to"], pass_res)

# main function
def main():
	# process command line arguments
	if len(sys.argv) != 2:
		print("Usage : python tim.py <POSTAL_CODE>")
		exit(1)
	postal = str(sys.argv[1])
	
	# get a client
	client = prepare_client(postal)
	
	# Blocking call that processes network traffic, dispatches callbacks and
	# handles reconnecting.
	# Other loop*() functions are available that give a threaded interface and a
	# manual interface.
	client.loop_forever()

if __name__ == "__main__":
	main()