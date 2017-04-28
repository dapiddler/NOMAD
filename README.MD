# Nomad
#### A nomad is a person with no settled home, moving from place to place as a way of obtaining food, finding pasture for livestock, or otherwise making a living. The word Nomad comes from a Greek word that means one who wanders for pasture.

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

Create a realtively cheap robot for educational purposes that contains the following features:
1. Remote Control Functionality
2. Obstacle Avoidance
3. Livestream Video

## Installation

'''bash
pip install requirements.txt
'''

Install UV4L - https://www.linux-projects.org/uv4l/installation/

## Usage

Keyboard controls:
* W - Forward
* S - Reverse
* A - Left
* D - Right
* I - Create Obstacle avoidance thread
* K - Kill Obstacle avoidance thread
* Q - Exit script

Dashboard:
Navigate to http://[RPI-IP]:5000/nomad/

![Screenshot](Dashboard.png)

## License

MIT