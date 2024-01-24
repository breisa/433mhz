# 433.py
A command-line tool to record, plot and replay arbitrary digital 433mhz signals using a Raspberry Pi.

Using this tool, a Raspberry Pi and a set of cheap [433mhz receiver/sender modules](https://www.amazon.de/433-mhz-transmitter/s?k=433+mhz+transmitter) you can work with 433mhz signals.
This allows to clone key fobs, garage door openers and remote controls that send data on 433mhz.
These kind of devices typically sends a static repeating code when their buttons are pressed.
Once you recorded a code with `--record`, you can view it using `--plot` and replay it using `--send`.



## How to use it?
```
usage: 433.py [-h] (--record GPIO | --plot | --send GPIO) [--recordlen MS] FILE

positional arguments:
  FILE            the json file to load or store a signal

options:
  -h, --help      show this help message and exit
  --record GPIO   record a signal on gpio pin GPIO and store it in FILE
  --plot          plot the signal stored in FILE
  --send GPIO     replay the signal stored in FILE on gpio pin GPIO
  --recordlen MS  amount of milliseconds to record (defaults to 250ms)

```

## Example
We will use the tool to clone the remote control of a set of remote controlled power sockets like [these](https://www.amazon.de/Brennenstuhl-Funkschalt-Set-Funksteckdosen-Funksteckdose-Kindersicherung/dp/B07CGBRS7T/).

### Wiring
The receiver module is typtically rectangular and should have 4 pins: VCC, DATA1, DATA2, GND. Connect VCC to the Pi's 3.3V output, GND to the Pi's GND and either DATA1 or DATA2 to one of the Pi's [GPIO pins](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#gpio-and-the-40-pin-header). Note the GPIO number (not the pin number) that you connected to DATA. The GPIO number depends on the specific board you are using. See the [pigpio documentation](https://abyz.me.uk/rpi/pigpio/#GPIO) for a board-dependant pin/gpio mapping.

The typically square sender module has only 3 pins: DATA, VCC, GND. Connect VCC to the Pi's 5V output, GND to the Pi's GND and DATA to another one of the Pi's GPIO pins. Note the GPIO number.

tbc
