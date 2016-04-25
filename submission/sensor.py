from ir_ain import IR_AIN
from color_sensor_ISL29125 import color_senser



class Sensor(object):

	def __init__(self):
		self.ir = IR_AIN( 1 )   # ADC1 is position (left) ir on bot 10
		self.ir.set_thresh( 0.5 )  # 0.5V threshold for black values
		self.cs = color_senser()
		if not self.cs.valid_init:
			print "Color Sensor invalid"
		
		
	def is_Red(self):
		return self.cs.is_Red()

	def is_Black(self):
		return (not self.ir.is_white())


