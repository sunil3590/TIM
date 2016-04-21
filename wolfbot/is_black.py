#!/usr/bin/python

import motion
import sensor
from time import sleep

bot_sensor = sensor.Sensor()

while True:
    print bot_sensor.is_Black()
    sleep(1)
