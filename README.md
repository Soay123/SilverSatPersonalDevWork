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

2. Regarding the INA219

- High Side (i.e. in series before load, rather than between load and ground).
- Do not exceed 64 watts and 3.2 amps.
- Ground does NOT need to be shared between load and QWIIC VDD
- 12 Bit ADC - Gain might need to be set
- Put in the appropriate precautions if you are using an inductive load.
- INA219 measures voltage and current (and therefore also power)

## Some reasoning about the electronics needed

Read to the bottom

1. A quarter watt resistor at 5 volts must have a resistance of at least 100 ohm
2. Based on GPIO limitations per pin:

- 50 mA total for all of the GPIO pins, and .017 amps at 3.3v max for one:
- 3.3v \* .017 amps = .0561 watts max per pin max.
  1. So min Resistance equals about 200 ohm for Pi; however,
  2. ADS1015 is only rated to 10 mA. So (3.3 + .3)/.01 = 360 Ohm at least
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

4. If trying to measure above 3.6v, then some other means would be needed to step down the voltage.

- At first a voltage divider might seem like a good choice
  1. Voltage dividers are not a good choice because both legs share a common ground. Thus voltage varies like a circuit in parrell.
  - This could be done with a 4700 Ohm, and 9100 Ohm; or 3 4700 Ohm for simplicity.
- Another way to do it would be to put diodes is series with the load.
  1. That will drop the voltage about .6 volts per diode. (3 diodes)
  2. In turn at least a 360 ohm load will be needed.
  3. This is a constant offset
- And finally another way is to use 5v for VDD, 530 Ohm resistor, with a 2/3 gain setting on the ADS1015

## Varoius Circuits

1. To measure 5.2 volts, with a ADS1015 at 3.3v VDD, at 10 mA:

- Use a resistor with at least 360 Ohm impedance, and 3 diodes with a .6 to .7 voltage drop per diode:

```
Vin--Diode-Diode-Diode---Resistor-----Load------Gnd
Vin---|>|---|>|---|>|---|360 Ohm|---|ADS1015|---Gnd
```

2. To measure up to 3.6 volts with an ADS1015 at 3.3v VDD:

- Use a resistor with at least 360 Ohm impedance, and use a circuit like:

```
Vin---|360 Ohm|---|ADS1015|---Gnd
```

3. To measure 5.2 volts, with a ADS1015 at 5v VDD, 10 mA max:

- Set gain to 2/3, use a resistor with at least 530 Ohm impedance, and use a circuit like:

```
Vin---|530 Ohm|---|ADS1015|---Gnd
```
