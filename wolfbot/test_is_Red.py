#!/usr/bin/python

import sys
import motion
import sensor

from time import sleep

mot = motion.Motion()

bot_sensor = sensor.Sensor()

mot.w.move(0, 60)

for x in range(20):
	
	t = bot_sensor.is_Red()
	print t

	if t:
		mot.w.move(0, 0)

	sleep(0.5)


