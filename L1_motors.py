
# This example sends commands to two motors on the appropriate pins for H-bridge
# Designed for Pi hardware.

import gpiozero #gpiozero is the chosen library for PWM functionality
from gpiozero import PWMOutputDevice
import time
import RPi.GPIO as GPIO

#info on pins:
# Broadcom (BCM) pin numbering for Pi gives names of GPIO17
# and GPIO18 to physical pins 11 and 12

#use this if high/low pins reverse
leftOutA = PWMOutputDevice(5, active_high=False, frequency=1000,initial_value=0)
leftOutB = PWMOutputDevice(12, active_high=False,frequency=1000,initial_value=0)

# leftOutA = PWMOutputDevice(5, frequency=1000,initial_value=0)
# leftOutB = PWMOutputDevice(12, frequency=1000,initial_value=0)

RightOutA = PWMOutputDevice(6, frequency=1000,initial_value=0)
RightOutB = PWMOutputDevice(13, frequency=1000,initial_value=0)

# This section shows another way to assign parameters if uncommented
# leftOutA.frequency = 1000 #this is redundant
# leftOutA.value = 0.0 # this is for duty cycle

#channel refers to left(0) or right(1)
def MotorL(speed):
    if speed>0:
        leftOutB.value = speed
        leftOutA.value = 0
    elif speed<0:
        leftOutB.value = 0
        leftOutA.value = (-1*speed) #drive opposite polarity with positive duty cycle
    elif speed==0:
        leftOutB.value = 0
        leftOutA.value = 0

def MotorR(speed):
    if speed>0:
        RightOutB.value = speed
        RightOutA.value = 0
    elif speed<0:
        RightOutB.value = 0
        RightOutA.value = (-1*speed) #drive opposite polarity with positive duty cycle
    elif speed==0:
        RightOutB.value = 0
        RightOutA.value = 0

#Uncomment the section below to run this code by itself!
if __name__ == "__main__":
    while True:  # This loop will drive both motors forwards and backwards, repeatedly
        try:
            print("running")
            MotorL(1)
            MotorR(1)
            time.sleep(2)
                

            MotorR(0)
                
            MotorL(0)
            time.sleep(2)
        except KeyboardInterrupt:
            GPIO.cleanup()

            pass


# 




