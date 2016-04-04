import sys
sys.path.append('/wolfbot/agent')
import wolfbot as wb
from time import time
from time import sleep
sys.path.append('../sensors/')
from ir_ain import IR_AIN

w = wb.wolfbot()
w.move(0,0)
#sleep(5)


ir = IR_AIN()

print "batt voltage: " + str(w.battery.voltage() ) + "\n"

ir.set_thresh(0.5)

def check_white():
	print "val: " + str(ir.travel_val()) + " " + str(ir.travel_is_white())
	return ir.travel_is_white()

# use rotating movements to find line
def rot_line():
	dir = 1
	theta_l = [-30, 28]	#bot 14 drifts left, need more power on right swing
	tw = 1
	td = 0.02
	tot = 0
	while 1:
		theta = theta_l[dir]
		dir = (dir+1) %2
		for x in range(tw):
			w.rotate(theta)
			sleep(td)
			tot += td
			#w.rotate(0)
			if not check_white():
				print tw*td
				print tot
				return
		tw += 1
		print tw	
	

w.move(0,0)

rot_line()
print "Found Line"


