#!/usr/bin/python

from random import gauss
import bot
import sys
import threading
import time

def generateSleepValues():
	values = []
	sleep = []

	while len(values) < 50:
    		value = gauss(60,20)
    		if 0 < value < 120:
        		values.append(round(value,1))

	values.sort()

	sleep.append(values[0])

	for x in range(1,50):
		sleep.append(round((values[x]-values[x-1]),1))
	return sleep

sleep = generateSleepValues()
print(sleep)

for x in range(0,50):
	time.sleep(sleep[x])
	# process command line arguments

	bot_id = x
	enter_lane = "blue"
	exit_lane = "green"
	
	# get mqtt client
	client = bot.prepare_client(bot_id)
	
	# create a thread for the driver function
	driver_thread = threading.Thread(target = bot.driver, args = (client, bot_id, exit_lane, bot.command_q, enter_lane))
	driver_thread.start()
	client.loop_forever()
