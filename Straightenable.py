'''
# This file contains the representation of a mesh from a .STL file
# and contains functions related to analyzing and plotting it
'''
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
        self.SLICES = const.SLICES ## Default NumSlices

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

        # Data
        self.diameter : dict = None
        self.condensedDiameter : dict = None    # stores the condensed version of diameter
        self.centers : list  = None

        # Flags
        self.isSorted         = False # tracks if the vectorList has been sorted
        self.centroidsUpdated = False # tracks if the centroids have been computed
        self.greatestSpanUpdated    = False # tracks if the greatest span has been kept updated
        self.diameterUpdated     = False # tracks if avgDiameter is up to date
        self.datameanUpdated  = False

        # Control flags
        self.isAutoTargetAxis: bool     = None
        self.useAxisDiameterCenterline: bool    = None

        # Methods
        self.diameterMethod = va.calculateDiameterByValue

        # Constants
        self.DEFAULTRESOLUTION = .01

    def getGreatestSpan(self):
        if self.greatestSpanUpdated == False:
            # Sets axisIdx as well
            self.greatestSpan = va.greatestSpan(self)
            self.greatestSpanUpdated = True
            return self.greatestSpan
        return self.greatestSpan

    def autoSetTargetAxis(self):
        '''Automatically sets the target axis based on the 
        axis with the greatest span'''
        self.axisIdx = self.getGreatestSpan()[0]

    # Set the target axis
    # If none is given, axis auto targets to the one
    # with the greatest span
    def setTargetAxis(self, axisIdx: int = None):
        '''Sets the target axis to the index of the given axis. If -1 is inputted,
        sets the mesh to auto target the axis with the greatest span'''
        if axisIdx == -1:
            self.isAutoTargetAxis = True
            print("Mesh axis will autofind")
            return
        self.isAutoTargetAxis = False
        self.axisIdx = axisIdx
        print("Mesh axis set to axis:", axisIdx)
    
    def sortPoints(self):
        '''
        Sorts the vectorList by the x, y, or z axis based
        on the axisIdx
        '''
        # Don't sort if already sorted
        if (self.isSorted):
            return
        self.vectorList = va.sortPoints(self.axisIdx, self.vectorList)
        self.isSorted = True
        print("Sorted")

    def getCentroids(self) -> list[tuple[float, float, float]]:
        '''Gets the centroids of the mesh'''
        if self.centroidsUpdated == True:
            return self.centroids
        if self.isAutoTargetAxis:
            self.autoSetTargetAxis()
        self.centroids, self.vectorList = va.findCentroids(self)
        self.centroidsUpdated = True
        self.isSorted = True  # Finding the centroids sorts the points
        va.findCenterline(self)
        self.datameanUpdated = True
        return self.centroids

    def fitGeometry(self):
        self.getCentroids()
        if self.isAutoTargetAxis:
            self.autoSetTargetAxis()
        va.fitGeometry(self)
        # Rotation mixes points
        # centroids must be recomputed 
        self.resetState()

    def straighten(self, resolution = .01, show = True):
        '''Straightens the channel iteratively until the threshold set'''
        if show:
            print(f"Resolution {resolution}")
            ax1 = plt.axes(projection = '3d')
            plt.title("Original")
            vp.plotMesh(self.vectorList, ax1, resolution)
            plt.show()
        iteration = 1
        print(f"\nIteration: {iteration}    threshold: {THRESHOLD}")
        self.fitGeometry()
        if show == True and iteration % self.ITERATIONNUM == 0:
                plt.title(f"Iteration {iteration}")
                self.show(resolution)
        rotationSum = (self.curRotation[0] ** 2) + (self.curRotation[1] ** 2) + (self.curRotation[2] ** 2)
        print(f"Rotation: {self.curRotation} =  {rotationSum}")
        while not self.atThreshold():
            iteration += 1
            print(f"\nIteration: {iteration}")
            self.fitGeometry()
            rotationSum = (self.curRotation[0] ** 2) + (self.curRotation[1] ** 2) + (self.curRotation[2] ** 2)
            print(f"Rotation: {self.curRotation} =  {rotationSum}")
            print(f"Total rotation = {self.totalRotation}")
            if show == True and iteration % self.ITERATIONNUM == 0:
                plt.title(f"Iteration {iteration}")
                self.show(resolution)
        print(f"\nThreshold reached ({THRESHOLD})")
        print(f"  Last rotation (radians): {self.curRotation} = {rotationSum}")
        print(f"  Total rotation (radians): {self.totalRotation}")
        if show:
            plt.title("Straightened")
            self.show(resolution)

    
    # Make a diameter function for different slices

    def atThreshold(self):
        pt = self.getCentroids()[0] # Take a point from somewhere
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
        self.resetState()   # set flags to false

    def computeDiameter(self, width = 0):
        if self.diameterUpdated:
            return
        self.diameter, self.centers = self.diameterMethod(self.axisIdx, self.vectorList, self.dirVector, self.datamean)
        self.diameterUpdated = True
        #calculateDiameterByValue(axisIdx, sortedVL, dirVector, datamean, avgDiameter: dict = None) -> tuple[dict, list]
        #calculateDiameterAlongLine(axisIdx, vectorList, dirVector, datamean, avgDiameter: dict = None) -> tuple[dict, list]:
        #calculateDiameterBetweenCentroids(axisIdx, vectorList, points, avgDiameter: dict = None) -> tuple[dict, list]:

    ### Setters and Getters ###
    def getNumSlices(self) -> int:
        '''Gets the number of slices used to compute the mesh's centroids'''
        return self.SLICES
    def setNumSlices(self, numSlices: int):
        '''Sets the number of slices used to compute the mesh's centroids'''
        self.SLICES = numSlices
    def getDiameter(self) -> dict[float]:
        '''Gets the diameter dictionary along the mesh's center axis'''
        if self.diameterUpdated:
            return self.diameter
        self.computeDiameter()
        return self.diameter
    def getCenters(self):
        if self.diameterUpdated:
            return self.centers
        self.computeDiameter()
        return self.centers
    def getDatamean(self):
        print(f"datamean updated: {self.datameanUpdated}")
        if self.datameanUpdated == False:
            print("Updating datamean")
            va.findCenterline(self)
            self.datameanUpdated = True
            # self.dirVectorUpdated = True
            return self.datamean
        else:
            return self.datamean

    def getSortedVL(self):
        '''Gets the point cloud as a sorted list'''
        if self.isSorted:
            return self.vectorList
        self.sortPoints()
        return self.vectorList
    # For data purposes, gets the single avg diameter across
    # entire channel
    def getEntireDiameter(self, width):
        self.getCentroids()
        if not self.diameterUpdated:
            self.diameter, centers = va.condenseDiameterByChunk(self.axisIdx, width, self)
            self.diameterUpdated = True
        avgDiameter = self.diameter
        avgDiameterNum = 0
        for d in avgDiameter.values():
            avgDiameterNum += d
        avgDiameterNum /= len(avgDiameter)
        print(f"Average diameter across object: {avgDiameterNum}")
        return avgDiameterNum

    def resetState(self) -> None:
        '''Sets all flags to false so everything will be recomputed'''
        self.isSorted = False
        self.centroidsUpdated = False
        self.greatestSpanUpdated = False
        self.diameterUpdated = False
        self.datameanUpdated = False

    def setDiameterMethod(self, method):
        self.diameterMethod = method

    def setDiameterCenterline(self, axisIdx):
        '''Sets an axis to be used as the centerline.
        Set to -1 to reset to auto centerline (axis with longest span)

        axisIdx: the index of the axis to be used as the centerline
        '''
        # Reset if -1
        if axisIdx == -1:
            self.useAxisDiameterCenterline = False
            return
        # Use the given axis as the centerline
        self.useAxisDiameterCenterline = True
        dirVector = [0, 0, 0]
        dirVector[axisIdx] = 1
        self.dirVector = dirVector

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
        file.write(f"sorted,{self.isSorted}")
        file.write(f"centroidsFound,{self.centroidsUpdated}")
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

    ### Plotting
    def dprint(self, string, debug):
        if debug:
            print(string)

    def plotCentroids(self, ax):
        self.getCentroids()
        vp.plotCentroids(self.centroids, ax)

    def plotMesh(self, ax, resolution = .5):
        '''Plots the mesh. Default resolution of .5'''
        vp.plotMesh(self.vectorList, ax, resolution)

    def plotCenterLine(self, ax, debug = False):
        min = self.vectorList[-1][self.axisIdx]
        max = self.vectorList[0][self.axisIdx]
        self.dprint(f"Min: {self.vectorList[-1]}, Max: {self.vectorList[0]}", debug)
        vp.plotCenterLine(self.centroids, ax, min, max)

    # Shows centroids, centerline, mesh, and axes
    def show(self, resolution = 1, debug = False):
        ax1 = plt.axes(projection = '3d')
        self.plotCentroids(ax1)
        self.dprint(f"\nPlotting", debug)
        self.dprint(f"datamean: {self.datamean}", debug)
        self.plotCenterLine(ax1)
        self.plotMesh(ax1, resolution)
        self.plotTargetAxis(ax1, self.axisIdx)
        plt.show()
    
    def plotTargetAxis(self, ax, axisIdx):
        '''Plots the cardinal axes and extends the line of the target axis if existing'''
        axes = [[0, 0], [0, 0], [0, 0]]
        datamean = self.getDatamean()
        if axisIdx is not None:
            print(f"Axis is {self.axisIdx}")
            axes[axisIdx][1] = datamean[axisIdx]
            vp.plotAxes(ax, datamean[axisIdx] / 4)
            ax.plot3D(axes[0], axes[1], axes[2], c = "black")
        else:
            print("No axis targeted")
            print(f"datemean: {datamean}")
            vp.plotAxes(ax, (datamean[0] + datamean[1] + datamean[2]) / 3)

    def showMeshPreview(self, ax, resolution: int = .5):
        print("\nShowing Mesh Preview:")
        print(f"Auto-targeting: {self.isAutoTargetAxis}\nAxis selected: {self.axisIdx}\n")
        self.plotTargetAxis(ax, self.axisIdx)
        self.plotMesh(ax, resolution)
        plt.show()

    # Mostly deprecated, use chunkdiameter to show diameter plotted
    # along slice centerlines
    def plotDiameter(self, ax):
        self.getCentroids()
        self.computeDiameter()
        vp.plotDiameter(ax, self.getDiameter())
        
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

    def showDiameter(self, ax: plt.Axes = plt.axes()):
        self.plotDiameter()
        plt.show()
    
    # Shows plot for diameter and centers
    def plotDiameterInfo(self):
        self.plotDiameter()
        self.showCenters(self.getCenters())

    def saveDiameterPlot(self, filepath : str):
        '''Saves the diameter plot to the given filepath'''
        plt.clf()

        ax = plt.axes()
        self.plotDiameter(ax)
        plt.savefig(filepath, format= "png")

    def showCenters(self, centers):
        '''Plots the mesh and plots the center points used
        in the diameter calculation'''
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

    # TODO: Make chunkdiameter called by getDiameter
    def showChunkDiameter(self, specifiedWidth):
        plt.clf()
        ax = plt.axes()
        self.getCentroids()
        avgDiameter, centers = va.condenseDiameterByChunk(self.axisIdx, specifiedWidth, self)
        avgDiameterNum = 0
        for d in avgDiameter.values():
            avgDiameterNum += d
        avgDiameterNum /= len(avgDiameter)
        print(f"Average diameter across object: {avgDiameterNum}")
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
        self.diameter = avgDiameter
        self.diameterUpdated = True

    def cropDiameter(self, lower, upper):
        '''Takes the diameter calculated and crops based on the lower
        and upper values given'''
        diameter = self.diameter.copy()
        # Add to the new dictionary if within bounds
        for slice in self.diameter.items():
            if slice[0] < lower or slice[0] > upper:
                diameter.pop(slice[0])
        self.diameter = diameter
        

    def showCroppedChunkDiameter(self, ax, lower, upper):
        '''Takes the diameter calculated and crops based on the lower
        and upper values given'''
        self.cropDiameter(lower, upper)
        vp.plotDiameter(ax, self.diameter)
        
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
        #ax.set_ylim([0, None])
        plt.title("Diameter across the longest axis")
        plt.show()
