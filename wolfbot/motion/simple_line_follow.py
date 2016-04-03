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

print "batt voltage: " + str(w.battery.voltage() ) + "\n"

current_dir = 'left'

def switch_dir(old, speed):
        if old == 'left':
                w.move( 3, speed)
                return 'right'
        else :
                w.move( 357, speed)
                return 'left'


drive_speed = 50

t_end = time() + 60*2   # 2 mins
current_dir = switch_dir( current_dir, drive_speed) #start moving
black_check = 0         #seen black yet? don't change dir

#while time() < t_end:
for x in range(15):      #approx 20s
        print "Is White: " + str(ir.travel_is_white())

        if ir.travel_is_white() and black_check :
                current_dir = switch_dir(current_dir, drive_speed)
                print "Dir : " + current_dir
                black_check = 0
        else:
                black_check = 1

        sleep(0.1)

w.move(0,0)

