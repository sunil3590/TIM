import color_sensor_ISL29125
from time import time

cs = color_sensor_ISL29125.color_senser(1)

if cs.valid_init:
        print "Valid color sensor"
else :
        print "Color Sensor invalid"

t0 = time()
red_list = []
green_list = []
blue_list = []
for x in range(100):
	stat = cs.readStatus()
	if "" in stat: 			#"FLAG_CONV_DONE" in stat:
		if "FLAG_CONV_R" not in stat:
			red_list.append( cs.readRed() )
		if "FLAG_CONV_G" not in stat:
                        green_list.append( cs.readGreen() )
		if "FLAG_CONV_G" not in stat:
                        blue_list.append( cs.readBlue() )
tf = time()
red_avg = float(sum( red_list)) / float(len(red_list))
green_avg = float(sum( green_list)) / float(len(green_list))
blue_avg = float(sum( blue_list)) / float(len(blue_list))

print "In " + str( int((tf-t0)*10000)/10.0) + "ms the avg of: " 
print  str(len(red_list)) +  " red   vals was " + str(red_avg)  
print  str(len(green_list)) +" green vals was " + str(green_avg)  
print  str(len(blue_list)) + " blue  vals was " + str(blue_avg) 

print red_avg
print green_avg
print blue_avg
print ""


