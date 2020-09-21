# movement.py          In Progress

# Code purpose: Closed loop driving based on heading deviances.
# this code reads values from the magnetomer and calls for the direction
# the robot needs to go. The difference between those two is passed in as a
# thetadot into inverse kinematics. A speed profile is built off of these. Obstacle avoidance is tied in next

# Import external libraries
import numpy as np
import time

# Import internal programs
import L2_heading as heading
import L2_kinematics as kin
import L2_speed_control as sc
import L2_inverse_kinematics as inv
from Bearing import Bearing
import ObstacleAvoidance as oba

class movement:
    #initializes movement object with 'dest' as goal
    def __init__(self,dest):
        self.dest = dest
        self.current = Bearing(self.dest)
        #initialize variables for control system
        self.t0 = 0
        self.t1 = 1
        self.e00 = 0
        self.e0 = 0
        self.e1 = 0
        self.dt = 0
        self.de_dt = np.zeros(2)  # initialize the de_dt
        self.count = 0

    #updates current location, checks if waypt has been reached, updates target bearing
    def updateGeo(self):
        self.current.getLoc()
        self.current.checkWaypt()
        if self.current.arrived == True:
            self.stop()
            return
        self.targetBearing = self.current.getBearing()

    def stop(self):  # stops motors
        # needs condition:
        speeds = [0, 0]
        sc.driveOpenLoop(speeds)


    def launch(self):  # needs to run in while loop every .005 seconds
        # could insert an obstacle avoidance function call here
        oba.callObstacle()  # pulls in open loop obstacle avoidance code
        currentHeading = heading.whereismyHead()  # gets the direction the robot is facing
        print(currentHeading)
        thetaOffset = self.targetBearing - currentHeading  # calculates theta offset (the difference between the heading and the direction of intention)
        print("offset: ", thetaOffset)
        myThetaDot = thetaOffset * 3.14 / 180 * 4  # attempt centering in 0.5 seconds

        print(myThetaDot)
        myXDot = 0.5  # travel half a meter per second in forward speed
        # BUILD SPEED TARGETS ARRAY
        A = np.array([myXDot, myThetaDot])  # combines xdot and myThetaDot into one array to be passed into inverse kin
        pdTargets = inv.convert(A)  # convert from [xd, td] to [pdl, pdr]
        kin.getPdCurrent()  # capture latest phi dots & update global var
        pdCurrents = kin.pdCurrents  # assign the global variable value to a local var
        print(pdTargets)
        # UPDATES VARS FOR CONTROL SYSTEM
        self.t0 = self.t1  # assign t0
        self.t1 = time.time()  # generate current time
        self.dt = self.t1 - self.t0  # calculate dt
        self.e00 = self.e0  # assign previous previous error
        self.e0 = self.e1  # assign previous error
        self.e1 = pdCurrents - pdTargets  # calculate the latest error
        self.de_dt = (self.e1 - self.e0) / self.dt  # calculate derivative of error

        # CALLS THE CONTROL SYSTEM TO ACTION
        sc.driveClosedLoop(pdTargets, pdCurrents, self.de_dt)  # call the control system
        time.sleep(0.005)  # very small delay.

    def cleanUp(self):
        self.current.cleanUp()
        del self.current

if __name__ == "__main__":

    while (1):
        launch()
