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
        dr = 1
        theta_l = [-25, 23]     #bot 14 drifts left, need more power on right swing
        tw = 1
        td = 0.02
        tot = 0
	while(1):
        	t0 = time()
		w.rotate( theta_l[dr] )
		while ir.travel_val() < ir.thresh:
			print ir.travel_val()
			if (time()-t0) > (tw*td) :
				break
		w.rotate(0)
		tot += tw*td
		tw += 1
		dr = (dr+1)%2
		if ir.travel_val() >= ir.thresh:
			print tw
			print tot
			return


rot_line()
print "Found line"
