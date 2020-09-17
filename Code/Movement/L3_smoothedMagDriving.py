# SmoothedMagDriving            In Progress

# Code purpose: Closed loop driving based on heading deviances.
#this code reads values from the magnetomer and calls for the direction
#the robot needs to go. The difference between those two is passed in as a
#thetadot into inverse kinematics. 

# Import external libraries
import numpy as np
import time

# Import internal programs
import L2_heading as heading
import L2_kinematics as kin
import L2_speed_control as sc
import L2_inverse_kinematics as inv


targetHeading=0    #this will be a function call to get a global variable

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
    
    #could insert an obstacle avoidance function call here
    
    currentHeading=heading.whereismyHead()   #gets the direction the robot is facing
    print(currentHeading)
    thetaOffset=targetHeading-currentHeading   #calculates theta offset (the difference between the heading and the direction of intention)
    print("offset: ", thetaOffset)
    myThetaDot = thetaOffset * 3.14/180 *4 # attempt centering in 0.5 seconds
    
    print(myThetaDot)
    myXDot= 0.5    #travel half a meter per second in forward speed
    # BUILD SPEED TARGETS ARRAY
    A = np.array([ myXDot, myThetaDot])  #combines xdot and myThetaDot into one array to be passed into inverse kin
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
    
    # CALLS THE CONTROL SYSTEM TO ACTION
    sc.driveClosedLoop(pdTargets, pdCurrents, de_dt)  # call the control system
    time.sleep(0.005) # very small delay.
