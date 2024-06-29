import numpy as np
import VectorAnalyzer as va
import Channel as chan

class Slice:
    def __init__(self) -> None:
        self.MINISLICES = None  # the number of centroids/minislices within
        self.vectorList = None  # all the points within the slice
        self.dirVector  = None  # tracks the directional vector through the slice
        self.centroids  = None  # tracks the centroids of this slice
        self.datamean   = None  # tracks the center of the slice
        self.axisIdx    = None  # tracks the axis along this slice
        self.vectorCount    = None # number of vertices in this

    # Finds the centroids of 
    def findCentroids(self):
        pass
    # Find a fit for the centroids and datamean
    def findCenterline(self):
        va.findCenterline(self)

    # Takes in a dictionary and adds to the slice-diameter index
    def calculateDiameter(self, avgDiameter):
        avgDiameter, centers = va.calculateDiameter(self.axisIdx, self.vectorList, self.dirVector, self.datamean, avgDiameter)
