import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)

def ping():
	"""Get reading from HC-SR04"""
	GPIO.setmode(GPIO.BCM)
	 
	TRIG = 23 
	ECHO = 18
	 
	GPIO.setup(TRIG,GPIO.OUT)
	GPIO.setup(ECHO,GPIO.IN)
	 
	GPIO.output(TRIG, False)
	time.sleep(1)
	 
	GPIO.output(TRIG, True)
	time.sleep(0.00001)
	GPIO.output(TRIG, False)
	 
	while GPIO.input(ECHO)==0:
	  pulse_start = time.time()
	 
	while GPIO.input(ECHO)==1:
	  pulse_end = time.time()
	 
	pulse_duration = pulse_end - pulse_start
	 
	distance = pulse_duration * 17150
	 
	distance = round(distance, 2)
	 
	print "Distance:",distance,"cm"
	 
	GPIO.cleanup()

print "Reading Distance \n"

while True:
	ping()
