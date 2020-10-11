
#This code adapted from the Scuttle Library and altered by Jesse Rosart-Brodnitz
#Author: Jesse Rosart-Brodnitz
#Contact: jorbaustin@gmail.com
#Motor Overide for glitches and motor emergency stop
#primarily used to deal with the GPIO pins resetting 
# This example sends commands to two motors on the appropriate pins for H-bridge
# Designed for Pi hardware.

import gpiozero #gpiozero is the chosen library for PWM functionality
from gpiozero import PWMOutputDevice
import time
import RPi.GPIO as GPIO


#info on pins:
# Broadcom (BCM) pin numbering for Pi gives names of GPIO17
# and GPIO18 to physical pins 11 and 12
leftOutA = PWMOutputDevice(5, active_high=False, frequency=1000,initial_value=0)
leftOutB = PWMOutputDevice(12, active_high=False,frequency=1000,initial_value=0)

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


MotorL(0)
MotorR(0)

#GPIO.cleanup()

