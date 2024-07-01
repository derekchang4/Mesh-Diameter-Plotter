# This file contains the representation of a mesh from a .STL file
# and contains functions related to analyzing and plotting it
import VectorReader as vr
import VectorAnalyzer as va
import VectorPlotter as vp
import Constants as const
import numpy as np
import matplotlib.pyplot as plt

THRESHOLD = const.THRESHOLD
ITERATIONNUM = const.ITERATIONNUM

class Straightenable:
    def __init__(self):
        # Unchanging
        self.VECTORCOUNT  = None
        self.OGVECTORLIST = None
        self.ITERATIONNUM = ITERATIONNUM

        # Updates as the object rotates
        self.axisIdx        = None
        self.greatestSpan   = None  # tracks the axis of greatest span and the units it spans
        self.vectorList     = None  # required for sorting and ordering; current position
        self.centroids      = None  # represents the centroids of the slices of the channel
        self.datamean       = None  # represents the center of the channel
        self.dirVector      = None  # represents the slope of the centerline
        self.totalRotation     = [0, 0, 0]  # tracks the rotation applied to the original mesh (in radians)
        self.curRotation       = [0, 0, 0]  # the amount the object was rotated by the current iteration
        self.change         = None  # the amount of change the mesh went through in the last iteration

        # Flags
        self.sorted         = False # tracks if the vectorList has been sorted
        self.centroidsFound = False # tracks if the centroids have been computed
        self.greatestSpanUpdated    = False # tracks if the greatest span has been kept updated

    def getGreatestSpan(self):
        if self.greatestSpanUpdated == False:
            # Sets axisIdx as well
            self.greatestSpan = va.greatestSpan(self)
            self.greatestSpanUpdated = True
    
    def sortPoints(self):
        # Don't sort if already sorted
        if (self.sorted):
            return
        self.vectorList = va.sortPoints(self.axisIdx, self.vectorList)
        self.sorted = True
        print("Sorted")

    def findCentroids(self):
        if self.centroidsFound == True:
            return
        self.centroids, self.vectorList = va.findCentroids(self)
        va.findCenterline(self)
        self.sorted = True  # Finding the centroids sorts the points
        self.centroidsFound = True

    def fitGeometry(self):
        self.findCentroids()
        va.fitGeometry(self)
        self.sorted = False # Rotation mixes points
        self.centroidsFound = False # centroids must be recomputed 

    # Straightens the channel iteratively until threshold in Straightenable.py
    # Then calculates the diameters across the axis
    def straighten(self, resolution = .01, plot = True):
        if plot:
            print(f"Resolution {resolution}")
            ax1 = plt.axes(projection = '3d')
            plt.title("Original")
            vp.plotMesh(self.vectorList, ax1, resolution)
            plt.show()
        iteration = 1
        print(f"\nIteration: {iteration}    threshold: {THRESHOLD}")
        self.fitGeometry()
        if plot == True and iteration % self.ITERATIONNUM == 0:
                plt.title(f"Iteration {iteration}")
                self.plot(resolution)
        rotationSum = (self.curRotation[0] ** 2) + (self.curRotation[1] ** 2) + (self.curRotation[2] ** 2)
        print(f"Rotation: {self.curRotation} =  {rotationSum}")
        while not self.atThreshold():
            iteration += 1
            print(f"\nIteration: {iteration}")
            self.fitGeometry()
            rotationSum = (self.curRotation[0] ** 2) + (self.curRotation[1] ** 2) + (self.curRotation[2] ** 2)
            print(f"Rotation: {self.curRotation} =  {rotationSum}")
            print(f"Total rotation = {self.totalRotation}")
            if plot == True and iteration % self.ITERATIONNUM == 0:
                plt.title(f"Iteration {iteration}")
                self.plot(resolution)
        print(f"\nThreshold reached ({THRESHOLD})")
        print(f"  Last rotation (radians): {self.curRotation} = {rotationSum}")
        print(f"  Total rotation (radians): {self.totalRotation}")
        if plot:
            plt.title("Straightened")
            self.plot(resolution)

    
    # Make a diameter function for different slices

    def atThreshold(self):
        pt = self.centroids[0] # Take a point from somewhere
        radius = np.linalg.norm(pt - self.datamean)  # Get the dist
        c = 0
        for axisIdx, radians in enumerate(pt):
            c += (radius * self.curRotation[axisIdx]) ** 2
        c = np.sqrt(c)
        self.change = c
        print(f"Threshold: {c} < {THRESHOLD} = {c < THRESHOLD}")

        if c < THRESHOLD:
            return True
        else:
            return False
        
    def rotate(self, rotation, radians = True):
        if not radians:
            for axis, theta in rotation:
                rotation[axis] = theta * np.pi / 180
        for axis, rads in enumerate(rotation):
            va.rotate(self.vectorList, rads, axis, True)
        self.sorted = False
        self.centroidsFound = False

    ## Files
    # UNFINISHED
    def save(self, filename):
        file = open(filename, "w")
        # Info
        file.write(f"VECTORCOUNT,{self.VECTORCOUNT}")
        file.write(f"axisIdx,{self.axisIdx}")
        file.write(f"greatestSpan,{self.greatestSpan[0]},{self.greatestSpan[1]}")
        file.write(f"change,{self.change}")
        # Flags
        file.write(f"sorted,{self.sorted}")
        file.write(f"centroidsFound,{self.centroidsFound}")
        file.write(f"greatestSpanUpdated,{self.greatestSpanUpdated}")
        file.write(f"\n")

        # Any point lists
        file.write(f"OGVECTORLIST")
        for v in self.OGVECTORLIST:
            file.write(f"{v[0]},{v[1]},{v[2]}")
        file.write(f"\n")
        file.write("vectorList")
        for v in self.vectorList:
            file.write(f"{v[0]},{v[1]},{v[2]}")
