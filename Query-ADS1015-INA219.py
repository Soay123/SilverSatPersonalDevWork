#!/path/to/new/virtual/environment/bin/python3
import os
import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_ina219

# Prepare Raspberry Pi:
# apt install python
# apt install git
# git config --global user.name "John Doe"
# git config --global user.email johndoe@example.com
# git config --global init.defaultBranch main
# mkdir ~/.ssh
# cd ~/.ssh
# ssk-keygen -t ed25519
# chmod 700 ~/.ssh
# chmod 644 ~/.ssh/id_ed25519.pub
# chmod 600 ~/.ssh/id_ed25519
#
# <log into github and add public key>
#
# pip3 install --upgrade pip
# python3 -m venv /path/to/new/virtual/environment
# /path/to/new/virtual/environment/bin/pip3 install Adafruit-Blinka
# /path/to/new/virtual/environment/bin/pip3 install adafruit-circuitpython-ads1x15
# /path/to/new/virtual/environment/bin/pip3 install adafruit-circuitpython-ina219
# mkdir ~/code
# cd ~/code
# git clone <whatever the git path to your repo is>
# cd repo-name
## pythonpath should be the path to python3 in your virtual environment
# pythonpath=$(which python3)
# pythonpath="#\!$pythonpath"
# sed -i "1s/.*/$pythonpath/" ./this-file.py
# chmod +x ./this-file.py

# Documentation:
# https://docs.circuitpython.org/projects/ads1x15/en/stable/
# https://docs.circuitpython.org/projects/ina219/en/stable/

# Basic formulas:
# Watts = V*I = I^2 * R = V^2/R
# R = V * I/I^2 = V/I = V^2/Watts = Watts/I^2
# V = I*R = Watts/I
# I = V/R = Watts/V = (Watts/R)^0.5

# From this: A quater watt resistor at 5 volts must have a resistance of at least 100 ohm
# However:
# Based on GPIO limitations per pin. 50 mA total for all of the GPIO pins:
# 3.3v * .017 amps = .0561 watts max per pin max. Min Resistance equals about 200 ohm
# 5v * .01122 amps =.0561 watts. Min Resistance equals about 450 ohm (but see below)
# From the ADS1015 Datasheet:
# VDD to GND –0.3 to +0.3 - using whatever volatage qwic is thus 3.3 volts. (So 3.0 to 3.6)
# Analog input momentary current 100 mA
# Analog input continuous current 10 mA (which means for 5.2v you actually need at least a 520 ohm resistor)
# For this experiment the 3.3v lead has a 500 ohm resistor
# The 5.2 volt lead has a 500 ohm followed by a 4700 ohm followed by a voltage divider followed by 2 4700 ohm.

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
# Use pin pairs A0+A1,A2+A3 for reference
# ADS Gain must literally be the float value 2/3 to allow ~ 6volts
# Somehow when 3.3v and 5v are on, 5v measures 3.8
ads_5v = ADS.ADS1015(i2c, gain=1, address=72)
ads_object_5v = ads_object(ads_5v, ADS.P0, ADS.P1, base_name="ADS1015_72_5v")
object_array.append(ads_object_5v)

ads_3_3v = ADS.ADS1015(i2c, gain=1, address=72)
ads_object_3_3v = ads_object(ads_3_3v, ADS.P2, ADS.P3, base_name="ADS1015_72_3_3v")
object_array.append(ads_object_3_3v)

# ads_5v = ADS.ADS1015(i2c, gain=2/3, address=73)
# ads_object_5v = ads_object(ads_5v, ADS.P0, ADS.P1, base_name="ADS1015_73_5v")
# object_array.append(ads_object_5v)

# ads_3_3v = ADS.ADS1015(i2c, gain=1, address=73)
# ads_object_3_3v = ads_object(ads_3_3v, ADS.P2, ADS.P3, base_name="ADS1015_73_3_3v")
# object_array.append(ads_object_3_3v)


# Create the INA219 objects
# Addresses: Default = 0x40 = 64, A0 soldered = 0x41 = 65,
# A1 soldered = 0x44 = 68, A0 and A1 soldered = 0x45 = 69
ina219_1 = adafruit_ina219.INA219(i2c, addr=64)
ina219_object_1 = ina_object(ina219_1, "ina219_64")
object_array.append(ina219_object_1)

# ina219_2 = adafruit_ina219.INA219(i2c, addr=65)
# ina219_object_2 = ina_object(ina219_2, "ina219_65")
# object_array.append(ina219_object_2)
#
# ina219_3 = adafruit_ina219.INA219(i2c, addr=68)
# ina219_object_3 = ina_object(ina219_3, "ina219_68")
# object_array.append(ina219_object_3)
#
# ina219_4 = adafruit_ina219.INA219(i2c, addr=69)
# ina219_object_4 = ina_object(ina219_4, "ina219_69")
# object_array.append(ina219_object_4)

while True:
  for item in object_array:
    item.get_next_sample()
  time.sleep(0.25)
