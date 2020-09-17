#Author: Evan Maraist
#Email: emaraist1357@gmail.com
#Team BAST - ESET Capstone Project 2020
import findDir
from geo_Data import *
from shapely.geometry import Point, Polygon, LineString
import math
#import GPS
#import magnetometer

#Insure findDir, geo_Data, GPS, and magnetometer custom files are installed
#Insure Shapely library is installed

class Bearing:
    #class receives destination building code
    def __init__(self, dest):
        #self.currentLoc = shapely point of gps

        #find closest entrance to target building
        lengths = [] #list to hold distances
        for i in Destinations[dest]:
            #create line beginning at current location and ending at a building entrance
            line = LineString([self.currentLoc,i])
            #append length of line to lengths list
            lengths.append(line.length)

        #set target point as the point within dest that is the shortest distance away
        self.target = Destinations[dest][lengths.index(min(lengths))]
        del lengths

        directions = findDir(self.currentLoc, self.target)

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

    # find closest point on a line to a point outside of it
    def closestPnt(self, point, line):
        return line.interpolate(line.project(point))

    # determine if a point is in a NoGo zone
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



