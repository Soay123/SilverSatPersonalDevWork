#!/path/to/new/virtual/environment/bin/python3
import os
import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_ina219

# Base name should include full path and extra info
class find_unique_filename:
  """Class to create a unique filename"""
  def __init__(self, base_name:str="__",suffix:str=""):
    self.base_path = ""
    self.base_name = ""
    self.base_path, self.base_name = os.path.split(base_name)
    self.file_path = ""
    self.temp_path = ""
    self.file_increment = 0
    self.suffix=suffix
    if self.base_path is "" or self.base_path is None or not os.path.isdir(self.base_path):
      self.base_path = f"{os.getcwd()}"
    # For some reason os.pathsep was a :
    pathsep = "/"
    self.base_path = f"{self.base_path}{pathsep}"
    self.temp_path = f"{self.base_path}{self.base_name}{self.suffix}"
  def getname(self):
    """Build the filename and return it"""
    while os.path.exists(self.temp_path):
      self.temp_path = f"{self.base_path}{self.base_name}_{self.file_increment}{self.suffix}"
      self.file_increment = self.file_increment + 1
    self.file_path = self.temp_path
    return self.file_path

class ads_object:
  """Class responsible for querying the ADS and then writing data to a file and the screen."""
  def __init__(self, ads:ADS.ADS1015, positive_pin:int, negitive_pin:int, base_name:str="_"):
    self.ads = ads
    self.out = ""
    self.file_path = ""
    self.positive_pin = positive_pin
    self.negitive_pin = negitive_pin
    self.base_name = base_name
    unique_name=find_unique_filename(base_name=f"{self.base_name}_ads_out_{self.positive_pin}_{self.negitive_pin}",suffix=".csv")
    self.file_path=unique_name.getname()
    self.channel=AnalogIn(ads, positive_pin, negitive_pin)
    data = f"\"time_in_ms\",\"voltage\"\n"
    with open(self.file_path, "w") as file:
      file.write(data)
    self.start_time = int(time.time() * 1000)
  def write_to_file(self):
    data = f"{self.out}\n"
    # This is kind of a bumber because I constantly open and close the file
    with open(self.file_path, "a") as file:
      file.write(data)
  def create_output_string(self):
    ads_voltage = 0.0
    ads_voltage = self.channel.voltage
    # adc_value = chan_vcc.value
    time_in_ms = int(time.time() * 1000) - self.start_time
    self.out = f"{time_in_ms},{ads_voltage}"
  def display_on_screen(self):
    print(f"{self.out}")
  def get_next_sample(self):
    """Method responsible for querying the ADS and displaying the output"""
    self.create_output_string()
    self.display_on_screen()
    self.write_to_file()

class ina_object:
  """Class responsible for querying the INA and then writing data to a file and the screen."""
  def __init__(self, ina:adafruit_ina219.INA219, base_name:str="_"):
    self.ina = ina
    self.out = ""
    self.file_path = ""
    self.base_name=base_name
    addr = self.ina.i2c_addr
    unique_name=find_unique_filename(base_name=f"{self.base_name}_{addr}",suffix=".csv")
    self.file_path=unique_name.getname()
    data = f"\"time_in_ms\",\"bus_voltage\",\"shunt_voltage\",\"current\",\"power\"\n"
    with open(self.file_path, "w") as file:
      file.write(data)
    self.start_time = int(time.time() * 1000)
  def write_to_file(self):
    data = f"{self.out}\n"
    # This is kind of a bumber because I constantly open and close the file
    with open(self.file_path, "a") as file:
      file.write(data)
  def create_output_string(self):
    bus_voltage = self.ina.bus_voltage
    shunt_voltage = self.ina.shunt_voltage
    current = self.ina.current
    power = self.ina.power
    time_in_ms = int(time.time() * 1000) - self.start_time
    self.out = f"{time_in_ms},{bus_voltage},{shunt_voltage},{current},{power}"
  def display_on_screen(self):
    print(f"{self.out}")
  def get_next_sample(self):
    """Method responsible for querying the INA and displaying the output"""
    self.create_output_string()
    self.display_on_screen()
    self.write_to_file()

i2c = busio.I2C(board.SCL, board.SDA)

object_array = []

# Can be configured with I2C addresses Default address 72, Soldered 73
# 0x48: The default address, which is set when the address pin is connected to GND
# 0x49: Set when the address pin is connected to VDD
# 0x4A: Set when the address pin is connected to SDA
# 0x4B: Set when the address pin is connected to SCL
# Use pin pairs A0+A1;A2+A3 for reference
# ADS Gain must literally be the float value 2/3 to allow more than 4 volts
# However you would only want to do that if VDD is 5v (see note in readme).
try:
  ads_5v = ADS.ADS1015(i2c, gain=1, address=72)
  ads_object_5v = ads_object(ads_5v, ADS.P0, ADS.P1, base_name="ADS1015_72_5v")
  object_array.append(ads_object_5v)
except Exception as err:
  print(f"Unexpected {err=}, {type(err)=}")

try:
  ads_3_3v = ADS.ADS1015(i2c, gain=1, address=72)
  ads_object_3_3v = ads_object(ads_3_3v, ADS.P2, ADS.P3, base_name="ADS1015_72_3_3v")
  object_array.append(ads_object_3_3v)
except Exception as err:
  print(f"Unexpected {err=}, {type(err)=}")

try:
  ads_b_1 = ADS.ADS1015(i2c, gain=1, address=73)
  ads_object_b_1 = ads_object(ads_b_1, ADS.P0, ADS.P1, base_name="ADS1015_73_b_1")
  object_array.append(ads_object_b_1)
except Exception as err:
  print(f"Unexpected {err=}, {type(err)=}")

try:
  ads_b_2 = ADS.ADS1015(i2c, gain=1, address=73)
  ads_object_b_2 = ads_object(ads_b_2, ADS.P2, ADS.P3, base_name="ADS1015_73_b_2")
  object_array.append(ads_object_b_2)
except Exception as err:
  print(f"Unexpected {err=}, {type(err)=}")

# Create the INA219 objects
# Addresses: Default = 0x40 = 64, A0 soldered = 0x41 = 65,
# A1 soldered = 0x44 = 68, A0 and A1 soldered = 0x45 = 69
try:
  ina219_1 = adafruit_ina219.INA219(i2c, addr=64)
  ina219_object_1 = ina_object(ina219_1, "ina219_64")
  object_array.append(ina219_object_1)
except Exception as err:
  print(f"Unexpected {err=}, {type(err)=}")

try:
  ina219_2 = adafruit_ina219.INA219(i2c, addr=65)
  ina219_object_2 = ina_object(ina219_2, "ina219_65")
  object_array.append(ina219_object_2)
except Exception as err:
  print(f"Unexpected {err=}, {type(err)=}")

try:
  ina219_3 = adafruit_ina219.INA219(i2c, addr=68)
  ina219_object_3 = ina_object(ina219_3, "ina219_68")
  object_array.append(ina219_object_3)
except Exception as err:
  print(f"Unexpected {err=}, {type(err)=}")

try:
  ina219_4 = adafruit_ina219.INA219(i2c, addr=69)
  ina219_object_4 = ina_object(ina219_4, "ina219_69")
  object_array.append(ina219_object_4)
except Exception as err:
  print(f"Unexpected {err=}, {type(err)=}")

while len(object_array) is not 0:
  for item in object_array:
    item.get_next_sample()
  time.sleep(0.25)
