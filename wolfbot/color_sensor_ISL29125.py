import os
import csv
import sys
sys.path.append('/wolfbot/agent/i2c/')

from Adafruit_I2C import Adafruit_I2C

from  ISL29125_const import *
from operator import sub
from operator import abs
#from operator import int

#based on SparkFunISL29125.cpp

class color_senser(Adafruit_I2C):

# Initialize - returns true if successful
# Starts Wire/I2C Communication
# Verifies sensor is there by checking its device ID
# Resets all registers/configurations to factory default
# Sets configuration registers for the common use case
	def __init__(self, enable=True):
		ret = 1
		self.sub_address = ISL_I2C_ADDR

		#Start I2C device
		try:
			self.i2c = Adafruit_I2C(self.sub_address, busnum=1, debug=False)
		except IOError as e:
			print "I2C init failed: %s" % e.strerror

		#Check device ID
		if( self.i2c.readS8(DEVICE_ID) != 0x7D):
			ret &= 0

		#reset registers
		data = 0
		self.i2c.write8(DEVICE_ID, 0x46)
		#check reset
		data |= self.i2c.readS8(CONFIG_1)
		data |= self.i2c.readS8(CONFIG_1)
		data |= self.i2c.readS8(CONFIG_3)
		data |= self.i2c.readS8(STATUS)
		if( data != 0x0 ):
			ret &= 0

		# Set to RGB mode, 10k lux, and high IR compensation
		ret &= self.config(CFG1_MODE_RGB | CFG1_10KLUX | CFG1_12BIT, CFG2_IR_ADJUST_HIGH, CFG3_NO_INT )

		self.valid_init = ret

		# read and save rgb values from file
		self.setup_rgb_colors()

# Setup Configuration registers (three registers) - returns true if successful
# Use CONFIG1 variables from SFE_ISL29125.h for first parameter config1, CONFIG2 for config2, 3 for 3
# Use CFG_DEFAULT for default configuration for that register
	def config( self,config1, config2, config3):
		ret = 1
		data = 0x00

		# Set 1st configuration register
		self.i2c.write8(CONFIG_1, config1)

		# Set 2nd configuration register
		self.i2c.write8(CONFIG_2, config2)

		# Set 3rd configuration register
		self.i2c.write8(CONFIG_3, config3)


		# Check if configurations were set correctly
		data = self.i2c.readS8(CONFIG_1)
		if (data != config1):
			ret &= 0

		data = self.i2c.readS8(CONFIG_2)
		if (data != config2):
			ret &= 0

		data = self.i2c.readS8(CONFIG_3)
		if (data != config3):
			ret &= 0

		return ret

	# Reads the raw_rgb.txt
	def setup_rgb_colors(self):
		rgb_colors = {}
		self.rgb_colors = {}
		try:
			fc = open("./red_config.txt",'r')
		except IOError:
			print "No red_config.txt"
			return

		for x in range(2):
			tmp = fc.readline().split()
			rgb_colors[tmp[0]]=map(float,tmp[1:])
		self.rgb_colors = rgb_colors


	# Sets upper threshold value for triggering interrupts
	def setUpperThreshold(self, data):
		self.i2c.write16(THRESHOLD_HL, data)


	# Sets lower threshold value for triggering interrupts
	def setLowerThreshold( self, data):
		self.i2c.write16(THRESHOLD_LL, data)


	# Check what the upper threshold is, 0xFFFF by default
	def readUpperThreshold(self):
		return self.i2c.readU16(THRESHOLD_HL)


	# Check what the upper threshold is, 0x0000 by default
	def readLowerThreshold(self):
		return self.i2c.readU16(THRESHOLD_LL)


	# Read the latest Sensor ADC reading for the color Red
	def readRed(self):
		return self.i2c.readU16(RED_L)


	# Read the latest Sensor ADC reading for the color Green
	def readGreen(self):
		return self.i2c.readU16(GREEN_L)


	# Read the latest Sensor ADC reading for the color Blue
	def readBlue(self):
		return self.i2c.readU16(BLUE_L)


	# Check status flag register that allows for checking for interrupts, brownouts, and ADC conversion completions
	def readStatus(self):
		word =  self.i2c.readU8(STATUS)
		
		stat = ""

		if (word &  FLAG_CONV_B) ==  FLAG_CONV_B :
			stat += " FLAG_CONV_B"
		if (word &  FLAG_CONV_R) ==  FLAG_CONV_R :
			stat += " FLAG_CONV_R"
		if (word &  FLAG_CONV_G) ==  FLAG_CONV_G :
			stat += " FLAG_CONV_G"
		if (word &  FLAG_BROWNOUT) ==  FLAG_BROWNOUT :
			stat += " FLAG_BROWNOUT"
		if (word &  FLAG_CONV_DONE) ==  FLAG_CONV_DONE :
			stat += " FLAG_CONV_DONE"
		if (word & FLAG_INT) == FLAG_INT :
			stat += " FLAG_INT"


		if stat == "":
			stat = "No Status Flags"

		return stat



	def is_Red(self):
		if len(self.rgb_colors) < 1:
                        print "No valid red_config.txt"
                        return "No valid red_config.txt"
                else:
                        red_list = []
                        green_list = []
                        blue_list = []
                        for x in range(100):
                                stat = self.readStatus()
                                if "" in stat:                  #"FLAG_CONV_DONE" in stat:
                                        if "FLAG_CONV_R" not in stat:
                                                red_list.append( self.readRed() )
                                        if "FLAG_CONV_G" not in stat:
                                                green_list.append( self.readGreen() )
                                        if "FLAG_CONV_G" not in stat:
                                                blue_list.append( self.readBlue() )
			red_avg = float(sum( red_list)) / float(len(red_list))
                        green_avg = float(sum( green_list)) / float(len(green_list))
                        blue_avg = float(sum( blue_list)) / float(len(blue_list))
                        diff = {}
                        for color,vals in self.rgb_colors.items():
                                diff[color] = sum(map(abs, map(sub, vals, [red_avg,green_avg,blue_avg])))

			answer = min(diff, key=diff.get)

			if answer == "Red":
				return True
			else :
				return False



