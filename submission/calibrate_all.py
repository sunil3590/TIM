import motion
import sensor
from time import sleep

mot = motion.Motion()
sen = sensor.Sensor()

mot.w.move(0,0)


print "Battery Value:"
print str(mot.w.battery.voltage()) + "V"
print ""

print "Testing Sensor"
print 	str(sen.cs.readRed()) + "  " +\
	str(sen.cs.readGreen()) + "  " +\
	str(sen.cs.readBlue())
print sen.is_Red()

print""
print sen.ir.val()
print sen.is_Black()


print ""
print "Testing Pos IR"
print mot.ir.val()
print mot.ir.is_white()



mot.w.move(0,0)
