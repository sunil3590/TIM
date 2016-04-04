import sys
sys.path.append('/wolfbot/agent')
import wolfbot as wb
from time import time
from time import sleep
sys.path.append('../sensors/')
from ir_ain import IR_AIN

w = wb.wolfbot()
w.move(0,0)
sleep(5)


ir = IR_AIN()
ir.set_thresh(0.5)


print "batt voltage: " + str(w.battery.voltage() ) + "\n"


def switch_dir(old, speed):
        if old == 'left':
                w.move( 3, speed)
                return 'right'
        else :
                w.move( 357, speed)
                return 'left'


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
                while ir.travel_val() < ir.get_thresh():
#                        print ir.travel_val()
                        if (time()-t0) > (tw*td) :
                                break
                w.rotate(0)
                tot += tw*td
                tw += 1
                dr = (dr+1)%2
                if ir.travel_val() >= ir.get_thresh():
#                        print tw
#                        print tot
                        return


position = {'count':0, 'status': 'on_white'}

drive_speed = 55

t0 = time()
tend = 20	#max runtime in seconds
while 1:
	if (time() - t0) > tend:
		print "Finished Runtime"
		break

	if ir.travel_val() >= ir.get_thresh():       
		w.move(0, drive_speed)
	else:
		rot_line()

	#print ir.pos_val()
	if (ir.pos_val() >= ir.get_thresh()) and\
		 (position['status'] == 'on_white'):
		position['status'] = 'on_black'
		position['count'] += 1

	if (ir.pos_val() < ir.get_thresh()) and \
		 (position['status'] == 'on_black'):
		position['status'] = 'on_white'
		print position['count']



	sleep(0.1)


w.move(0,0)

