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

- [ads1x15](https://docs.circuitpython.org/projects/ads1x15/en/stable/)
- [ina219](https://docs.circuitpython.org/projects/ina219/en/stable/)

## Basic formulas:

- `Watts` = `V*I` = `I^2 * R` = `V^2/R`
- `R` = `V/I` = `V^2/Watts` = `Watts/I^2`
- `V` = `I*R` = `Watts/I` = `(R * Watts)^0.5`
- `I` = `V/R` = `Watts/V` = `(Watts/R)^0.5`

## TL;DR

- Do not use a voltage divider. It becomes a parallel circuit when connected to gound
- For 5.2 volts use a circuit like:

```
Vin--Diode-Diode-Diode--Resistor---Load---Gnd
Vin---|>|---|>|---|>|---|520 Ohm|---|ADS1015|---Gnd
```

- For 3.3 vollts use a circuit like:

```
Vin---|200 Ohm|---|ADS1015|---Gnd
```

- I skipped the INA219
  1. Some load is needed, but I do not know what max amps are (5mA?)
  2. Max volts is 26 (5200 Ohm load needed if max 5mA)

## Some reasoning about the electronics needed

Read to the bottom

1. A quater watt resistor at 5 volts must have a resistance of at least 100 ohm
2. Based on GPIO limitations per pin:

- 50 mA total for all of the GPIO pins, and .017 amps at 3.3v max for one:
- 3.3v \* .017 amps = .0561 watts max per pin max. So min Resistance equals about 200 ohm
- If the same wattage extends to 5v then:
- 5v \* .01122 amps =.0561 watts. Min Resistance equals about 450 ohm

3. From the ADS1015 Datasheet:

- Parameters
  1. VDD to GND –0.3 to +0.3
  2. QWIC is is used for VDD, thus 3.3 volts. (So 3.0 to 3.6)
  3. Analog input momentary current 100 mA; continuous current 10 mA
- So for 5.2v you actually need at least a 520 ohm resistor, and
- For the 3.3v a 200 ohm or greater resistor is needed.

4. At 5.2v a voltage divider or some other means would be needed to step down the voltage
   to 3.3v.

- At first a voltage divider might seem like a good choice
  1. voltage dividers are not a good choice because the voltage varies like a circuit in parrell.
  - This could be done with a 4700 Ohm, and 9100 Ohm; or 3 4700 Ohm for simplicity.
  2. Another way to do it would be to put diodes is series with the load.
  - That will drop the voltage about .6 volts per diode. (3 diodes)
  - In turn at least a 200 ohm load will be needed.
  - This is a constant offset
  3. Use 5v for VDD, with a 2/3 gain setting on the ADS
