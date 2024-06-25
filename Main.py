import VectorAnalyzer as va
import VectorPlotter as vp
import VectorReader as vr
import matplotlib.pyplot as plt
import numpy as np
import Geometry as geo

# Setup:
# 1. Create mesh object with file path

def testingOGCylinder():
    mesh = geo.Mesh("./cylinder_test.stl")
    mesh.readVectors()
    print(mesh.VECTORCOUNT, "Vertices")
    mesh.getGreatestSpan()
    print("Longest axis: ", mesh.greatestSpan)
    mesh.findCentroids()

    ax = plt.axes(projection= '3d')
    ax.scatter(0, 0, 0, s=20, color="black")
    #centroids = np.array(centroids)
    #vectorList = np.array(vectorList)

    mesh.plotCentroids(ax)
    #va.rotate(vectorList, 90, 0)
    mesh.plotMesh(ax)
    mesh.plotCenterLine(ax)
    # Get the intercepts for 0 along the axis
    intercept = va.findPointAlongLine(mesh.dirVector, mesh.axisIdx, mesh.datamean)
    ax.scatter(intercept[0], intercept[1], intercept[2], color="red")

    mesh.fitGeometry()
    mesh.plotMesh(ax)

    ax.margins(.2, .2, .2)
    plt.show()

def rotatedCylinderTest():
    mesh = geo.Mesh("files/rotatedCylinder.stl")
    mesh.readVectors()
    ax1 = plt.axes(projection= '3d')
    #mesh.findCentroids()
    #mesh.plotCenterLine(ax1)
    #mesh.plotMesh(ax1)
    plt.title("Original")
    #plt.show()
    mesh.plot()

    mesh.straighten()
    ax2 = plt.axes(projection= '3d')
    plt.title("Straightened")
    #mesh.findCentroids()
    #mesh.fitGeometry()
    mesh.plotCenterLine(ax2)
    mesh.plotMesh(ax2)
    plt.show()

    mesh.plotDiameter()

def bigCylinderTest():
    # HOLY MOLY 652636 Vertices
    mesh = geo.Mesh("files/middle.wrl")
    mesh.readVectors()
    ax = plt.axes(projection= '3d')
    plt.title("Original")
    mesh.plot()

    geo.updateIterationShown(7) # Show every 7th iteration
    mesh.straighten()
    mesh.plotDiameter()

def main():
    mesh = geo.Mesh("files/rotatedMPCylinder.stl")
    mesh.readVectors()
    geo.updateIterationShown(1)
    mesh.straighten()
    mesh.plotDiameter()

main()




# ## Test for sign-mantissa conversion
# value = "7.06098e-01"
# idx = value.find("e")
# numVal = float(value[:idx])
# exp = int(value[idx + 1:])
# numVal *= 10 ** exp
# print("Exponent: ", exp)
# print("Original:", value)
# print("Post-exponentiated:", numVal)
