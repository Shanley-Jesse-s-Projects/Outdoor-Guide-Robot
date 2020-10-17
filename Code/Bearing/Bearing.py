#Author: Evan Maraist
#Email: emaraist1357@gmail.com
#Team BAST - ESET Capstone Project 2020
import math
from shapely.geometry import Point, LineString
from geo_Data import NoGo, Destinations
from datetime import datetime
import googlemaps

gmaps = googlemaps.Client(key='enter key here')

# Insure findDir, geo_Data, GPS, and magnetometer custom files are installed
# Insure Shapely library is installed

class Bearing(object):
    #'dest' is TAMU defined building name acronym
    #initialization method receives target building acronym and finds its closest entrance
    #init then calls API to get waypts between current location and destination
    def __init__(self, dest):
        #self.getLoc()
        #Current location in the form of a Shapely point
        self.currentLoc = Point(30.617073,-96.341687)  # entrance to the PIC
        self.arrived = False
        #find closest entrance to target building
        lengths = [] #list to hold distances
        for i in Destinations[dest]:
            #create line beginning at current location and ending at a building entrance
            line = LineString([self.currentLoc,i])
            #append length of line to lengths list
            lengths.append(line.length)
            #print(line.length)

        #set target point as the point within dest that is the shortest distance away
        #print(lengths.index(min(lengths)))
        self.target = Destinations[dest][lengths.index(min(lengths))]
        self.getDir(self.currentLoc, self.target)
        self.waypts.append(self.target) #Make sure our final point is in waypts list, Gmaps leaves it out sometimes
        self.currentWaypt_iterator = 0   #to track index number of current waypt
        self.currentWaypt = self.waypts[self.currentWaypt_iterator]

        print("From Google:")
        for i in self.waypts:
            print(i.x, i.y)
        #check through received waypts and insure they're not in NoGo zones
        #if they are, reroute them to nearby okay zone
        iterator = 0 #to track which point we're on
        for pt in self.waypts: #check every point received from GoogleMaps
            #print("Checking: ", pt)
            for loc in NoGo.keys(): #Read throuh NoGo zones
                #print("Testing: ", loc)
                if pt.within(NoGo[loc]['Polygon']) == True: #if point is within NoGo zone
                    #print("Point was out of bounds.")
                    #map it to the nearest sidewalk
                    self.waypts[iterator] = self.closestPnt(self.waypts[iterator], NoGo[loc]['Reroute2'])
            iterator = iterator + 1
        print("\nUpdated:")
        for i in self.waypts:
            print(i.x, i.y)
        print("\n")

    #get directions from start to end using Gmaps API, save them in self.waypts
    def getDir(self, start, end):
        # convert Shapely point object into 1x2 array containing lat/long
        self.start_location = [start.x,start.y]
        self.end_location = [end.x,end.y]
        self.waypts = [] # array to store waypoints in Shapely Point form

        now = datetime.now()
        # get directions from Google in the form of a JSON script that is converted to a python list
        whereto = gmaps.directions(self.start_location, self.end_location, mode="walking", departure_time=now)
        # Read through the instruction list and pull out the lat/longs for each waypoints
        for i in whereto[0]['legs'][0]['steps']:
            l1 = []
            # step through list
            # print([i][0]['start_location'])
            l1.append([i][0]['start_location']['lat'])
            l1.append([i][0]['start_location']['lng'])
            # compile waypts into Point object array
            self.waypts.append(Point(l1[0],l1[1]))

    # return direction (0-360degrees) to aim at to reach destination
    def getBearing(self):
        # Math to calculate target bearing given two sets of points on earths surface
        A = math.radians(self.currentLoc.x)
        B = math.radians(self.currentLoc.y)
        C = math.radians(self.currentWaypt.x)
        D = math.radians(self.currentWaypt.y)
        # print(A,B,C,D)
        x = math.cos(C) * math.sin(D - B)
        y = math.cos(A) * math.sin(C) - math.sin(A) * math.cos(C) * math.cos(D-B)
        b = math.degrees(math.atan2(x,y))
        bearing = (b + 360) % 360
        return bearing

    #  find distance of the length of the line from point to line
    def pntToLineDist(self, point, line):
        x = point
        y = line
        #  closest point on y to x
        pnt = y.interpolate(y.project(x))
        line = LineString([x, pnt])
        return line.length

    #  find closest point  on a line to a point outside of it
    def closestPnt(self, point, line):
        return line.interpolate(line.project(point))

    #  determine if a point (pnt) is in a NoGo zone
    def isNoGo(self, pnt):
        #  Array of NoGo zones point is within
        y = []
        #  Out of Bounds
        out_of_bounds = False
        for i in NoGo:
            if pnt.within(i):
                y.append(i)
                out_of_bounds = True
        if out_of_bounds:
            return True
        else:
            return False

    # this function makes the next waypt in the list our current waypt
    def nextWaypt(self):
        if self.currentWaypt_iterator == len(self.waypts) - 1:
            print("You have arrived.")
            return
        self.currentWaypt_iterator = self.currentWaypt_iterator + 1
        self.currentWaypt = self.waypts[self.currentWaypt_iterator]

    # get current GPS coordinates from Nova
    # def getLoc(self):
    #     close = False
    #     #  loop until a close enough value is found
    #     while (close == False):
    #         location = hologram.network.location
    #         #  wait for a location to be received
    #         if location is None:
    #             while (location is None):
    #                 location = hologram.network.location
    #         #  only return a value if its within max of 3m
    #         if location.uncertainty < 3:
    #             close = True
    #            self.currentLoc = [location.latitude, location.longitude]

    # check if current position is within 1.5m of destination
    def checkWaypt(self):
        # 0.000090 degrees is equal to 1m
        x1 = self.waypts[self.currentWaypt].x - 0.000090
        y1 = self.waypts[self.currentWaypt].y - 0.000090
        x2 = self.waypts[self.currentWaypt].x + 0.000090
        y2 = self.waypts[self.currentWaypt].y + 0.000090
        # check if current location is within 1m
        if x1<=self.currentLoc[0]<=x2 and y1<=self.currentLoc[1]<=y2:
            # if it is, increment to next waypt
            self.currentWaypt = self.currentWaypt + 1
        # if current index exceeds length of direction waypts, you have arrived
        if self.currentWaypt > len(self.waypts):
            self.arrived = True

# Bearing test functionality
if __name__ == "__main__":
    You_Are_Here = Point(30.617073,-96.341687)  # entrance to the PIC
    # User wants to go to the MSC
    example = Bearing("ZEEC", You_Are_Here)
    for i in range(0,len(example.waypts)):
        # get bearing to next waypoint
        print("Current location: ", example.currentLoc)
        print("Target: ", example.currentWaypt)
        print("Bearing: ", example.getBearing(),"\n")
        # make current waypoint our new location
        example.currentLoc = example.waypts[i]
        # manually increment waypts
        example.nextWaypt()
