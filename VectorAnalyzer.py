# This file will find the maximum span along the shape,
# slice along the nearest axis and find the center of the
# collection of points, then use linear regression to 
# create an approximate fit for a centerline along the
# channel. This process will occur repeatedly until
# the change falls below the specified threshold

## axis (x, y, z)
# from timeit import default_timer as timer
#from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
import numpy as np
SLICES = 5

# Finds the axis with the greatest span
# and returns the letter of that axis
def greatestSpan(vectorMap):
    sampleVector = vectorMap.popitem()              #Get some vector
    vectorMap[sampleVector[0]] = sampleVector[1]    #Add it back in
    xMin = sampleVector[0][0]
    xMax = sampleVector[0][0]
    yMin = sampleVector[0][1]
    yMax = sampleVector[0][1]
    zMin = sampleVector[0][2]
    zMax = sampleVector[0][2]

    #Find maxes and mins
    for key in vectorMap.keys():
        if key[0] < xMin:
            xMin = key[0]
        elif key[0] > xMax:
            xMax = key[0]
        if key[1] < yMin:
            yMin = key[1]
        elif key[1] > yMax:
            yMax = key[1]
        if key[2] < zMin:
            zMin = key[2]
        elif key[2] > zMax:
            zMax = key[2]
    
    xSpan = xMax - xMin
    ySpan = yMax - yMin
    zSpan = zMax - zMin

    if xSpan >= ySpan and xSpan >= zSpan:
        maxSpan = xSpan
        return ("x", maxSpan)
    if ySpan > xSpan and ySpan > zSpan:
        maxSpan = ySpan
        return ("y", maxSpan)
    if zSpan > xSpan and zSpan > ySpan:
        maxSpan = zSpan
        return ("z", maxSpan)
    else:
        print("Error finding span")
        quit()
    

def findCentroids(vectorMap):
    #Sort vectors by x, y, or z parameter
    centroids = []
    axis, span = greatestSpan(vectorMap) 

    # Get index of the axis
    match axis:
        case "x":
            axisIdx = 0
        case "y":
            axisIdx = 1
        case "z":
            axisIdx = 2
        case _:
            print("Invalid axis; Quitting")
            quit()

    # Sort points
    vectorList = sortPoints(axis, vectorMap)
    sliceSize = span / SLICES
    max = vectorList[0][axisIdx]
    min = vectorList[-1][axisIdx]

    floor = max - sliceSize
    ceiling = max
    
    # Iterator to get each next vertex
    # Iteratively get sums of individual x, y, and z
    # then divide by # vertices to get
    # the avg x, y, and z per slice

    # start = timer()
    # numVertices = 0
    # for i in vectorList:
    #     if i[axisIdx] > floor and i[axisIdx] <= ceiling:
    #         pass
    # end = timer()
    # print("Method 1 took", end - start, "seconds")

    it = iter(vectorList)
    v = next(it)
    for i in range(SLICES):
        numVertices = 0
        sums = [0, 0, 0]
        # Move the floor all the way down if on last slice
        # to account for slight inaccuracy from floats
        if (i == SLICES - 1):
            floor = min - 1
        while v[axisIdx] > floor and v[axisIdx] <= ceiling:
            sums[0] += v[0]
            sums[1] += v[1]
            sums[2] += v[2]
            numVertices += 1
            try:
                v = next(it)
            except StopIteration: # No next error
                print("No vectors left")
                break
        # Calculate average by dividing each by numVertices
        centroid = [0, 0, 0]
        for j in range(len(sums)):
            centroid[j] = sums[j] / numVertices
        centroids.append(tuple(centroid))
        print("Slice:", i, ", numVertices:", numVertices, ", centroid:", tuple(centroid))
        #print("Iteration", i, "Floor:", floor)
        floor -= sliceSize
    # print("Min= ", min)
    return centroids, vectorList

def sortX(v):
    return v[0]
