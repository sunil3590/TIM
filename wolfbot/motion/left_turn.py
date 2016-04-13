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
sleep( 2 )
w.rotate( 27 ) 	#ccw turn
sleep( 0.5 )
w.move(0, 60)
sleep( 1.2 )
w.rotate( 27 )
sleep( 0.5 )
w.move( 0, 60 )
sleep( 1.5 )



w.move( 0, 0 )


