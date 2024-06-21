import VectorAnalyzer as va
import VectorPlotter as vp
import matplotlib.pyplot as plt
import numpy as np
#from mpl_toolkits import mplot3d


# This file reads an stl file and produces a list of all
# vertexes contained in the mesh. Excludes duplicate vertexes
# (x, y, z) : # times counted

def readVectors(fileName):
    file = open(fileName)   # default on "rt" (read, text)
    map = {}                # empty dictionary
    # Header
    line = file.readline()

    ### Continue reading shapes
    while line != '':
        # normal and outer loop
        file.readline()
        # If we passed endsolid marker
        if file.readline() == '':
            break
        point1 = readVertex(file)
        point2 = readVertex(file)
        point3 = readVertex(file)
        triangle = (point1, point2, point3)
        ## print(triangle)
        # Create a vertex to hold and insert into map
        # Tuples could work for x,y,z!
        map[point1] = map.get(point1, 0) + 1
        map[point2] = map.get(point2, 0) + 1
        map[point3] = map.get(point3, 0) + 1

        # Endloop and Endfacet
        file.readline()
        line = file.readline()
    file.close()
    return map

def sciToFloat(coord):
    idx = coord.find("e")
    if idx == -1:
        print("Error parsing vectors. Could not find exponent marker 'e+/-'")
        quit()
    numVal = float(coord[:idx]) #Convert to a float
    exp = int(coord[idx + 1:])  #Convert to an int
    numVal *= 10 ** exp
    # print("Exponent: ", exp)
    return numVal

# Returns a 3-tuple using a 3-array of 
# numbers in scientific notation
def readVertex(file):
    # Read in points, strip excess
    point = file.readline().strip()[6:].split()
    #print(point)
    # convert to numerical value
    x = sciToFloat(point[0])
    y = sciToFloat(point[1])
    z = sciToFloat(point[2])
    return (x, y, z)

## I'll make a vector class soon

# def storeVector
# def open # loads the file in
# def run
# def save


vectorMap = readVectors("./cyclinder_test.stl")
print(len(vectorMap), "Vertices")
print("Longest axis: ", va.greatestSpan(vectorMap))
centroids, vectorList = va.findCentroids(vectorMap)

ax = plt.axes(projection= '3d')
ax.scatter(0, 0, 0, s=20, color="black")
centroids = np.array(centroids)
vectorList = np.array(vectorList)

vp.plotCentroids(centroids, ax)
#va.rotate(vectorList, 90, 0)
vp.plotMesh(vectorList, ax)
vp.plotCenterLine(centroids, ax)

ax.margins(.2, .2, .2)
plt.show()




# ## Test for sign-mantissa conversion
# value = "7.06098e-01"
# idx = value.find("e")
# numVal = float(value[:idx])
# exp = int(value[idx + 1:])
# numVal *= 10 ** exp
# print("Exponent: ", exp)
# print("Original:", value)
# print("Post-exponentiated:", numVal)
