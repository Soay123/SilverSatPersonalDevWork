# SilverSatPersonalDevWork

Work related to the Silver Sat team

###

## Prepare Raspberry Pi:

```
# With the monitor and power unplugged from the Pi install the QWIIC shim

# Enable I2C
sudo raspi-config
Select Interfacing Options
Select 'Yes' that I2C kernel module should be enabled
Then Finish and reboot (shutdown -r now)

# If this is your first time using this Pi then start here:
# Install Python3
apt install python3
python3 -m venv /home/me/Desktop/venv
/home/me/Desktop/venv/pip3 install --upgrade pip
/home/me/Desktop/venv/bin/pip3 install Adafruit-Blinka
/home/me/Desktop/venv/bin/pip3 install adafruit-circuitpython-ads1x15
/home/me/Desktop/venv/bin/pip3 install adafruit-circuitpython-ina219

# Install Git
apt install git
git config --global user.name "John Doe"
git config --global user.email johndoe@example.com
git config --global init.defaultBranch main

# Configure SSH
mkdir ~/.ssh
cd ~/.ssh
ssh-keygen -t ed25519
chmod 700 ~/.ssh
chmod 644 ~/.ssh/id_ed25519.pub
chmod 600 ~/.ssh/id_ed25519

cat ~/.ssh/id_ed25519.pub
# Copy the output. Its a long line and may wrap.

# Log into github
# Go to Settings -> GPG & SSH Keys
# Create a new key (name does not matter)
# Paste in text copied above

# Clone repository
mkdir /home/me/Desktop/code
cd /home/me/Desktop/code
git clone git@github.com:Soay123/SilverSatPersonalDevWork.git
cd SilverSatPersonalDevWork

# Update the first line of a file with the python3 path
pythonpath="/home/me/Desktop/venv/bin/python3"
pythonpath="#\!$pythonpath"
sed -i "1s/.\*/$pythonpath/" ./this-file.py
chmod +x ./this-file.py
```

```
# If you are coming back to a Pi you already configured then:
cd /home/me/Desktop/code/SilverSatPersonalDevWork
git pull origin main

## You made a local change to a file and already commited it locally
## Make a copy of your work
# git branch my-new-branch-name
## delete your changes
# git log
## copy the second md5 hash from the top
# git reset --hard <paste the md5 hash>
# git pull origin main
```

```
# If you get an ssh key authentication error then you probably
# have added your key to more than one github repository.
# Delete the key from both github repositories, and then add it back to one
```

```
# Now your local and remote are in sync. You are ready to go
# After editing your local copy
git commit -a -m "Short description of the change" -m "An optional really detailed description of the change"
git push origin main

# If you create new file you would like to track then you can add them
# by name or with a wildcard
git add *
```

## Documentation:

