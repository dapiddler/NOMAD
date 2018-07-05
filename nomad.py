#!/usr/bin/env python

import os
import sys
import time
import signal
import curses
import PCA9685
import requests
import threading
import curses.textpad
import subprocess as sp
import RPi.GPIO as gpio
from network import get_ip
from SR04 import ping

rpiIP = str(get_ip()) #sets ip address of raspberry pi
COLL_DIST = 45 # sets distance at which robot stops and reverses to 30cm

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
    '''setup GPIO Pins'''
    gpio.setmode(gpio.BCM)
    gpio.setup(26, gpio.OUT)
    gpio.setup(19, gpio.OUT)
    gpio.setup(13, gpio.OUT)
    gpio.setup(12, gpio.OUT)


def reverse(tf):
    '''move backwards'''
    gpio.output(26, True)
    gpio.output(19, False)
    gpio.output(13, True) 
    gpio.output(12, False)
    time.sleep(tf)


def forward(tf):
    '''move forwards'''
    gpio.output(26, False)
    gpio.output(19, True)
    gpio.output(13, False) 
    gpio.output(12, True)
    time.sleep(tf)


def left(tf):
    '''pivot left'''
    gpio.output(26, False)
    gpio.output(19, True)
    gpio.output(13, True) 
    gpio.output(12, False)
    time.sleep(tf)


def right(tf):
    '''pivot right'''
    gpio.output(26, True)
    gpio.output(19, False)
    gpio.output(13, False) 
    gpio.output(12, True)
    time.sleep(tf)


def stop():
    '''dead stop'''
    gpio.output(26, False)
    gpio.output(19, False)
    gpio.output(13, False) 
    gpio.output(12, False)


def set_servo_pulse(channel, pulse):
    '''Helper function to make setting a servo pulse width simpler'''
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 60       # 60 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)


def message(input):
    """sends current status to flask server
    
    :param input: message to be sent
    :type input: string
    :returns: N/A
    :rtype: N/A
    """

    url = "http://%s:5000/events" % (rpiIP)
    payload = "{\"value\":\"%s\"}" % (input)
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache",
        'postman-token': "49121925-c1b5-8071-4463-8c1f8f835a9a"
    }
    response = requests.request("POST", url, data=payload, headers=headers)


def servo_left():
    '''Physically move servo to left most position'''
    pwm.set_pwm(0, 0, servo_min)


def servo_center():
    '''Physically move servo to center position'''
    pwm.set_pwm(0, 0, servo_mid)


def servo_right():
    '''Physically move servo to right most position'''
    pwm.set_pwm(0, 0, servo_max)


def ai_loop():
    '''Main obstacle avoidance loop'''
    servo_center()
    curDist = ping() # read distance in cm
    if (curDist < COLL_DIST):
        print("changing directions")
        stop()
        change_path() # if forward is blocked change direction
    forward(.025)
    print("moving forwards")


def change_path():
    '''stores distance values and calls function'''
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
    compare_distance(leftDistance,rightDistance)


def compare_distance(leftUnit,rightUnit):
    '''compares values and moves robot
    
    :param leftUnit: ultrasonic reading left
    :param rightUnit: ultrasonic reading right
    :type leftUnit: int
    :type rightUnit: int
    :returns: N/A
    :rtype: N/A
    '''
    if (leftUnit > rightUnit):
        left(2)
        print("turning left")
        message("turning left")
    elif (rightUnit > leftUnit):
        right(2)
        print("turning right")
        message("turning right")
    else:
        left(6)
        print("pulling a u-turn")
        message("pulling a u-turn")


def spawn_thread(arg):
    '''create AI thread with exit flag'''
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        print ("working on %s" % arg)
        ai_loop()
    print("Exiting AI process")


def check_kill_process(pstring):
    '''Kills python process
    
    :param pstring: process name
    :type input: string
    :returns: N/A
    :rtype: N/A
    '''
    for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
        fields = line.split()
        pid = fields[0]
        os.kill(int(pid), signal.SIGKILL)


def shutdown():
    '''Shutdown Script Procedure/Cleanup'''
    os.system('pkill uv4l')  # kill uv4l video streaming server
    check_kill_process("python")  # kill flask server
    process.kill()  # kill flask server dead


def main():
    '''main loop'''
    sleep_value = .035
    init()
    t = None
    stdscr = curses.initscr()
    curses.noecho()
    try:
        while 1:
            key = stdscr.getch()
            if key == ord('i'):
                print("Thread Started")
                t = threading.Thread(target=spawn_thread, args=("",))
                t.start()
                print(key)
            elif key == ord('k'):
                print("Thread Ended")
                t.do_run = False
                t.join()
                stop()
                print(key)
            elif key == ord('w'):
                forward(sleep_value)
                stop()
                print(key)
            elif key == ord('s'):
                reverse(sleep_value)
                stop()
                print(key)
            elif key == ord('a'):
                left(sleep_value)
                stop()
                print(key)
            elif key == ord('d'):
                right(sleep_value)
                stop()
                print(key)
            elif key == ord('q'):
                if t.isAlive():
                    t.do_run = False
                    t.join()
                    stop()
                    gpio.cleanup()
                    curses.endwin()
                    break
                else:
                    stop()
                    gpio.cleanup()
                    curses.endwin()
                    break
    except NameError:
        stop()
        gpio.cleanup()
        curses.endwin()

if __name__ == "__main__":
    os.system('uv4l --driver raspicam --auto-video_nr --width 640 --height 480 --encoding jpeg') #initiate uv4l video streaming server
    process = sp.Popen('python /home/pi/NOMAD/web/webserver.py', shell=True, stdout=sp.PIPE, stderr=sp.PIPE) #start flask server
    main()
    shutdown()


