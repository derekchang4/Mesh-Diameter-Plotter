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
import Constants as c

# Number of slices for computing centroids
#SLICES = 5
# Will print every nth point if num points
# greater than COMPRESSLEN
#NTHTERM = 500
# Limit before the prints will skip
#SKIPLEN = 1000

SLICES = c.SLICES
NTHTERM = c.NTHTERM
SKIPLEN = c.SKIPLEN

def dprint(string, debug = False):
    if (debug):
        print(string)

# Finds the axis with the greatest span
# and returns the letter of that axis
def greatestSpan(mesh):
    sampleVector = mesh.vectorList[0]                    #Get some vector
    xMin = sampleVector[0]
    xMax = sampleVector[0]
    yMin = sampleVector[1]
    yMax = sampleVector[1]
    zMin = sampleVector[2]
    zMax = sampleVector[2]

    #Find maxes and mins
    for point in mesh.vectorList:
        if point[0] < xMin:
            xMin = point[0]
        elif point[0] > xMax:
            xMax = point[0]
        if point[1] < yMin:
            yMin = point[1]
        elif point[1] > yMax:
            yMax = point[1]
        if point[2] < zMin:
            zMin = point[2]
        elif point[2] > zMax:
            zMax = point[2]
    
    xSpan = xMax - xMin
    ySpan = yMax - yMin
    zSpan = zMax - zMin

    if xSpan >= ySpan and xSpan >= zSpan:
        maxSpan = xSpan
        mesh.greatestSpan = ("x", maxSpan)
        mesh.axisIdx = 0
        return ("x", maxSpan)
    if ySpan > xSpan and ySpan > zSpan:
        maxSpan = ySpan
        mesh.greatestSpan = ("y", maxSpan)
        mesh.axisIdx = 1
        return ("y", maxSpan)
    if zSpan > xSpan and zSpan > ySpan:
        maxSpan = zSpan
        mesh.greatestSpan = ("z", maxSpan)
        mesh.axisIdx = 2
        return ("z", maxSpan)
    else:
        print("Error finding span")
        quit()
    

def findCentroids(mesh, debug = False):
    #Sort vectors by x, y, or z parameter
    centroids = []
    axis, span = greatestSpan(mesh) 

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
    mesh.vectorList = sortPoints(axis, mesh.vectorList)
    vectorList = mesh.vectorList
    print(f"Axis idx: {axisIdx}")
    # print(vectorList)
    sliceSize = span / SLICES
    max = vectorList[0][axisIdx]
    min = vectorList[-1][axisIdx]

    floor = max - sliceSize
    ceiling = max
    
    # Iterator to get each next vertex
    # Iteratively get sums of individual x, y, and z
    # then divide by # vertices to get
    # the avg x, y, and z per slice

    it = iter(vectorList)
    v = next(it)
    dprint(f"Span: {mesh.greatestSpan}  SliceSize: {sliceSize}", debug)
    dprint(f"Floor: {floor}  Ceiling: {ceiling}", debug)
    for i in range(SLICES):
        numVertices = 0
        sums = [0, 0, 0]
        # Move the floor all the way down if on last slice
        # to account for slight inaccuracy from floats
        if (i == SLICES - 1):
            floor = min - 1
        #print(f"First point: {v[axisIdx]} <= {ceiling} = {v[axisIdx] <= ceiling}")
        #print(f"Within constraints?  {v[axisIdx] > floor and v[axisIdx] <= ceiling}")
        while v[axisIdx] > floor and v[axisIdx] <= ceiling:
            #print(f"{floor} < {v[axisIdx]} < {ceiling}")
            sums[0] += v[0]
            sums[1] += v[1]
            sums[2] += v[2]
            numVertices += 1
            try:
                v = next(it)
            except StopIteration: # No next error
                #print("No vectors left")
                break
        # Calculate average by dividing each by numVertices
        centroid = [0, 0, 0]
        foundVertices = False
        for j in range(len(sums)):
            if numVertices == 0:
                pass
            else:
                centroid[j] = sums[j] / numVertices
                foundVertices = True
        if foundVertices:
            centroids.append(tuple(centroid))
        dprint(f"Slice: {i}, numVertices: {numVertices}, centroid: {tuple(centroid)}", True)
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
def sortPoints(axis, vectorCollection):
    if (type(vectorCollection) == dict):
        vectorList = list(vectorCollection.keys())
    else:
        vectorList = list(vectorCollection)
    match axis:
        case "x":
            vectorList.sort(reverse = True, key = sortX)
        case "y":
            print(type(vectorList))
            vectorList.sort(reverse = True, key = sortY)
        case "z":
            vectorList.sort(reverse = True, key = sortZ)
        case _:
            if isinstance(axis, int) and axis > -1 and axis < 3:
                pass
            else:
                print("Invalid axis; Quitting")
                quit()
    #-for v in vectorList:
    #-    print(v)
    return vectorList

