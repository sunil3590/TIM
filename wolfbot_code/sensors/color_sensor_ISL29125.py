import os
import csv
from i2c.Adafruit_I2C import Adafruit_I2C

csv.register_dialect('nospace', skipinitialspace=True)

def clean_csv(f):
  for line in f:
      line = line.strip()
      if line and not line.startswith('#'):
          yield line

def signed_16(low,high):
  val = low + (high<<8)
  # two's compliment
  if val & (1<<15):
      val -= (1<<16)
  return val
  
# We must OR with 0x80 to set the MSB of the register, allowing multiple reads
MULTI = 0x80



class accel(Adafruit_I2C):
  """Access accelerometer over I2C
  Note that the registers for each direction are read in low, high order, which is 
  the opposite of the magenetometer.
  """

  def __init__(self, enable=True):
      self.sub_address = 0b0011001
      reg = {}
      cur_dir = os.path.dirname(os.path.abspath(__file__))
      with open(cur_dir + '/lsm/lsm_accel_map.csv', 'r') as f:
          data = csv.DictReader(clean_csv(f), dialect='nospace')
          for row in data:
            name = row['register']
            reg[name] = int(row['hex'],base=16)
      self.reg = reg
      try:
          self.i2c = Adafruit_I2C(self.sub_address, busnum=1, debug=False)
      except IOError as e:
          print "I2C init failed: %s" % e.strerror

      if enable:
        self.enable()

  def enable(self):
      # From datasheet, Table 18
      X_en = 1<<0
      Y_en = 1<<1
      Z_en = 1<<2
      LP_en = 1<<3
      rate_10hz = 0b10<<4
      self.i2c.write8(self.reg['CTRL_REG1_A'], rate_10hz|X_en|Y_en|Z_en)  # 0x27
           
  def read_x(self):
      low,high = self.i2c.readList(self.reg['OUT_X_L_A'] | MULTI, 2)
      return signed_16(low,high)

  def read_y(self):
      low,high = self.i2c.readList(self.reg['OUT_Y_L_A'] | MULTI, 2)
      return signed_16(low,high)

  def read_z(self):
      low,high = self.i2c.readList(self.reg['OUT_Z_L_A'] | MULTI, 2)
      return signed_16(low,high)

  def read(self):
      x_l,x_h,y_l,y_h,z_l,z_h = self.i2c.readList(self.reg['OUT_X_L_A'] | MULTI, 6)
      return signed_16(x_l,x_h),signed_16(y_l,y_h),signed_16(z_l,z_h)