def sortY(v):
    return v[1]
def sortZ(v):
    return v[2]

# Sorts the points based on the letter axis
# highest to lowest
def sortPoints(axis, vectorMap):
    if (type(vectorMap) == dict):
        vectorList = list(vectorMap.keys())
    else:
        vectorList = vectorMap
    match axis:
        case "x":
            vectorList.sort(reverse = True, key = sortX)
        case "y":
            vectorList.sort(reverse = True, key = sortY)
        case "z":
            vectorList.sort(reverse = True, key = sortZ)
        case _:
            print("Invalid axis; Quitting")
            quit()
    #-for v in vectorList:
    #-    print(v)
    return vectorList

# Takes the vectorList and counts the number of points
# at each length value on the axis
def slicePoints(axisIdx, vectorList):
    it = iter(vectorList)
    v = next(it)
    slices = {}
    while v != None:
        length = v[axisIdx]
        slices[length] = slices.get(length, 0) + 1
        try:
            v = next(it)
        except StopIteration:
            print("Finished slicing")
            v = None
    return slices
    
# Sets a point on the centerline at the
# same level as the lowest point on the mesh
# to the origin
def setToOrigin(sortedVL, dirVector, axisIdx):
    
    pass

# Rotates the mesh by given number of degrees
# about the given axis
def rotate(vectorList, theta, axisIdx):
    # Convert to radians since sin,cos expect that
    thetaRadians = theta * np.pi / 180
    Rx = np.array([[1, 0, 0],
                  [0, np.cos(thetaRadians), -np.sin(thetaRadians)],
                  [0, np.sin(thetaRadians), np.cos(thetaRadians)]]
                  )
    Ry = np.array([[np.cos(thetaRadians), 0, np.sin(thetaRadians)],
                  [0, 1, 0],
                  [-np.sin(thetaRadians), 0, np.cos(thetaRadians)]]
                  )
    Rz = np.array([[np.cos(thetaRadians), -np.sin(thetaRadians), 0],
                  [np.sin(thetaRadians), np.cos(thetaRadians), 0],
                  [0, 0, 1]]
                  )
    Rotation = (Rx, Ry, Rz)
    for i in range(len(vectorList)):
        vectorList[i] = Rotation[axisIdx] @ vectorList[i]

#Find a fit for the centroids
def findFit():
    pass

### Track rotation later
#Fit the line of the centroids to be parallel with the axis
def fitGeometry(axisIdx, dirVector, centroids):
    # Centroids sorted by height due to slicing
    pt = centroids[0] 
    coords = [False, False, False]
    coords[axisIdx] = True
    for axis in coords:
        if axis == True:
            np.arctan(pt[axisIdx] / pt[])
            rotate()

# Finds a point along some line given the values of
# one coordinate
def findPointAlongLine(dirVector, axisIdx, axisVal):

#! Not tested
def calculateDiameter(axisIdx, sortedVL, dirVector):
    dirVector = np.array(dirVector)
    # Axis length to avg diameter at that length
    avgDiameter = {}
    slices = slicePoints(axisIdx, sortedVL)
    it = iter(sortedVL)
    v = next(it)
    for k in slices:
        totalDiameter = 0
        while k[0] == v[axisIdx]:
            scalar = v[axisIdx] / dirVector[axisIdx]    # This is how much we need to multiply
            # the direction vector by to get to the same plane as v[axisIdx]
            center = dirVector * scalar
            print(v, "vs", center)
            # Euclidean distance using numpy
            dist = np.linalg.norm(v - center)
            totalDiameter += dist * 2
            try:
                v = next(it)
            except StopIteration:
                print("Finished calculating diameter")
                v = None
        avgDiameter[k[0]] = totalDiameter / k[1]    # divide the diameter total by num of points
    # Returns dict of lengths along longest axis to avg diameters
    return avgDiameter
        

def plotDiameter():
    pass

print("Vector Analyzer imported")

