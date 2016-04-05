#!/usr/bin/python

import sys
from time import time
from time import sleep
import threading

try:
	sys.path.append('/wolfbot/agent')
	import wolfbot as wb
	sys.path.append('/boot/uboot/tim_code/sensors/')
	from ir_ain import IR_AIN
	valid_wb = True
except:
	print "Not on wolfbot, faking data"
	valid_wb = False

class Motion(object):

	def __init__(self):
		if valid_wb:
			#create ir travel object to be used for motion.start()
			self.ir = IR_AIN()
			self.w = wb()
		else:
			print "Running Motion with fake data"
	
		self.stop_signal = False
		self.valid = True


	#creates a thread to handle line following
	#return thread object so it can be exited by motion.stop()
	def start(self):
		#start line following thread here
		self.follow_thread = threading.Thread(target = self.__follower)
		self.follow_thread.start()


	# ayschronously stops the line follow thread	
	def stop(self):
		self.stop_signal = True
		self.follow_thread.join()


	# make a hardcoded left turn
	def cross_left(self):
		if valid_wb: #TODO motion left
			self.w.move(0,50)
			sleep(2)
			self.w.rotate(-30)
			sleep(1)
			self.w.move(0,50)
			sleep(2)
			self.w.move(0,0)
		else:
			print "Turning Left!"


	# make a hardcoded straight motion		
	def cross_straight(self):
		if valid_wb: #TODO motion straight
			self.w.move(0,50)
			sleep(2)
			self.w.rotate(-30)
			sleep(1)
			self.w.move(0,50)
			sleep(2)
			self.w.move(0,0)
		else:
			print "Crossing Straight!"


	# make a hardcoded right turn
	def cross_right(self):
		if valid_wb: #TODO motion right
			self.w.move(0,50)
			sleep(2)
			self.w.rotate(-30)
			sleep(1)
			self.w.move(0,50)
			sleep(2)
			self.w.move(0,0)	
		else:
			print "Turning Right!"


	# thread code that handels following line
	def __follower(self):
		if valid_wb:
			drive_speed = 55
			while not self.stop_signal:
				if self.ir.travel_val() >= self.ir.get_thresh():
					self.w.move(0, drive_speed)
				else:
					__rot_line()
				sleep(0.1)
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
		theta_l = [-25, 23]     #bot 14 drifts left, need more power on right swing
		tw = 1
		td = 0.02
		tot = 0
		while(1):
			t0 = time()
			self.w.rotate( theta_l[dr] )
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


# main function to test class
def main():
	bot_mot = Motion()
	if bot_mot.valid :
		print "Working motion object created"
	else:
		print "Error in creating Motion object"
		exit(1)
	bot_mot.start()
	sleep(5)
	bot_mot.stop()
	bot_mot.cross_left()
	print "At your destination"

if __name__ == "__main__":
	main()
