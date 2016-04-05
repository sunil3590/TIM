import color_sensor_ISL29125
from time import time


def get_avg():
	red_list = []
	green_list = []
	blue_list = []
	for x in range(100):
		stat = cs.readStatus()
		if "" in stat:                  #"FLAG_CONV_DONE" in stat:
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

	return [red_avg, green_avg, blue_avg]


cs = color_sensor_ISL29125.color_senser(1)

if cs.valid_init:
        print "Valid color sensor"
else :
        print "Color Sensor invalid"

fc = open( "./red_config.txt",'w')

#===================================================
col = "Red"
print "Test " + col + " Square"
raw_input("Press Enter to take average rgb")
ColAvg = get_avg()
print ColAvg
tmp = col + " " +  str(ColAvg[0])\
	+ " " + str(ColAvg[1])\
	+ " " + str(ColAvg[2]) + "\n"
fc.write( tmp )


col = "White"
print "Test " + col + " Square"
raw_input("Press Enter to take average rgb")
ColAvg = get_avg()
print ColAvg
tmp = col + " " +  str(ColAvg[0])\
	+ " " + str(ColAvg[1])\
	+ " " + str(ColAvg[2]) + "\n"
fc.write( tmp )


fc.close()


