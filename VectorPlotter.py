import numpy as np
import matplotlib.pyplot as plt

def plotCentroids(centroids, ax):
    #centroids should be numpy array
    ptsX = []
    ptsY = []
    ptsZ = []
    for v in centroids:
        ptsX.append(v[0])
        ptsY.append(v[1])
        ptsZ.append(v[2])
    ptsX = np.array(ptsX)
    ptsY = np.array(ptsY)
    ptsZ = np.array(ptsZ)
    ax.scatter(ptsX, ptsY, ptsZ)

def plotMesh(vectorList, ax):
    # VectorList should be numpy array
    ptsX = []
    ptsY = []
    ptsZ = []
    for v in vectorList:
        ptsX.append(v[0])
        ptsY.append(v[1])
        ptsZ.append(v[2])
    ptsX = np.array(ptsX)
    ptsY = np.array(ptsY)
    ptsZ = np.array(ptsZ)
    ax.scatter(ptsX, ptsY, ptsZ)


def plotCenterLine(centroids, ax):
    # Finding line of best fit
    datamean = centroids.mean(axis= 0)
    #print(datamean)

    # Use SVD to find the direction of the 
    # vector of best fit
    uu, dd, vv = np.linalg.svd(centroids - datamean)

    # Now generate points for plotting
    linepts = vv[0] * np.mgrid[-1000:1000:2j][:, np.newaxis]
    print("VV[0]= ", vv[0])
    print("mgrid= ", np.mgrid[-1000:1000:2j][:, np.newaxis])
    print("linepts= ", linepts)
    linepts += datamean
    print("input to plot3d:", *linepts.T)
    ax.plot3D(*linepts.T)
    return vv[0], datamean
    # Use this direction vector elsewhere + datamean

# Takes in an axes object
def clearPlot(ax):
    ax.cla()
