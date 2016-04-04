#!/usr/bin/python

from random import gauss
import bot
import sys
import threading
import time
import numpy as np
#import matplotlib.pyplot as plt

def generateSleepValues():
	values = []
	sleep = []
        values = np.random.normal(60,20,50)
	values.sort()
#	print(values)

#        y = []
#        for x in range(0,50):
#		y.append(0)

#	plt.plot(values,y,'ro')
#	plt.show()

	sleep.append(round(values[0],2))

	for x in range(1,50):
		sleep.append(round((values[x]-values[x-1]),1))
	return sleep

def generateTrafficPerLane(enterLane, sleep, x):
	time.sleep(sleep[x])

	if enterLane == "green":
		bot_id = x
	elif enterLane == "blue":
		bot_id = x+50
	elif enterLane == "red":
		bot_id = x+100
        else:
		bot_id = x+150
	enter_lane = enterLane
	exit_lane = "green"
	
	# get mqtt client
	client = bot.prepare_client(str(bot_id))
	
	# create a thread for the driver function
	driver_thread = threading.Thread(target = bot.driver, args = (client, bot_id, exit_lane, bot.command_q, enter_lane))
	driver_thread.start()
	client.loop_forever()
	

sleepRed = generateSleepValues()
sleepGreen = generateSleepValues()
sleepBlue = generateSleepValues()
sleepMagenta = generateSleepValues()

for x in range(0,50):
        generateTrafficPerLane("blue", sleepBlue, x)
        generateTrafficPerLane("green", sleepGreen, x)
        generateTrafficPerLane("red", sleepRed, x)
        generateTrafficPerLane("magenta", sleepMagenta, x)
