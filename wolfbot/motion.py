#!/usr/bin/python

import sys
from time import time
from time import sleep
import threading

try:
	sys.path.append('/wolfbot/agent')
	import wolfbot as wb
	from ir_ain import IR_AIN
	valid_wb = True
except:
	print "Not on wolfbot, faking data"
	valid_wb = False

class Motion(object):

	def __init__(self):
		if valid_wb:
			#create ir travel object to be used for motion.start()
			self.ir = IR_AIN(0)  #travel ir on ADC0 for bot 10
			self.w = wb.wolfbot()
			self.w.move(0, 0)
		else:
			print "Running Motion with fake data"
	
		self.stop_signal = False
		self.valid = True


	#creates a thread to handle line following
	#return thread object so it can be exited by motion.stop()
	def start(self):
		self.stop_signal = False
		#start line following thread here
		self.follow_thread = threading.Thread(target = self.__follower)
		self.follow_thread.start()


	# ayschronously stops the line follow thread	
	def stop(self):
		self.stop_signal = True
		self.follow_thread.join()


	# make a hardcoded left turn
	def cross_left(self):
		if valid_wb: 
			self.w.move(0,60)
			sleep( 2 )
			self.w.rotate( 27 )  #ccw turn
			sleep( 0.5 )
			self.w.move(0, 60)
			sleep( 1.2 )
			self.w.rotate( 27 )
			sleep( 0.5 )
			self.w.move( 0, 60 )
			sleep( 1.5 )
			self.w.move( 0, 0 )
		else:
			print "Turning Left!"


	# make a hardcoded straight motion		
	def cross_straight(self):
		if valid_wb: 
			self.w.move(0,60)
			sleep(4)
			self.w.move(0,0)
		else:
			print "Crossing Straight!"


	# make a hardcoded right turn
	def cross_right(self):
		if valid_wb: #TODO motion right
			self.w.move(0,60)
			sleep(1.4)
			self.w.rotate(-30)	##neg cw right turn
			sleep(0.9)
			self.w.move(0,0)	
		else:
			print "Turning Right!"


	# thread code that handels following line
	def __follower(self):
		if valid_wb:
			drive_speed = 55
			while not self.stop_signal:
				if self.ir.val() >= self.ir.get_thresh():
					self.w.move(0, drive_speed)
				else:
					self.__rot_line()
				sleep(0.1)
			self.w.move(0, 0)
		else: #do nothing but simulate thread
			t = 0
			while not self.stop_signal:
				sleep(1)
				t += 1
				print str(t) + "sec"


	# funciton for follower() to use
	# use rotating movements to find line
	def __rot_line(self):
		ir = self.ir
		dr = 1
		theta_l = [-15, 13]     #bot 14 drifts left, need more power on right swing
		tw = 1
		td = 0.01
		tot = 0
		while(1):
			t0 = time()
			self.w.rotate( theta_l[dr] )
			while ir.val() < ir.get_thresh():
				if (time()-t0) > (tw*td):
					break
			self.w.rotate(0)
			tot += tw*td
			tw += 1
			dr = (dr+1)%2
			if ir.val() >= ir.get_thresh():
				return


# main function to test class
def main():
	bot_mot = Motion()
	if bot_mot.valid :
		print "Working motion object created"
	else:
		print "Error in creating Motion object"
		exit(1)
	
	# time to re align the wolfbot
	print "Realign if there was a jerk"
	sleep(5)

	# move for a few seconds
	print "Start moving"
	bot_mot.start()
	sleep(2)

	print "Test IR: " + str(bot_mot.ir.val())

	# stop and turn left
	bot_mot.stop()
	print "Stopped"
	bot_mot.cross_left()
	print "Turned Left"

if __name__ == "__main__":
	main()
