import sys
sys.path.append('/wolfbot/agent')
import time
import wolfbot
import ir_ain


w = wolfbot.wolfbot()
print "batt voltage: " + str(w.battery.voltage() ) + "\n"

ir = ir_ain.IR_AIN()
ir.set_thresh( 0.8 )

t0 = time.time()
print "travel_val: " + str(ir.travel_val())
t1 = time.time()
print "time to sample: " + str( t1-t0)


t0 = time.time()
print "pos_val: " + str(ir.pos_val())
t1 = time.time()
print "time to sample: " + str( t1-t0)


print "travel: " + str( ir.travel_is_white() )

print "pos:    " + str( ir.pos_is_white() )



print "\n"   #end of script line space
