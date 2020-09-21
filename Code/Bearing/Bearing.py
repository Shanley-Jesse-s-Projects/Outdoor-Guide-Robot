#Author: Evan Maraist
#Email: emaraist1357@gmail.com
#Team BAST - ESET Capstone Project 2020
from findDir import findDir
from geo_Data import *
from shapely.geometry import Point, Polygon, LineString
import math
from Hologram.HologramCloud import Hologram

#Insure findDir, geo_Data, GPS, and magnetometer custom files are installed
#Insure Shapely library is installed

class Bearing(object):
    #'dest' is TAMU defined building name acronym
    #initialization method receives target building acronym and finds its closest entrance
    #init then calls API to get waypts between current location and destination
    def __init__(self, dest):
        self.getLoc()
        self.arrived = False
        #find closest entrance to target building
        lengths = [] #list to hold distances
        for i in Destinations[dest]:
            #create line beginning at current location and ending at a building entrance
            line = LineString([self.currentLoc,i])
            #append length of line to lengths list
            lengths.append(line.length)

        #set target point as the point within dest that is the shortest distance away
        self.target = Destinations[dest][lengths.index(min(lengths))]
        del lengths #delete to save some memory

        self.directions = findDir(self.currentLoc, self.target)
        self.currentWaypt = 0   #to track index number of current waypt

    #return direction (0-360degrees) to aim at to reach destination
    def getBearing(self):
        #Math to calculate target bearing given two sets of points on earths surface
        x = math.cos(math.radians(self.target.x)) * math.sin(math.radians(self.target.y) - math.radians(self.currentLoc.y))
        y = math.cos(math.radians(self.currentLoc.x)) * math.sin(math.radians(self.target.x)) - math.sin(math.radians(self.currentLoc.x)) * math.cos(math.radians(self.target.y) - math.radians(self.currentLoc.y))
        b_radians = math.atan2(x,y)
        b = b_radians * (180/math.pi)
        return b

    # find distance of the length of the line from point to line
    def pntToLineDist(self, point, line):
        x = point
        y = line
        # closest point on y to x
        pnt = y.interpolate(y.project(x))
        line = LineString([x, pnt])
        return line.length

    # find closest point  on a line to a point outside of it
    def closestPnt(self, point, line):
        return line.interpolate(line.project(point))

    # determine if a point (pnt) is in a NoGo zone
    def isNoGo(self, pnt):
        # Array of NoGo zones point is within
        y = []
        # Out of Bounds
        out_of_bounds = False
        for i in NoGo:
            if pnt.within(i):
                y.append(i)
                out_of_bounds = True
        if out_of_bounds:
            return True, y
        else:
            return False

    #get current GPS coordinates from Nova
    def getLoc(self):
        close = False
        # loop until a close enough value is found
        while (close == False):
            location = hologram.network.location
            # wait for a location to be received
            if location is None:
                while (location is None):
                    location = hologram.network.location
            # only return a value if its within max of 3m
            if location.uncertainty < 3:
                close = True
                self.currentLoc = [location.latitude, location.longitude]

    #check if current position is within 1.5m of destination
    def checkWaypt(self):
        #0.000135 degrees is equal to 1.5 meters
        x1 = self.directions.waypts[self.currentWaypt].x - 0.000135
        y1 = self.directions.waypts[self.currentWaypt].y - 0.000135
        x2 = self.directions.waypts[self.currentWaypt].x + 0.000135
        y2 = self.directions.waypts[self.currentWaypt].y + 0.000135
        #check if current location is within 1.5m
        if x1<=self.currentLoc[0]<=x2 and y1<=self.currentLoc[1]<=y2:
            #if it is, increment to next waypt
            self.currentWaypt = self.currentWaypt + 1
        #if current index exceeds length of direction waypts, you have arrived
        if self.currentWaypt > len(self.directions.waypts):
            self.arrived = True

    #cleans up created objects to prevent memory leak
    def cleanUp(self):
        del self.directions

#if __name__ == "__main__":
