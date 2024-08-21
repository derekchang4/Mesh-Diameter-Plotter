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
# Extends from Straightenable, so has all the methods and fields
# Straightenable has
class Channel(strtn.Straightenable):
    def __init__(self, filename):
        super().__init__()
        # Unchanging
        self.filename     = filename
        self.VECTORMAP    = None

        # Post straightened data
        self.slices         = None  # A vector list with points separated by slices
        self.slicesCurrent  = False # Flag for if the slices are up to date

    def readVectors(self):
        if (".stl" in self.filename.lower()):
            print("[STL FILE]")
            self.VECTORMAP = vr.readVectorsSTL(self.filename)
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
    def straightenSlices(self, resolution = 0, plot = False):
        print("\nStraightening slices")
        sliceNum = 0
        for s in self.slices:
            # iteration = 1
            print(f"Slice {sliceNum}")
            sliceNum += 1
            self.straighten(resolution, plot)
            # print(f"\nIteration: {iteration}    threshold: {THRESHOLD}")
            # s.fitGeometry()
            # rotationSum = (s.curRotation[0] ** 2) + (s.curRotation[1] ** 2) + (s.curRotation[2] ** 2)
            # print(f"Rotation: {s.curRotation} =  {rotationSum}")
            # while not s.atThreshold():
            #     iteration += 1
            #     print(f"\nIteration: {iteration}")
            #     s.fitGeometry()
            #     rotationSum = (s.curRotation[0] ** 2) + (s.curRotation[1] ** 2) + (s.curRotation[2] ** 2)
            #     print(f"Rotation: {s.curRotation} =  {rotationSum}")
            #     print(f"Total rotation = {s.totalRotation}")
            # print(f"\nThreshold reached ({THRESHOLD})")
            # print(f"  Last rotation: {s.curRotation} = {rotationSum}")
            # print(f"  Total rotation: {s.totalRotation}")
    
    # Creates the slices and computes their
    def computeMiniSlices(self):
        self.sortPoints()
        self.getGreatestSpan()
        self.slices = va.sliceMiniSlices(self.vectorList, self.axisIdx, self.greatestSpan[1])

    def plotMeshBySlice(self, ax, resolution):
        for s in self.slices:
            s.plotMesh(ax, resolution)
            s.plotCenterLine(ax)
        
    def showSlices(self, resolution = .01):
        if self.slices == None:
            print("Slices not computed yet!")
            return
        ax = plt.axes(projection= '3d')
        self.plotMeshBySlice(ax, resolution)
        self.plotTargetAxis(ax, self.axisIdx)
        plt.show()
        # Could override each method in straightenable to check
        # for slicing

    # Doesn't work currently
    def updateIterationShown(self, iteration):
        self.ITERATIONNUM = iteration

    def diameterByCentroids(self):
        connectingLines = []
        for i in range(len((self.centroids)) - 1):
            connectingLines.append(self.centroids[i] - self.centroids[i + 1])
        