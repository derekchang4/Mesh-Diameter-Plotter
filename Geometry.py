# This file contains the representation of a mesh from a .STL file
# and contains functions related to analyzing and plotting it
import VectorReader as vr
import VectorAnalyzer as va
import VectorPlotter as vp
import Constants as c
import numpy as np
import matplotlib.pyplot as plt

## Defaults! To edit, do it in the Constants.py file
## Uncomment these if Constants.py isn't working for some reason
# THRESHOLD = .005 # Threshold for change in rotation in radians
# ITERATIONNUM = 3 # The nth iteration to display

THRESHOLD = c.THRESHOLD
ITERATIONNUM = c.ITERATIONNUM

## This class represents a mesh geometry file and will include 
# a set of vectors and anything else that might need to be stored.
class Mesh:
    def __init__(self, filename):
        # Unchanging
        self.filename     = filename
        self.VECTORMAP    = None
        self.VECTORCOUNT  = None
        self.OGVECTORLIST = None

        # Updates as the object rotates
        self.axisIdx      = None
        self.greatestSpan = None  # tracks the axis of greatest span and the units it spans
        self.vectorList   = None  # required for sorting and ordering; current position
        self.centroids    = None  # represents the centroids of the slices of the channel
        self.datamean     = None  # represents the center of the channel
        self.dirVector    = None  # represents the slope of the centerline
        self.totalRotation     = [0, 0, 0]  # tracks the rotation applied to the original mesh (in radians)
        self.curRotation       = [0, 0, 0]  # the amount the object was rotated by the current iteration

    def readVectors(self):
        self.VECTORMAP
        if (".stl" in self.filename.lower()):
            print("[STL FILE]")
            self.VECTORMAP = vr.readVectors(self.filename)
        elif (".wrl" in self.filename.lower()):
            print("[WRL FILE]")
            self.VECTORMAP = vr.readVectorsWRL(self.filename)
        else:
            print("UNSUPPORTED FILE TYPE")
            quit()
        self.VECTORCOUNT = len(self.VECTORMAP)
        # Saving all lists as numpy arrays since matrix numpy operations will
        # need to be done on them later
        self.OGVECTORLIST = np.array(list(self.VECTORMAP.keys()))
        self.vectorList = np.copy(self.OGVECTORLIST)
        #print(self.VECTORMAP)
        #print(self.vectorList)
        print(self.VECTORCOUNT, "Vertices")

    def getGreatestSpan(self):
        # Sets axisIdx as well
        self.greatestSpan = va.greatestSpan(self)
    
    def sortPoints(self):
        self.vectorList = va.sortPoints(self.axisIdx, self.vectorList)

    def findCentroids(self):
        self.centroids, self.vectorList = va.findCentroids(self)
        va.findCenterline(self)

    def fitGeometry(self):
        self.findCentroids()
        va.fitGeometry(self)

    # Straightens the channel iteratively until threshold in Geometry.py
    # Then calculates the diameters across the axis
    def straighten(self):
        ax1 = plt.axes(projection = '3d')
        plt.title("Original")
        vp.plotMesh(self.vectorList, ax1)
        plt.show()
        iteration = 1
        self.fitGeometry()
        print(f"\nIteration: {iteration}    threshold: {THRESHOLD}")
        rotationSum = (self.curRotation[0] ** 2) + (self.curRotation[1] ** 2) + (self.curRotation[2] ** 2)
        print(f"Rotation: {self.curRotation} =  {rotationSum}")
        while rotationSum > THRESHOLD:
            self.fitGeometry()
            rotationSum = (self.curRotation[0] ** 2) + (self.curRotation[1] ** 2) + (self.curRotation[2] ** 2)
            iteration += 1
            print(f"Iteration: {iteration}")
            print(f"Rotation: {self.curRotation} =  {rotationSum}")
            print(f"Total rotation = {self.totalRotation}")
            if iteration % ITERATIONNUM == 0:
                plt.title(f"Iteration {iteration}")
                self.plot()
        print(f"\nThreshold reached ({THRESHOLD})")
        print(f"  Last rotation: {self.curRotation} = {rotationSum}")
        print(f"  Total rotation: {self.totalRotation}")
        plt.title("Straightened")
        self.plot()



### Plotting
    def plotCentroids(self, ax):
        self.findCentroids()
        vp.plotCentroids(self.centroids, ax)

    def plotMesh(self, ax):
        vp.plotMesh(self.vectorList, ax)

    def plotCenterLine(self, ax, min = -10, max= 10):
        self.sortPoints()
        min = self.vectorList[-1][self.axisIdx]
        max = self.vectorList[0][self.axisIdx]
        vp.plotCenterLine(self.centroids, ax, min, max)

    def plot(self):
        ax1 = plt.axes(projection = '3d')
        self.plotCentroids(ax1)
        self.plotCenterLine(ax1)
        self.plotMesh(ax1)
        plt.show()

    def plotDiameter(self):
        ax = plt.axes()
        self.sortPoints()
        avgDiameter = va.calculateDiameter(self.axisIdx, self.vectorList, self.dirVector, self.datamean)
        vp.plotDiameter(ax, avgDiameter)
        axis = None
        match self.axisIdx:
            case 0:
                axis = "x"
            case 1:
                axis = "y"
            case 2:
                axis = "z"
            case _:
                print("Invalid axis")
                quit()
        plt.xlabel(f"{axis} axis")
        plt.ylabel("Diameter")
        ax.set_ylim([0, None])
        plt.title("Diameter across the longest axis")
        plt.show()

def updateIterationShown(iteration):
    ITERATIONNUM = iteration
