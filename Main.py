import Geometry
import VectorAnalyzer as va
import VectorPlotter as vp
import VectorReader as vr
import matplotlib.pyplot as plt
import numpy as np


vectorMap = vr.readVectors("./cyclinder_test.stl")
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
dirVector, datamean = vp.plotCenterLine(centroids, ax)

# Get the intercepts for axis=0
intercept = va.findPointAlongLine(dirVector, 1, datamean)
ax.scatter(intercept[0], intercept[1], intercept[2], color="red")

vp.clearPlot(ax)
va.fitGeometry(1, centroids, dirVector, datamean, vectorList)
vp.plotMesh(vectorList, ax)

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
