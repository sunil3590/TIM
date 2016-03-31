import bbb

class IR_AIN(object):
    def __init__(self):
        self.travel_adc = bbb.ADC( 0 )		# line travel IR on AIN0
	self.pos_adc = bbb.ADC( 1 )		# pos line counter IR on AIN4
        self.trav_ratio = 1			#normalization ratio
        self.pos_ratio = 1			#normalization ratio
	self.thresh = 1

    def travel_val(self):
        # adcs are 12-bit, but report a millivolt value via SysFS
	n = 5
	samples = [ self.travel_adc.volts for i in range(n) ]
        average =  (sum(samples) / n)
        return average / self.trav_ratio


    def pos_val(self):
        # adcs are 12-bit, but report a millivolt value via SysFS
	n = 5
	samples = [ self.pos_adc.volts for i in range(n) ]
        average =  (sum(samples) / n)
        return average / self.pos_ratio

    def set_thresh(self, val):
	self.thresh = val

    def get_thresh(self):
	return self.thresh

    def travel_is_white(self):
	return (self.travel_val() < self.thresh)

    def pos_is_white(self):
	return (self.pos_val() < self.thresh)


