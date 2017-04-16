## Synopsis

4WD remote control robot controlled via WIFI, with an obstacle avoiding mode. This robot utilizes a Raspberry Pi 3 and also includes raspberry pi camera live stream capabilities.

## Code Example

```python
def changePath():
    print("stopping")
    servo_right()
    time.sleep(.5)
    rightDistance = ping() #set right distance
    print(rightDistance)
    time.sleep(.5)
    servo_left()
    time.sleep(.7)
    leftDistance = ping()  # set right distance
    print(leftDistance)
    time.sleep(.5)
    servo_center()
    time.sleep(.1)
    compareDistance(leftDistance,rightDistance)
```

## Motivation

Create a realtively cheap robot that contains the following features:
Remote Control
Obstacle Avoidance
Livestream Video

## Installation

Install adafruit library - https://learn.adafruit.com/adafruit-16-channel-servo-driver-with-raspberry-pi/using-the-adafruit-library

Install UV4L - https://www.linux-projects.org/uv4l/installation/

## License

MIT