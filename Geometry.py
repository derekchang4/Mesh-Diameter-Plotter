# This file contains the representation of a mesh from a .STL file
# and contains functions related to analyzing and plotting it
import VectorReader as vr
import VectorAnalyzer as va
import VectorPlotter as vp
import Constants as const
import numpy as np
import matplotlib.pyplot as plt

## Defaults! To edit, do it in the Constants.py file
## Uncomment these if Constants.py isn't working for some reason
# THRESHOLD = .005 # Threshold for change in rotation in radians
# ITERATIONNUM = 3 # The nth iteration to display

THRESHOLD = const.THRESHOLD
ITERATIONNUM = const.ITERATIONNUM

## This class represents a mesh geometry file and will include 
# a set of vectors and anything else that might need to be stored.
class Mesh:
    def __init__(self, filename):
        # Unchanging
        self.filename     = filename
        self.VECTORMAP    = None
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
        self.change         = None

        # Post straightened data
        self.slices         = None  # A vector list with points separated by slices

    def readVectors(self):
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



### Plotting
    def dprint(self, string, debug):
        if debug:
            print(string)

    def plotCentroids(self, ax):
        self.findCentroids()
        vp.plotCentroids(self.centroids, ax)

    def plotMesh(self, ax, resolution = 1):
        vp.plotMesh(self.vectorList, ax, resolution)

    def plotCenterLine(self, ax, min = -10, max= 10, debug = False):
        min = self.vectorList[-1][self.axisIdx]
        max = self.vectorList[0][self.axisIdx]
        self.dprint(f"Min: {self.vectorList[-1]}, Max: {self.vectorList[0]}", debug)
        vp.plotCenterLine(self.centroids, ax, min, max, self.axisIdx)

    def plot(self, resolution = 1, debug = False):
        ax1 = plt.axes(projection = '3d')
        self.plotCentroids(ax1)
        self.dprint(f"\nPlotting", debug)
        self.dprint(f"datamean: {self.datamean}", debug)
        self.plotCenterLine(ax1)
        self.plotMesh(ax1, resolution)
        self.plotTargetAxis(ax1, self.axisIdx)
        plt.show()
    
    def plotTargetAxis(self, ax, axisIdx):
        axes = [[0, 0], [0, 0], [0, 0]]
        axes[axisIdx][1] = self.datamean[axisIdx]
        vp.plotAxes(ax, self.datamean[axisIdx] / 4)
        ax.plot3D(axes[0], axes[1], axes[2])

    def plotDiameter(self):
        ax = plt.axes()
        self.findCentroids()
        avgDiameter, centers = va.calculateDiameter(self.axisIdx, self.vectorList, self.dirVector, self.datamean)
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

        # Showing centers in relation
        x = []
        y = []
        z = []
        for v in centers:
            x.append(v[0])
            y.append(v[1])
            z.append(v[2])
        ax1 = plt.axes(projection= '3d')
        self.plotMesh(ax1, .001)
        ax1.scatter(x, y, z)
        print(f"Centers: {len(centers)}")
        plt.title("Centers")
        plt.show()

    def updateIterationShown(self, iteration):
        self.ITERATIONNUM = iteration
