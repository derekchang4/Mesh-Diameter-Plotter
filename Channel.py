# This file contains the representation of a mesh from a .STL file
# and contains functions related to analyzing and plotting it
import VectorReader as vr
import VectorAnalyzer as va
import VectorPlotter as vp
import Constants as const
import numpy as np
import matplotlib.pyplot as plt
import Straightenable as strtn

## Defaults! To edit, do it in the Constants.py file
## Uncomment these if Constants.py isn't working for some reason
# THRESHOLD = .005 # Threshold for change in rotation in radians
# ITERATIONNUM = 3 # The nth iteration to display

THRESHOLD = const.THRESHOLD
ITERATIONNUM = const.ITERATIONNUM

## This class represents a mesh geometry file and will include 
# a set of vectors and anything else that might need to be stored.
class Channel(strtn.Straightenable):
    def __init__(self, filename):
        super().__init__()
        # Unchanging
        self.filename     = filename
        self.VECTORMAP    = None

        ## MOVED TO STRAIGHTENABLE ##
        # self.VECTORCOUNT  = None
        # self.OGVECTORLIST = None
        # self.ITERATIONNUM = ITERATIONNUM

        # # Updates as the object rotates
        # self.axisIdx        = None
        # self.greatestSpan   = None  # tracks the axis of greatest span and the units it spans
        # self.vectorList     = None  # required for sorting and ordering; current position
        # self.centroids      = None  # represents the centroids of the slices of the channel
        # self.datamean       = None  # represents the center of the channel
        # self.dirVector      = None  # represents the slope of the centerline
        # self.totalRotation     = [0, 0, 0]  # tracks the rotation applied to the original mesh (in radians)
        # self.curRotation       = [0, 0, 0]  # the amount the object was rotated by the current iteration
        # self.sorted         = False # tracks if the vectorList has been sorted
        # self.centroidsFound = False # tracks if the centroids have been computed
        # self.change         = None  # the amount of change the mesh went through in the last iteration
        ## MOVED TO STRAIGHTENABLE ##

        # Post straightened data
        self.slices         = None  # A vector list with points separated by slices
        self.slicesCurrent  = False # Flag for if the slices are up to date

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

    # Straightens each slice in the channel until threshold
    def straightenSlices(self):
        print("\nStraightening slices")
        sliceNum = 1
        for s in self.slices:
            iteration = 1
            print(f"Slice {sliceNum}")
            sliceNum += 1
            print(f"\nIteration: {iteration}    threshold: {THRESHOLD}")
            s.fitGeometry()
            rotationSum = (s.curRotation[0] ** 2) + (s.curRotation[1] ** 2) + (s.curRotation[2] ** 2)
            print(f"Rotation: {s.curRotation} =  {rotationSum}")
            while not s.atThreshold():
                iteration += 1
                print(f"\nIteration: {iteration}")
                s.fitGeometry()
                rotationSum = (s.curRotation[0] ** 2) + (s.curRotation[1] ** 2) + (s.curRotation[2] ** 2)
                print(f"Rotation: {s.curRotation} =  {rotationSum}")
                print(f"Total rotation = {s.totalRotation}")
            print(f"\nThreshold reached ({THRESHOLD})")
            print(f"  Last rotation: {s.curRotation} = {rotationSum}")
            print(f"  Total rotation: {s.totalRotation}")

    # Gets the diameter dictionary
    def getDiameter(self, chunkSize):
        return va.condenseDiameterByChunk(self.axisIdx, chunkSize, self)
    
    # Creates the slices and computes their
    def computeMiniSlices(self):
        self.sortPoints()
        self.getGreatestSpan()
        self.slices = va.sliceMiniSlices(self.vectorList, self.axisIdx, self.greatestSpan[1])

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
        self.showCenters(centers)

    def showCenters(self, centers):
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

    def plotChunkDiameter(self, specifiedWidth):
        ax = plt.axes()
        self.findCentroids()
        avgDiameter, centers = va.condenseDiameterByChunk(self.axisIdx, specifiedWidth, self)
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
        self.showCenters(centers)

    # Doesn't work currently
    def updateIterationShown(self, iteration):
        self.ITERATIONNUM = iteration
