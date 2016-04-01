import color_sensor_ISL29125
from time import time

cs = color_sensor_ISL29125.color_senser(1)

if cs.valid_init:
	print "Valid color sensor"
else :
	print "Color Sensor invalid"

cs.setUpperThreshold(0x5)

print "UT : " + str( cs.readUpperThreshold())


for x in range(5):
	t0 = time()
	print "\nStatus: " + cs.readStatus()
	print "Red  : " + str( cs.readRed())
	print "Green: " + str( cs.readGreen())
	print "Blue : " + str( cs.readBlue())
	t1 = time()
	print "Guessed Color is " + cs.roadColor()
	print "Sample time: " + str( int((t1-t0)*10000)/10.0) + "ms"


