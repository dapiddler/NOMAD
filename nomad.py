#!/usr/bin/env python
import RPi.GPIO as gpio
import curses
import curses.textpad
import time
import sys
import os
import threading
import PCA9685
from SR04 import ping

MAX_DISTANCE = 300 # sets maximum useable sensor measuring distance to 300cm
COLL_DIST = 45 # sets distance at which robot stops and reverses to 30cm
TURN_DIST = COLL_DIST+20 # sets distance at which robot veers away from object

#distances on either side
leftDistance = 0
rightDistance = 0
curDist = 0

pwm = PCA9685.PCA9685()

# Configure min and max servo pulse lengths
servo_min = 300  # Min pulse length out of 4096
servo_max = 500  # Max pulse length out of 4096
servo_mid = 405

# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)

def init():
    """GPIO setup"""
    gpio.setmode(gpio.BCM)
    gpio.setup(26, gpio.OUT)
    gpio.setup(19, gpio.OUT)
    gpio.setup(13, gpio.OUT)
    gpio.setup(12, gpio.OUT)

def reverse(tf):
    gpio.output(26, True)
    gpio.output(19, False)
    gpio.output(13, True) 
    gpio.output(12, False)
    time.sleep(tf)

def forward(tf):
    gpio.output(26, False)
    gpio.output(19, True)
    gpio.output(13, False) 
    gpio.output(12, True)
    time.sleep(tf)

def left(tf):
    gpio.output(26, False)
    gpio.output(19, True)
    gpio.output(13, True) 
    gpio.output(12, False)
    time.sleep(tf)

def right(tf):
    gpio.output(26, True)
    gpio.output(19, False)
    gpio.output(13, False) 
    gpio.output(12, True)
    time.sleep(tf)

def stop():
    gpio.output(26, False)
    gpio.output(19, False)
    gpio.output(13, False) 
    gpio.output(12, False)

# Helper function to make setting a servo pulse width simpler.
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 60       # 60 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)


def servo_left():
    pwm.set_pwm(0, 0, servo_min)

def servo_center():
    pwm.set_pwm(0, 0, servo_mid)

def servo_right():
    pwm.set_pwm(0, 0, servo_max)

def loop():
    servo_center()
    curDist = ping() # read distance in cm
    if (curDist < COLL_DIST):
        print("changing directions")
        stop()
        changePath() # if forward is blocked change direction
    forward(.025)
    print("moving forwards")

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

def compareDistance(leftUnit,rightUnit):
    if (leftUnit>rightUnit):
        left(2)
        print("turning left")
    elif (rightUnit>leftUnit):
        right(2)
        print("turning right")
    else:
        left(6)
        print("pulling a u-turn")

def doit(arg):
    """AI thread with exit flag"""
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        print ("working on %s" % arg)
        loop()
    print("Exiting AI process")

def main():
    init()

    stdscr = curses.initscr()

    curses.noecho()

    while 1:
        c = stdscr.getch()
        if c == ord('i'):
            print("Thread Started")
            t = threading.Thread(target=doit, args=("",))
            t.start()
            print(c)
        elif c == ord('k'):
            print("Thread Ended")
            t.do_run = False
            t.join()
            stop()
            print(c)
        elif c == ord('w'):
            forward(.035)
            stop()
            print c
        elif c == ord('s'):
            reverse(.035)
            stop()
            print c
        elif c == ord('a'):
            left(.035)
            stop()
            print c
        elif c == ord('d'):
            right(.035)
            stop()
            print c
        elif c == ord('q'):
            if t.isAlive():
                t.do_run = False
                t.join()
                stop()
            break # Exit the while()

    curses.endwin()

if __name__ == "__main__":
    os.system('uv4l --driver raspicam --auto-video_nr --width 640 --height 480 --encoding jpeg') #initiate uv4l video streaming server
    main()
    os.system('pkill uv4l') #kill uv4l video streaming server