# Takes the vectorList and counts the number of points
# at each length value on the axis. Used in plotting
def slicePoints(axisIdx, vectorList):
    vectorList = sortPoints(axisIdx, vectorList)
    it = iter(vectorList)
    v = next(it)
    slices = {}
    while v is not None:
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
def rotate(vectorList, theta, axisIdx, radians= False):
    if radians == False:
        # Convert to radians since sin,cos expect that
        thetaRadians = theta * np.pi / 180
    else:
        thetaRadians = theta
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
def findCenterline(mesh):
    centroids = np.array(mesh.centroids)
    # Finding line of best fit
    datamean = centroids.mean(axis= 0)
    #print(datamean)

    # Use SVD to find the direction of the 
    # vector of best fit
    uu, dd, vv = np.linalg.svd(centroids - datamean)
    mesh.dirVector = vv[0]
    mesh.datamean = datamean
    # Use this direction vector elsewhere + datamean

### Track rotation later
#Fit the line of the centroids to be parallel with the axis
def fitGeometry(mesh, debug = False):
    # Takes the original vectorList and rotates by
    # the accumulated rotation to limit float error
    axisIdx = mesh.axisIdx
    centroids = mesh.centroids
    dirVector = mesh.dirVector
    datamean = mesh.datamean
    vectorList = mesh.OGVECTORLIST.copy()
    #vectorList = mesh.vectorList
    # Centroids sorted by height due to slicing
    pt = centroids[0] 
    # We need the longest axis paired with the other 2

    # True means it's been used; ie not to be used
    axes = [False, False, False]
    axes[axisIdx] = True
    origin = findPointAlongLine(dirVector, axisIdx, datamean)
    dprint(f"Point: {pt}", debug)
    dprint("Line origin: {origin}", debug)
    
    # Rotate about the other 2 axes
    for count, axis in enumerate(axes):
        if axis == False:
            # Get angle of rotation
            dprint(f"Comparing axis {axisIdx} and {count}", debug)
            dprint(f"Difference ({pt[axisIdx] - origin[axisIdx]}, {pt[count] - origin[count]})", debug)
            theta = np.arctan((pt[axisIdx] - origin[axisIdx]) / (pt[count] - origin[count]))
            rotationTheta = None
            # Rotate to vertical depending the closer rotation
            # range of arctan is pi/2 to -pi/2
            if (theta >= 0):
                rotationTheta = (np.pi / 2) - theta
            else:
                rotationTheta = -(np.pi / 2) - theta
            dprint(f"{theta} radians from axis", debug)
            dprint(f"Rotating by {rotationTheta} radians to fit", debug)
            # Mark axis
            axes[count] = True
            rotationAxis = None
            # Get other axis to rotate about
            for idx, status in enumerate(axes):
                if (status == False):
                    rotationAxis = idx
                    dprint(f"Rotated about axis {idx}", debug)
            # Add to the total rotation the mesh has experienced
            mesh.totalRotation[rotationAxis] += rotationTheta       
            mesh.curRotation[rotationAxis] = rotationTheta
            rotate(vectorList, mesh.totalRotation[rotationAxis], rotationAxis, True)
            # Unmark so the next rotation can use this axis
            axes[count] = False
    mesh.vectorList = vectorList


# Finds a point along some line given the values of
# one coordinate and a point
def findPointAlongLine(dirVector, axisIdx, datamean, axisVal = 0, debug = False):
    # (x, y, z) = dirVector * t + (datamean)

    # t is the scalar at which that axis hits 0
    t = (axisVal -datamean[axisIdx]) / dirVector[axisIdx]
    dprint(f"t at coord[{axisIdx}] = 0 is {t}", debug)
    foundPoint = (dirVector * t) + datamean
    dprint(f"Point found: {foundPoint}", debug)

    return foundPoint
    

#! Not tested
# may need to add datamean
def calculateDiameter(axisIdx, sortedVL, dirVector, datamean):
    dirVector = np.array(dirVector)
    # Axis length to avg diameter at that length
    avgDiameter = {}
    centers = []
    slices = slicePoints(axisIdx, sortedVL)
    it = iter(sortedVL)
    v = next(it)
    i = 0
    for k in slices.items():
        totalDiameter = 0
        # print(f"k = {k}  v = {v}")
        while k[0] == v[axisIdx]:
            # scalar = v[axis] - datamean / dirVector
            ## Wrong! -> scalar = v[axisIdx] / (dirVector[axisIdx] + datamean[axisIdx]) 
            scalar = (v[axisIdx] - datamean) / dirVector[axisIdx]    
            # This is how much we need to multiply
            # the direction vector by to get to the same plane as v[axisIdx]
            center = dirVector * scalar + datamean
            i += 1
            if (len(sortedVL) < SKIPLEN):
                print(v, "vs", center)
            elif i % (NTHTERM * 5) == 0:
                centers.append(center)
                print("Shortened", v, "vs", center)
            # Euclidean distance using numpy
            dist = np.linalg.norm(v - center)
            totalDiameter += dist * 2
            try:
                v = next(it)
            except StopIteration:
                print("Finished calculating diameter")
                break
        avgDiameter[k[0]] = totalDiameter / k[1]    # divide the diameter total by num of points
    # Returns dict of lengths along longest axis to avg diameters
    return avgDiameter, centers
        

print("Vector Analyzer imported")

