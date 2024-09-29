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
- `R` = `V \* I/I^2 = V/I` = `V^2/Watts` = `Watts/I^2`
- `V` = `I\*R` = `Watts/I`
- `I` = `V/R` = `Watts/V` = `(Watts/R)^0.5`

## Some reasoning about the electronics needed

```
From this: A quater watt resistor at 5 volts must have a resistance of at least 100 ohm
However:

Based on GPIO limitations per pin:
50 mA total for all of the GPIO pins and .017 amps at 3.3v max:
3.3v * .017 amps = .0561 watts max per pin max. So min Resistance equals about 200 ohm
If the same wattage extends to 5v then:
5v * .01122 amps =.0561 watts. Min Resistance equals about 450 ohm (but see below)
However:

From the ADS1015 Datasheet:
VDD to GND –0.3 to +0.3
QWIC is is ued for VDD, thus 3.3 volts. (So 3.0 to 3.6)

Specs:
Analog input momentary current 100 mA
Analog input continuous current 10 mA
So for 5.2v you actually need at least a 520 ohm resistor, and
for the 3.3v a 200 ohm or greater resistor is needed.
However:

* At 5.2v a voltage divider or some other means would be needed to step down the voltage
to 3.3v.
* At first a voltage divider might seem like a good choice; however, voltage dividers
are not a good choice because the voltage varies like a circuit in parrell.
(If your interested 3 4700 ohm resistors could be used to make about the correct voltage
divider)
* Another way to do it would to put diodes is series with the load.
That will drop the voltage about .6 volts per diode. (3 diodes)
In turn at least a 200 ohm load will be needed.
```
