class Slice:
    def __init__(self) -> None:
        self.MINISLICES = None  # the number of centroids/minislices within
        self.vectorList = None  # all the points within the slice
        self.dirVector  = None  # tracks the directional vector through the slice
        self.centroids  = None  # tracks the centroids of this slice
        self.datamean   = None  # tracks the center of the slice

    # Finds the centroids of 
    def findCentroids(self):

    # Finds the centerline and datamean of slice
    def findCenterLine(self):
