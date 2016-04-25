import bbb

class IR_AIN(object):

	#by default, travel is on ADC0, pos is on ADC1 
    def __init__(self, anum):
  	self.adc = bbb.ADC( anum )		
        self.ratio = 1			#normalization ratio
	self.thresh = 1

    def val(self):
        # adcs are 12-bit, but report a millivolt value via SysFS
	n = 5
	samples = [ self.adc.volts for i in range(n) ]
        average =  (sum(samples) / n)
        return average / self.ratio  

    def set_thresh(self, val):
	self.thresh = val

    def get_thresh(self):
	return self.thresh
    
    def is_white(self):
	return (self.val() < self.thresh)


