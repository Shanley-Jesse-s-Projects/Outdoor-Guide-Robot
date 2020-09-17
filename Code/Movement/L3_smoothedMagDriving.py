# SmoothedMagDriving

# Code purpose: DRIVING BY COLOR TRACKING WITH CLOSED-LOOP STEERING CONTROL
#   This program captures an image, discovers a target within your HSV range
#   Generates a pixel location of the target, and estimates the angle of the
#   target from the camera's centerline (x-y plane) called ThetaOffset.

# Import external libraries
import numpy as np
import time

# Import internal programs
import L2_heading as heading
import L2_kinematics as kin
import L2_speed_control as sc
import L2_inverse_kinematics as inv

#import L2_joint as joint
targetHeading=0
# initialize variables for control system
t0 = 0
t1 = 1
e00 = 0
e0 = 0
e1 = 0
dt = 0
de_dt = np.zeros(2) # initialize the de_dt
count = 0


while(1):
    currentHeading=heading.whereismyHead()
    print(currentHeading)
    thetaOffset=targetHeading-currentHeading
    print("offset: ", thetaOffset)
    myThetaDot = thetaOffset * 3.14/180 *4 # attempt centering in 0.5 seconds
    
    print(myThetaDot)
    myXDot= .25
    # BUILD SPEED TARGETS ARRAY
    A = np.array([ myXDot, myThetaDot])
    pdTargets = inv.convert(A) # convert from [xd, td] to [pdl, pdr]
    kin.getPdCurrent() # capture latest phi dots & update global var
    pdCurrents = kin.pdCurrents # assign the global variable value to a local var
    print(pdTargets)
    # UPDATES VARS FOR CONTROL SYSTEM
    t0 = t1  # assign t0
    t1 = time.time() # generate current time
    dt = t1 - t0 # calculate dt
    e00 = e0 # assign previous previous error
    e0 = e1  # assign previous error
    e1 = pdCurrents - pdTargets # calculate the latest error
    de_dt = (e1 - e0) / dt # calculate derivative of error
    #print(e1)
    # CALLS THE CONTROL SYSTEM TO ACTION
    sc.driveClosedLoop(pdTargets, pdCurrents, de_dt)  # call the control system
    # sc.driveOpenLoop(pdTargets)  # call the control system
    time.sleep(0.5) # very small delay.
