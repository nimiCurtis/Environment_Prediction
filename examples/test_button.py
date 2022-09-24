# GPIO library
import Jetson.GPIO as GPIO

# Handles time
import time 

# Pin Definition
button_pin = 15

# Set up the GPIO channel
GPIO.setmode(GPIO.BOARD) 
GPIO.setup(button_pin, GPIO.IN) 

while True:
    time.sleep(0.01)
    x=GPIO.input(button_pin)
    print(x)
