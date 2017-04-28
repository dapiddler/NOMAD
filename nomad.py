#!/usr/bin/env python
import RPi.GPIO as gpio
import curses
import curses.textpad
import time
import sys
import os
import threading
import PCA9685
import signal
import requests
import subprocess as sp
from HOST import get_ip
from SR04 import ping

rpiIP = str(get_ip()) #sets ip address of raspberry pi
MAX_DISTANCE = 300 # sets maximum useable sensor measuring distance to 300cm
COLL_DIST = 45 # sets distance at which robot stops and reverses to 30cm
TURN_DIST = COLL_DIST+20 # sets distance at which robot veers away from object

#distances on either side
leftDistance = 0
rightDistance = 0
curDist = 0

pwm = PCA9685.PCA9685()
pwm.set_pwm_freq(60) # Set frequency to 60hz, good for servos.

# Configure min and max servo pulse lengths
servo_min = 300  # Min pulse length out of 4096
servo_max = 500  # Max pulse length out of 4096
servo_mid = 405 # Mid pulse length out of 4096

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


def set_servo_pulse(channel, pulse):
    """Helper function to make setting a servo pulse width simpler."""
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 60       # 60 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)

def message(input):
    """sends current status to flask server"""
    url = "http://%s:5000/events" %(rpiIP)
    payload = "{\"value\":\"%s\"}" %(input)
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache",
        'postman-token': "49121925-c1b5-8071-4463-8c1f8f835a9a"
    }
    response = requests.request("POST", url, data=payload, headers=headers)

def servo_left():
    """Physically move servo to left most position"""
    pwm.set_pwm(0, 0, servo_min)

def servo_center():
    """Physically move servo to center position"""
    pwm.set_pwm(0, 0, servo_mid)

def servo_right():
    """Physically move servo to right most position"""
    pwm.set_pwm(0, 0, servo_max)

def loop():
    """Main obstacle avoidance loop"""
    servo_center()
    curDist = ping() # read distance in cm
    if (curDist < COLL_DIST):
        print("changing directions")
        stop()
        changePath() # if forward is blocked change direction
    forward(.025)
    print("moving forwards")

def changePath():
    """stores distance values and calls function"""
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
    """compares values and moves robot"""
    if (leftUnit>rightUnit):
        left(2)
        print("turning left")
        message("turning left")
    elif (rightUnit>leftUnit):
        right(2)
        print("turning right")
        message("turning right")
    else:
        left(6)
        print("pulling a u-turn")
        message("pulling a u-turn")

def doit(arg):
    """create AI thread with exit flag"""
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        print ("working on %s" % arg)
        loop()
    print("Exiting AI process")

def check_kill_process(pstring):
    """Kills python process"""
    for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
        fields = line.split()
        pid = fields[0]
        os.kill(int(pid), signal.SIGKILL)

def main():
    init()

    stdscr = curses.initscr()

    curses.noecho()
    try:
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
                    break
                    gpio.cleanup()
                break
                gpio.cleanup()
    except NameError:
        gpio.cleanup()

    curses.endwin()

if __name__ == "__main__":
    os.system('uv4l --driver raspicam --auto-video_nr --width 640 --height 480 --encoding jpeg') #initiate uv4l video streaming server
    process = sp.Popen('python /home/pi/NOMAD/web/webserver.py', shell=True, stdout=sp.PIPE, stderr=sp.PIPE) #start flask server
    main()
    os.system('pkill uv4l') #kill uv4l video streaming server
    check_kill_process("python") # kill flask server
    process.kill() # kill flask server dead
