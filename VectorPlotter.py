import numpy as np
import matplotlib.pyplot as plt
import Constants as c

NTHTERM = c.NTHTERM
SKIPLEN = 300

def dprint(string, print = False):
    if (print):
        print(string)

def plotCentroids(centroids, ax):
    #centroids should be numpy array
    ptsX = []
    ptsY = []
    ptsZ = []
    if centroids is None:
        print("do mesh.findCentroids first!")
        quit()
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
    ax.set_box_aspect((np.ptp(ptsX), np.ptp(ptsY), np.ptp(ptsZ)))  # aspect ratio is 1:1:1 in data space
    ax.scatter(ptsX, ptsY, ptsZ)


def plotCenterLine(centroids, ax, min, max, debug = False):
    centroids = np.array(centroids)
    print(f"Plot centerline centroids: {centroids}")
    print(centroids.size)
    if centroids is None or centroids.size == 0:
        print("Error: Call findCentroids() first! The direction vector, datamean, and centroids haven't been found yet!")
        quit()
    # Finding line of best fit
    print(centroids)
    datamean = centroids.mean(axis= 0)
    #print(datamean)

    # Use SVD to find the direction of the 
    # vector of best fit
    uu, dd, vv = np.linalg.svd(centroids - datamean)

    # Now generate points for plotting
    linepts = vv[0] * np.mgrid[min:max:2j][:, np.newaxis]
    dprint(f"VV[0]= {vv[0]}", debug)
    dprint(f"mgrid= {np.mgrid[min:max:2j][:, np.newaxis]}", debug)
    dprint(f"linepts= {linepts}", debug)
    linepts += datamean
    print("input to plot3d:", *linepts.T)
    ax.plot3D(*linepts.T)

# Takes in a dictionary of x value to avg diameter
def plotDiameter(ax, avgDiameter):
    axisVals = list(avgDiameter.keys())
    diameters = list(avgDiameter.values())
    # print(f"axisVals = {axisVals}\ndiameter = {diameters}")
    plt.scatter(axisVals, diameters)
    
    i = 0
    for v in avgDiameter.items():
        if (len(avgDiameter) > SKIPLEN):
            if (i % NTHTERM == 0):
                print(f"Skipped {NTHTERM} [{v[0]} : {v[1]}]")
        else:
            print(f"[{v[0]} : {v[1]}]")
        i += 1
        

# Takes in an axes object and clears it
def clearPlot(ax):
    ax.cla()