- [ADS1x15 API](https://docs.circuitpython.org/projects/ads1x15/en/stable/)
- [ADS1015 Datasheet](https://cdn-shop.adafruit.com/datasheets/ads1015.pdf)
- [INA219 API](https://docs.circuitpython.org/projects/ina219/en/stable/)
- [INA219 Datasheet](https://cdn-learn.adafruit.com/downloads/pdf/adafruit-ina219-current-sensor-breakout.pdf)

## Math note

- Depending on how voltage, current or power are measured by the sensor the actual value will have 3 to 8 significant digits after the decimal.
  1. Read the datasheet for units. For example mV.
  2. Read the datasheet for step. For example 100 uV.
  3. Read the datasheet for gain. For example step \* gain.
  4. Example gain is 16 (4 bits), and value is stored as 12 bits, making the largest number 16 bits, and the step 16 times as big. Which really means 7 significant digits total.
- Floating point numbers do not store the exact value, and add mantissa notation. Instead use the 'decimal' module. Invoke the Decimal constructor with a string representation of the number.
- Given that this can only measure up to 26 volts (two digits), then the precision should be 10. (maybe even just 7)

## Basic formulas:

- `Watts` = `V*I` = `I^2 * R` = `V^2/R`
- `R` = `V/I` = `V^2/Watts` = `Watts/I^2`
- `V` = `I*R` = `Watts/I` = `(R * Watts)^0.5`
- `I` = `V/R` = `Watts/V` = `(Watts/R)^0.5`

## TL;DR

1. Regarding the ADS1015:

- ADS1015 provides only voltage information
- Seems likely that the measured voltage must share the same ground as QWIIC VDD
- Various Vin to VDD combinations can use the circuits described at the end of the document
- A huge advantage of 12 rather than 16 bits is faster samples per second. 128 sps to 3300 sps depending on how the api constructor is invoked.
- Accuracy is a function of heat
- Gain = 2/3 = 6.144v max; Gain = 1 = 4.096v max
- So then at gain = 1, accuracy is 1 mV.
- Max gain error of .04% occurs at 85 degrees celsius.
- Differential offset error at 3v over entire operating tempeture range is about 3 uV
- Requires an input of at least 250 uA, .256v
- Do not exceed 10 mA and VDD + .3v
- With 3.3v, the resistor should be between (3.3 + .3)/.01 and 3.3/.00025 which is 360 to 13200 ohm.
- The step is:

2. Regarding the INA219

- High Side (i.e. in series before load, rather than between load and ground).
- Do not exceed 26v and 3.2 amps. (as best I can tell), but try to stay within 2 amps
- Ground does NOT need to be shared between load and QWIIC VDD
- 12 Bit ADC - Gain might need to be set?
- Put in the appropriate precautions if you are using an inductive load.
- INA219 measures voltage and current (and therefore also power)
- INA219 reports the average of 128 samples every 68.1 ms. (about 14 sps)
- INA219 has an accuracy of .8 mA (3.2/4096)

3. Regarding Vin of sample vs. VDD of QWIIC

- As discussed below some type of circuit would be needed to step down the voltage, but not to regulate it to a fixed amout.
- Easiest solution is probably to use diodes - then loading is not a concern.

## Some reasoning about the electronics needed

- Constraints (Read to the bottom)

1. A quarter watt resistor at 5 volts must have a resistance of at least 100 ohm
2. Based on GPIO limitations per pin:

- 50 mA total for all of the GPIO pins, and 17 mA at 3.3v max for one:
- 50 mA / 40 pins = 1.25 mA per pin normally.
- 3.3v \* 17mA = .0561 watts Vout max for a single pin.
  1. So min load at max current is about 200 ohm (3.3/.017) for Pi; however,
  2. ADS1015 is only rated to 10 mA. So min load = (3.3 + .3)/.01 = 360 Ohm
  - If the same wattage extends to 5v then:
  - 5v \* .01122 amps =.0561 watts.
    1. So min Resistance equals about 450 ohm for Pi; however,
    2. ADS1015 is only rated to 10 mA. So (5 + .3)/.01 = 530 Ohm at least

3. From the ADS1015 Datasheet:

- Parameters for ADS1015
  1. Can measure up to VDD +0.3 volts
  2. Analog input momentary current 100 mA; continuous current 10 mA
  3. QWIIC Shim is is used for VDD
  - Thus 3.3 volts. (So 3.6 volts max)
  - `3.6/0.010` = `R` = `360 Ohm`
  4. If 5v used for VDD, and 5.3v max, then you actually need at least a 530 ohm resistor
  5. The ADS1015 requires at least some current from Vin = 3.3/13200 = min current = .25 mA

4. If trying to measure above 3.6v, then some other means would be needed to step down the voltage. Aka. a level shifter.

- A voltage divider made using resistors

  1. R1 and R2 create a theroetical voltage divider; however,
  2. Once R3 is added, R2 and R3 are in paralel and the circuit is "loaded"

  - From wikipedia "To obtain a sufficiently stable output voltage, the output current must either be stable (and so be made part of the calculation of the potential divider values) or limited to an appropriately small percentage of the divider's input current."

  3. Example: In order to keep the ratio correct, R3 will need to be VERY large.
  4. Per the specs at 3.3v you cannot have more than 13200 ohm impedance and remain within the operating range of the sensor.

  - R3 > 3.6v/10mA
  - R3 < 3.3v/.25mA

  5. Parallel circuit Rt = 1/((1/R2)+(1/R3))
  6. Vout of voltage divider: Vin \* R2/(R1 + R2) = 3.3 (When R3 is infinite)
  7. Solve for R1 and R2 when

  - Vin \* Rt/(R1 + Rt) = Vout
  - R3 > ((Vout + .3)/.01)
  - R1 + R3 < 13200
  - Vin = 5, and Vout = 3.3

```

Vin---|
      R1
      |--R3--Sensor---|
      R2              |
Gnd---|---------------|

```

- A level shifter using diodes in series with the load.

1. That will drop the voltage about .6 or .7 volts per diode. (3 to 4 diodes)
2. Resistor values:

- 5.3 Vin - 3.3 Vout = 2.0v
- 2.0 div .6, +1 if 2.0 mod 6 != 0, thus 3 to 4 diodes (1.8 - 2.8 voltage drop)
- At least a 360 ohm load will be needed, given a Vout of 3.3v (3.6/.01 is minimum resistor value)

3. The diodes provide a constant offset to the actual voltage

```

Vin---|>|---|>|---|>|---R1---Sensor---Gnd

```

- And finally another way is to use 5v for VDD, 530 Ohm resistor, with a 2/3 gain setting on the ADS1015
- At the end of this readme I mention two other ways to do this too.

## Varoius Circuits

1. A level shifter using diodes seems the easiest to calculate.
2. To measure up to 3.6 volts with an ADS1015 at 3.3v VDD:

- Use a resistor with at least 360 Ohm impedance, and use a circuit like:

```

Vin---|360 Ohm|---|ADS1015|---Gnd

```

3. To measure up to 5.3 volts, with a ADS1015 at 5v VDD, 10 mA max:

- Set gain to 2/3, use a resistor with at least 530 Ohm impedance, and use a circuit like:

```

Vin---|530 Ohm|---|ADS1015|---Gnd

```

4. Crazy footnotes About Level Shifting

- Voltage dividers can be made of capacitors too. (Current is the same over all of the capacitors but voltage is different per capacitor)
- Using capacitors is more energy efficient, produces less heat, and is more accrute; however it is more sensitive to tempeture fluctions.
- Capacitors prevent the flow of DC current.
- Capacitors in a voltage divider do not have a specific frequency as in an RC circuit; however, the frequency affects the current.

  1. Genralized Capacitivie Reactance formula in Ohm:

  - Xc = 1/(2πfC)
  - Xc = Capacitive Reactance in Ohms, (Ω)
  - π (pi) = a numeric constant of 3.142
  - ƒ = Frequency in Hertz, (Hz)
  - C = Capacitance in Farads, (F)

  2. Calculate the Capacitive reactance (Ohm) of each capacitor using the formula above

  - X1 = 1/(2πfC1)
  - X2 = 1/(2πfC2)

  3. Calculate the total:

  - Xt = X1 + X2
  - Current in the circuit:
    1. I = Vin/Xt
    2. Voltage over each capacitor:
    - V1 = I \* X1
    - V2 = I \* X2
    - Note: Vin = V1 + V2

  4. Voltage at Vout can be calculated with the same formula as with resistors, or

  - Vout = Vin \* C1 / (C1 + C2)
  - Current is based on frequency.
    1. Take that into account so that you do not exceed 10 mA.
    2. A drain capacitor can be used to remove high frequencies

```

Vin---|
      C1
Vout--|
      C2
Gnd---|
```

5. A hybrid

```

Vin--------------|---|--Cs1--|
                 C1  |       |
                 |   R1      |
                 Rd1 |       |
|---|--R3--Vout--|---|--Cs2--|
|   |            C2  |       |
S   Z            |   R2      |
|   |            Rd2 |       |
|---|--Gnd-------|---|-------|
```

- Diagram Notes

  1. Cs1 = Cs2 = tiny nF drain for stray capacitance and high frequency
  2. C1, C2 for capacitive voltage divider for AC
  3. Rd1, Rd2 for damping (minimizes oscillation, such as voltage spikes, by reducing amplitude and frequency)
  4. R1 and R2 are the DC voltage divider resistors (5v in, 3.3v out)
  5. R3 13200 ohm
  6. Z zener diode for 3.6v volt drain
  7. S ADS1015 sensor

  - This probably means that the following constraints need to be calcultated:
    1. Voltage divider composed of resistors Vin=5, Vout=3.3
    2. Capacitive reactance + dampening resistor impedance where (Xc1 + Rd1) = R1; and (Xc2 + Rd2) = R2
    3. And the time constant (τ = RC) needs to be maintained so C1 \* Rd1 = C2 \* Rd2
    - Setting Rd to 0 solves this problem but removes damping

- To Do
  1. This still doesn't cover the effect of loading. Basically set the impedance on the Vout branch as high as possible (13200) and that controls your acceptable deviation from the ideal voltage divider.
- Referance
  1. [Balancing Super Capacitors](https://www.we-online.com/catalog/media/o671684v410%20ANP090a_EN.pdf)
