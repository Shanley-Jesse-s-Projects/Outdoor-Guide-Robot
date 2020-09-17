import googlemaps
from datetime import datetime
from shapely.geometry import Point, Polygon, LineString

gmaps = googlemaps.Client(key='AIzaSyD_8UslXeU3SmCAFmnHzqj4FgdlVAib_z8')

class findDir:
    def __init__(self, start, end):
        #convert Shapely point object into 1x2 array containing lat/long
        self.start_location = [start.x,start.y]
        self.end_location = [end.x,end.y]
        self.waypts = [] #array to store waypoints in Shapely Point form

        now = datetime.now()
        #get directions from Google in the form of a JSON script that is converted to a python list
        whereto = gmaps.directions(self.start_location, self.end_location, mode="walking", departure_time=now)
        #Read through the instruction list and pull out the lat/longs for each waypoints
        for i in whereto[0]['legs'][0]['steps']:
            l1 = []
            #step through list
            #print([i][0]['start_location'])
            l1.append([i][0]['start_location']['lat'])
            l1.append([i][0]['start_location']['lng'])
            #compile waypts into Point object array
            self.waypts.append(Point(l1[0],l1[1]))




