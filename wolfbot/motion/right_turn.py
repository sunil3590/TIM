import sys
from time import time
from time import sleep
import threading

sys.path.append('/wolfbot/agent')
import wolfbot as wb

w = wb.wolfbot()

print "batt voltage: " + str(w.battery.voltage() ) + "\n"

w.move(0,0)
sleep(3) # pause before start


w.move(0,60)
sleep( 1.4 )
w.rotate( -30 ) 	#cw turn
sleep( 0.9 )
w.move(0, 60)
sleep( 0.8 )
#w.rotate( 27 )
#sleep( 0.5 )


w.move( 0, 0 )


