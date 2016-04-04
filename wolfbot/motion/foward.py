import sys
sys.path.append('/wolfbot/agent')
import wolfbot as wb
from time import time
from time import sleep
sys.path.append('../sensors/')
from ir_ain import IR_AIN

w = wb.wolfbot()
ir = IR_AIN()
w.move(0,0)
sleep(5)

print "batt voltage: " + str(w.battery.voltage() ) + "\n"

w.move(0, 45)

sleep(8)

w.move(0,0)


