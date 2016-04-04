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

current_dir = 'left'

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


drive_speed = 50

t_end = time() + 60*2   # 2 mins
current_dir = switch_dir( current_dir, drive_speed) #start moving
black_check = 0		#seen black yet? don't change dir

#while time() < t_end:
for x in range(20):      #approx 20s
	if ir.travel_val() >= ir.thresh:       
		w.move(0, drive_speed)
	else:
		rot_line()

	sleep(0.2)

w.move(0,0)

