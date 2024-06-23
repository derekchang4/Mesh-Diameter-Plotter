## This class represents a mesh geometry file
# and will include a set of vectors and
# anything else that might need to be stored

class Mesh:
    def __init__(self, filename):
        self.filename = filename
        self.vectorMap
        self.vectorCount
        self.vectorList     # required for sorting and ordering
        self.centroids      # represents the centroids of the slices of the channel
        self.datamean       # represents the center of the channel
        self.dirVector      # represents the slope of the centerline
        self.rotation       # tracks the rotation applied to the original mesh
