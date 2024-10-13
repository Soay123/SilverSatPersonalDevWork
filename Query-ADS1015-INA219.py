#!/path/to/new/virtual/environment/bin/python3
import os
import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
# import adafruit_ina219
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219, Gain, Mode
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
    if self.base_path == "" or self.base_path == None or not os.path.isdir(self.base_path):
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
    start_time_as_str = f"{self.start_time}"
    self.start_time_str_len = len(start_time_as_str)
  def write_to_file(self):
    data = f"{self.out}\n"
    # This is kind of a bumber because I constantly open and close the file
    with open(self.file_path, "a") as file:
      file.write(data)
  def create_output_string(self):
    ads_voltage = 0.0
    ads_voltage = self.channel.voltage
    # adc_value = chan_vcc.value
    time_in_ms_raw = int(time.time() * 1000) - self.start_time
    time_in_ms_as_str = f"{time_in_ms_raw}"
    time_in_ms = time_in_ms_as_str.zfill(self.start_time_str_len)
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
  def __init__(self, ina:INA219, base_name:str="_"):
    self.ina = ina
    self.out = ""
    self.file_path = ""
    self.base_name=base_name
    # Default values
    # set_calibration_32V_2A()    Initialize chip for 32V max and up to 2A (default)
    #   Configures to INA219 to be able to measure up to 32V and 2A of current. Counter overflow occurs at 3.2A.
    #   self.bus_voltage_range = BusVoltageRange.RANGE_32V
    #   self.gain = Gain.DIV_8_320MV
    #   self.bus_adc_resolution = ADCResolution.ADCRES_12BIT_1S
    #   self.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_1S
    #   self.mode = Mode.SANDBVOLT_CONTINUOUS
    # overflow is Math Overflow bit in Bus Voltage register
    addr = self.ina.i2c_addr
    unique_name=find_unique_filename(base_name=f"{self.base_name}_{addr}",suffix=".csv")
    self.file_path=unique_name.getname()
    data = f"\"time_in_ms\",\"bus_voltage\",\"shunt_voltage\",\"v_plus\",\"current_ma\",\"power_calc\",\"power\",\"impedance\"\n"
    with open(self.file_path, "w") as file:
      file.write(data)
    self.start_time = int(time.time() * 1000)
    start_time_as_str = f"{self.start_time}"
    self.start_time_str_len = len(start_time_as_str)
  def write_to_file(self):
    data = f"{self.out}\n"
    # This is kind of a bumber because I constantly open and close the file
    with open(self.file_path, "a") as file:
      file.write(data)
  def create_output_string(self):
    # voltage on V- (load side)
    bus_voltage = self.ina.bus_voltage
    # voltage between V+ and V- across the shunt
    shunt_voltage = self.ina.shunt_voltage
    # voltage on V+ (voltage source side)
    v_plus = bus_voltage + shunt_voltage
    # current in mA - possible this is an int
    current = self.ina.current
    # Shunt current
    shunt_current:float = current / 1000
    # Calculated power
    power_calc = bus_voltage * shunt_current
    # Does that mean I can calculate impedance too?
    # Apparently not. Shut current is 0 sometimes
    current_flt:float = self.ina.current
    # If current is 0 then impedance is infinite, but we will just say 0
    impedance_calc:float = 0
    if current_flt != 0:
      impedance_calc = bus_voltage / current_flt
    # power in watts from register
    power = self.ina.power
    time_in_ms_raw = int(time.time() * 1000) - self.start_time
    time_in_ms_as_str = f"{time_in_ms_raw}"
    time_in_ms = time_in_ms_as_str.zfill(self.start_time_str_len)
    self.out = ""
    # Check internal calculations haven't overflowed (doesn't detect ADC overflows)
    if self.ina.overflow:
      print("Internal Math Overflow Detected (non ADC) 3.2 Amps exceeded!")
    else:
      self.out = f"{time_in_ms:d},{bus_voltage:5.5f},{shunt_voltage:5.5f},{v_plus:5.5f},{current:5.5f},{power_calc:5.5f},{power:5.5f},{impedance_calc:5.5f}"
  def display_on_screen(self):
    print(f"{self.out}")
  def get_next_sample(self):
    """Method responsible for querying the INA and displaying the output"""
    self.create_output_string()
    self.display_on_screen()
    self.write_to_file()

i2c = busio.I2C(board.SCL, board.SDA)

object_array = []
ina_addresses = [64, 65, 68, 69]
ads_addresses = [72, 73]
# Can be configured with I2C addresses Default address 72, Soldered 73
# Use pin pairs A0+A1;A2+A3 for reference
# Gnd of measured VIN is same as QWIIC Gnd
# And max Vin is +.3v above QWIIC VDD (3.3v)
# Thus gain is always 1. You cannot use a gain of 2/3 unless QWIIC VDD is 5v
for address in ads_addresses:
  try:
    ads_5v = ADS.ADS1015(i2c, gain=1, address=address)
    ads_object_5v = ads_object(ads_5v, ADS.P0, ADS.P1, base_name=f"ADS1015_{address}_5v")
    object_array.append(ads_object_5v)
  except Exception as err:
    print(f"Unexpected {err=}, {type(err)=}")

  try:
    ads_3_3v = ADS.ADS1015(i2c, gain=1, address=address)
    ads_object_3_3v = ads_object(ads_3_3v, ADS.P2, ADS.P3, base_name=f"ADS1015_{address}_3_3v")
    object_array.append(ads_object_3_3v)
  except Exception as err:
    print(f"Unexpected {err=}, {type(err)=}")

# Create the INA219 objects
# Addresses: Default = 0x40 = 64, A0 soldered = 0x41 = 65,
# A1 soldered = 0x44 = 68, A0 and A1 soldered = 0x45 = 69
for address in ina_addresses:
  try:
    ina219_1 = INA219(i2c, addr=address)
    ina219_object_1 = ina_object(ina219_1, f"ina219_{address}")
    object_array.append(ina219_object_1)
  except Exception as err:
    print(f"Unexpected {err=}, {type(err)=}")

while len(object_array) != 0:
  for item in object_array:
    item.get_next_sample()
  time.sleep(0.25)
