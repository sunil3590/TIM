mport sys
sys.path.append('/wolfbot/agent')
import wolfbot as wb
from time import time
from time import sleep
from ir_ain import IR_AIN

w = wb.wolfbot()
ir = IR_AIN()

print "batt voltage: " + str(w.battery.voltage() ) + "\n"

current_dir = 'left'

def switch_dir(old, speed):
	if old == 'left':
		w.move( 10, speed)
		return 'right'
	else :
		w.move( 350, speed)
		return 'left'


drive_speed = 45

t_end = time() + 60*2	# 2 mins
current_dir = switch_dir( current_dir, drive_speed) #start moving
while time() < t_end:
	
	if ir.travel_is_white() :
		current_dir = switch_dir(current_dir, drive_speed)
		print current_dir

	sleep(1)



