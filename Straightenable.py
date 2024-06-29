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
        self.sorted         = False # tracks if the vectorList has been sorted
        self.centroidsFound = False # tracks if the centroids have been computed
        self.change         = None  # the amount of change the mesh went through in the last iteration

    def getGreatestSpan(self):
        # Sets axisIdx as well
        self.greatestSpan = va.greatestSpan(self)
    
    def sortPoints(self):
        # Don't sort if already sorted
        if (self.sorted):
            return
        self.vectorList = va.sortPoints(self.axisIdx, self.vectorList)
        self.sorted = True

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

    # Straightens the channel iteratively until threshold in Geometry.py
    # Then calculates the diameters across the axis
    def straighten(self, resolution = 1):
        print(f"Resolution {resolution}")
        ax1 = plt.axes(projection = '3d')
        plt.title("Original")
        vp.plotMesh(self.vectorList, ax1, resolution)
        plt.show()
        iteration = 1
        print(f"\nIteration: {iteration}    threshold: {THRESHOLD}")
        self.fitGeometry()
        if iteration % self.ITERATIONNUM == 0:
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
            if iteration % self.ITERATIONNUM == 0:
                plt.title(f"Iteration {iteration}")
                self.plot(resolution)
        print(f"\nThreshold reached ({THRESHOLD})")
        print(f"  Last rotation: {self.curRotation} = {rotationSum}")
        print(f"  Total rotation: {self.totalRotation}")
        plt.title("Straightened")
        self.plot(resolution)

    # A straighten function that doesn't display
    # Straightens the channel iteratively until threshold in Geometry.py
    # Then calculates the diameters across the axis
    def straightenSlices(self):
        print("\nSlice straightening")
        for s in self.slices:
            iteration = 1
            print(f"\nIteration: {iteration}    threshold: {THRESHOLD}")
            s.fitGeometry()
            rotationSum = (s.curRotation[0] ** 2) + (s.curRotation[1] ** 2) + (s.curRotation[2] ** 2)
            print(f"Rotation: {self.curRotation} =  {rotationSum}")
            while not self.atThreshold():
                iteration += 1
                print(f"\nIteration: {iteration}")
                self.fitGeometry()
                rotationSum = (self.curRotation[0] ** 2) + (self.curRotation[1] ** 2) + (self.curRotation[2] ** 2)
                print(f"Rotation: {self.curRotation} =  {rotationSum}")
                print(f"Total rotation = {self.totalRotation}")
            print(f"\nThreshold reached ({THRESHOLD})")
            print(f"  Last rotation: {self.curRotation} = {rotationSum}")
            print(f"  Total rotation: {self.totalRotation}")
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
        
    def rotate(self, theta, rotationAxis, radians = True):
        if not radians:
            theta = theta * np.pi / 180
        va.rotate(self.vectorList, theta, rotationAxis, True)
