# SilverSatPersonalDevWork

My work related to the Silver Sat team

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

pythonpath should be the path to python3 in your virtual environment
pythonpath=$(which python3)
pythonpath="#\!$pythonpath"
sed -i "1s/.\*/$pythonpath/" ./this-file.py
chmod +x ./this-file.py
```

## Documentation:

- ads1x15[https://docs.circuitpython.org/projects/ads1x15/en/stable/]
- ina219[https://docs.circuitpython.org/projects/ina219/en/stable/]

## Basic formulas:

1. Watts = V*I = I^2 * R = V^2/R
2. R = V \* I/I^2 = V/I = V^2/Watts = Watts/I^2
3. V = I\*R = Watts/I
4. I = V/R = Watts/V = (Watts/R)^0.5

## Some reasoning about the electronics needed

```
From this: A quater watt resistor at 5 volts must have a resistance of at least 100 ohm
However:
Based on GPIO limitations per pin. 50 mA total for all of the GPIO pins and .017 amps at 3.3v max:
3.3v * .017 amps = .0561 watts max per pin max. Min Resistance equals about 200 ohm
5v * .01122 amps =.0561 watts. Min Resistance equals about 450 ohm (but see below)
From the ADS1015 Datasheet:
VDD to GND –0.3 to +0.3 - using whatever volatage qwic is thus 3.3 volts. (So 3.0 to 3.6)
Analog input momentary current 100 mA
Analog input continuous current 10 mA (which means for 5.2v you actually need at least a 520 ohm resistor)
So for the 3.3v a single resistor in series is needed at greater than 200 ohm.
However:
At 5.2v a voltage divider or some other means would be needed to step down the voltage.
As it turns out voltage dividers are not a good choice because the voltage varies like a circuit in parrell.(which you could make with 3 4700 resistors)
Another way to do it would to put diodes is series with the load, which will drop the voltage about 0.6v per diode. So to get to 3.3v volts, the diodes ought to do. Then just make sure there is at least a 200 ohm load.
For this experiment the 3.3v lead has a 500 ohm resistor
The 5.2 volt lead has a 500 ohm followed by a 4700 ohm followed by a voltage divider followed by 2 4700 ohm.
```
