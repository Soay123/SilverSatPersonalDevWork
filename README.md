# SilverSatPersonalDevWork

Work related to the Silver Sat team

###

## Prepare Raspberry Pi:

```
apt install python
apt install git
git config --global user.name "John Doe"
git config --global user.email johndoe@example.com
git config --global init.defaultBranch main
mkdir ~/.ssh
cd ~/.ssh
ssk-keygen -t ed25519
chmod 700 ~/.ssh
chmod 644 ~/.ssh/id_ed25519.pub
chmod 600 ~/.ssh/id_ed25519

<log into github and add public key>

pip3 install --upgrade pip
python3 -m venv /path/to/new/virtual/environment
/path/to/new/virtual/environment/bin/pip3 install Adafruit-Blinka
/path/to/new/virtual/environment/bin/pip3 install adafruit-circuitpython-ads1x15
/path/to/new/virtual/environment/bin/pip3 install adafruit-circuitpython-ina219
mkdir ~/code
cd ~/code
git clone <whatever the git path to your repo is>
cd repo-name

# pythonpath should be the path to python3 in your virtual environment
pythonpath=$(which python3)
pythonpath="#\!$pythonpath"
sed -i "1s/.\*/$pythonpath/" ./this-file.py
chmod +x ./this-file.py
```

## Documentation:

- [ADS1x15 API](https://docs.circuitpython.org/projects/ads1x15/en/stable/)
- [ADS1015 Datasheet](https://cdn-shop.adafruit.com/datasheets/ads1015.pdf)
- [INA219 API](https://docs.circuitpython.org/projects/ina219/en/stable/)
- [INA219 Datasheet](https://cdn-learn.adafruit.com/downloads/pdf/adafruit-ina219-current-sensor-breakout.pdf)
  550,4700

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
- Max gain error of .04% occurs at 85 degrees celsius.
- Differential offset error at 3v over entire operating tempeture range is about 3 uV
- Requires an input of at least 250 uA, .256v, means that at bottom of range R <=1024. So if you want to be able to sense the entire range with low power then the resistor should be between 530 and 1024 ohm. With more power the resistor should be between 530 and 13200 ohm.

2. Regarding the INA219

- High Side (i.e. in series before load, rather than between load and ground).
- Do not exceed 64 watts and 3.2 amps. (as best I can tell)
- Ground does NOT need to be shared between load and QWIIC VDD
- 12 Bit ADC - Gain might need to be set?
- Put in the appropriate precautions if you are using an inductive load.
- INA219 measures voltage and current (and therefore also power)
- INA219 reports the average of 128 samples every 68.1 ms. (about 14 sps)
- INA219 has an accuracy of .8 mA

3. Regarding Vin of sample vs. VDD of QWIIC

- As discussed below some type of circuit would be needed to step down the voltage, but not to regulate it to a fixed amout.
- Easiest solution is probably to use diodes.

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

- A voltage divider made using resistors (Current is different over each resistor, but voltage is the same)

  1. R1 and R2 create a theroetical voltage divider; however,
  2. Once R3 is added, R2 and R3 are in paralel.
  3. In order to keep the ratio correct, R3 will need to be very large.
  4. Per the specs at 3.3v you cannot have more than 13200 ohm impedance and remain within the operating range of the sensor. 360 < R3 < 13200 ohm
  5. Parallel circuit Rt = ((1/R2)+(1/R3))
  6. Vout of voltage divider: Vin \* R2/(R1 + R2) = 3.3 (When R3 is infinite)
  7. Solve for R1 and R2 when

  - Vin \* Rt/(R1 + Rt) = Vout
  - ((Vout + .3)/.01) < R3 < 13200
  - Vin = 5, and Vout = 3.3

```

Vin---|
      R1
      |--R3--Sensor---|
      R2              |
Gnd---|---------------|

```

- A level shifter using diodes in series with the load.

1. That will drop the voltage about .6 volts per diode. (3 diodes)
2. Resistor values:

- At least a 530 ohm load will be needed, given a VDD of 5v, and a Vin which is not greater than 5.3v, and 5.3/.01 is minimum resistor value.
- At least a 360 ohm load will be needed, given a VDD of 3.3v, and a Vin which is not greater than 3.6v, and 3.6/.01 is minimum resistor value.

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

- Voltage dividers can be made of capacitors too. (Current is the same over all of the capacitors but voltage is different)
- Capacitors prevent the flow of DC current.
- Capacitors in a voltage divider do not have a specific frequency as in an RC circuit.

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
    - V1 = I \_ X1
    - V2 = I \_ X2
    - Note: Vin = V1 + V2

  4. Voltage at Vout

  - Voltage Divider: (X1 \* X2)/(X1+X2)
  - Current is the same over entire circuit
  - Since I is the same, be sure to take that into account so that you do not exceed 10 mA

```

Vin----|------|--Cs1--|
C1 | |
| R1 |
Rd1 | |
Vout---|------|--Cs2--|
C2 | |
| R2 |
Rd2 | |
Gnd----|------|-------|
```

5. A hybrid

```

Vin----|------|--Cs1--|
C1 | |
| R1 |
Rd1 | |
Vout---|------|--Cs2--|
C2 | |
| R2 |
Rd2 | |
Gnd----|------|-------|
```

- Diagram Notes
  1. Cs1, Cs2 are for stray capacitance
  2. C1, C2 for capacitive voltage divider for AC
  3. Rd1, Rd2 for damping (minimizes osilation and prevents voltage spikes)
  4. R1, R2 voltage divider resistors for DC voltage
- Electrical Notes

1. When a capacitor and resistor are placed in parallel, they share the same voltage, and the current through each component is calculated based on their individual impedance.
2. Since the damping resistor and the shunt resistor are in parallel, their combined resistance is calculated using the formula: 1/(1/R_damping + 1/R_shunt)
3. Once you have the combined resistance, you can use the time constant formula (τ = RC) to find the capacitor value needed to achieve the desired time constant.

- Example problem:
  1. You want to design a circuit with a time constant of 10 milliseconds. The damping resistor has a resistance of 10 ohms, and the shunt resistor has a resistance of 100 ohms. What capacitor value is needed?
- Solution:
  1. Calculate the combined resistance: 1 / (1/10 + 1/100) = 9 ohms
  2. Calculate the capacitor value: C = τ / R = 0.01 seconds / 9 ohms = 0.0011 Farads (or 1.1 millifarads)
