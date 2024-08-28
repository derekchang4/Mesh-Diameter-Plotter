import VectorAnalyzer as va
import VectorPlotter as vp
import VectorReader as vr
import matplotlib.pyplot as plt
import numpy as np
import Channel as chan


# This is the main file. This is where the code that 

# Setup:
# 1. Create mesh object with file path

def commandLineInterface():
    '''
    This is the function that runs a command-line interface
    '''
    filename = input("Paste in the file path: ")
    channel = chan.Channel(filename)
    channel.readVectors()
    """
    [Options]
    1. Plot mesh
    2. Straighten
    3. Print total rotation
    4. Print avg diameter
    5. Plot diameter across length
    """

def commandLine(channel):
    #print("""Actions:
    #      [1] Rotate
    #      [2]
    #      """)
    print("\n###              Command line started            ###")
    print("You have access to the channel object. You can use this to debug : ex. print(channel.vectorList)")
    print("Enter 'q' to quit")
    command = input("\nEnter your python command: ")
    while command != 'q':
        try:
            exec(command)
        except Exception as error:
            print("An exception occured: ", type(error).__name__)
        command = input("\n$ ")

def main():
    channel = chan.Channel(r"C:\Users\dchan\Downloads\Illinois\ETRL\OneDrive_2024-08-20\8.13 Z1~Z4 Samples\clean\junseoc2_51_Long-Sample_113148.surf_Z1.wrl")
    channel.readVectors()
    ax = plt.axes(projection = '3d')

    channel.setTargetAxis(-1)   # Target axis always needs to be set
    channel.showMeshPreview(ax, .005)
    
    channel.straighten(.001, False)
    channel.showMeshPreview(ax, .002)

    # Show datamean
    #dm = channel.datamean
    #print(dm)
    #ax = plt.axes(projection = '3d')
    #channel.plotMesh(ax, .01)
    #ax.scatter(dm[0], dm[1], dm[2], s= 20)
    #plt.show()
    channel.setTargetAxis(2)
    channel.setDiameterCenterline(2)
    channel.showChunkDiameter(0)
    channel.showCroppedChunkDiameter(ax, 100, 4800)
    channel.getAverageDiameter(0)

main()





## Below are old test-runs. They aren't that important and
## can be deleted but these can be used as examples
def testingOGCylinder():
    mesh = chan.Channel("./cylinder_test.stl")
    mesh.readVectors()
    print(mesh.VECTORCOUNT, "Vertices")
    mesh.getGreatestSpan()
    print("Longest axis: ", mesh.greatestSpan)
    mesh.getCentroids()

    ax = plt.axes(projection= '3d')
    ax.scatter(0, 0, 0, s=20, color="black")
    #centroids = np.array(centroids)
    #vectorList = np.array(vectorList)

    mesh.plotCentroids(ax)
    #va.rotate(vectorList, 90, 0)
    mesh.plotMesh(ax)
    mesh.plotCenterLine(ax)
    # Get the intercepts for 0 along the axis
    intercept = va.findPointAlongLineWithAxis(mesh.dirVector, mesh.axisIdx, mesh.datamean)
    ax.scatter(intercept[0], intercept[1], intercept[2], color="red")

    mesh.fitGeometry()
    mesh.plotMesh(ax)

    ax.margins(.2, .2, .2)
    plt.show()

def rotatedCylinderTest():
    mesh = chan.Channel("files/rotatedCylinder.stl")
    mesh.readVectors()
    ax1 = plt.axes(projection= '3d')
    #mesh.plotCenterLine(ax1)
    #mesh.plotMesh(ax1)
    plt.title("Original")
    #plt.show()
    mesh.show()

    mesh.straighten()
    ax2 = plt.axes(projection= '3d')
    plt.title("Straightened")
    #mesh.findCentroids()
    #mesh.fitGeometry()
    mesh.plotCenterLine(ax2)
    mesh.plotMesh(ax2)
    plt.show()

    mesh.plotDiameter(ax2, mesh.filename)

def bigCylinderTest():
    # HOLY MOLY 652636 Vertices
    mesh = chan.Channel("files/middle.wrl")
    mesh.readVectors()
    ax = plt.axes(projection= '3d')
    plt.title("Original")
    mesh.show()

    chan.updateIterationShown(7) # Show every 7th iteration (doesn't work still :/)
    mesh.straighten()
    mesh.plotDiameter(ax, mesh.filename)

def manualRotationTest():
    mesh = chan.Channel("files/rotatedCylinder.stl")
    mesh.readVectors()
    ax1 = plt.axes(projection= '3d')

    plt.title("Original")
    mesh.show()

    print("Starting manual rotation...")
    print("Input changes in radians in the format -> radians rotationAxis")
    str = ''
    while str != 'q':
        print("Input q to quit")
        str = input("Enter rotation (radians rotationAxis): ")
        fields = str.split()
        try:
            radians = float(fields[0])
            axis = int(fields[1])
        except:
            if str == 'q':
                break
            print("Invalid input! Try again")
            continue
        mesh.rotate(radians, axis)
        mesh.show()
        

def basicHighVector():
    channel = chan.Channel("files/bottom.wrl")
    channel.readVectors()
    #mesh.updateIterationShown(1)
    channel.straighten(.001)
    ax = plt.axes(projection = '3d')
    channel.plotDiameter(ax, channel.filename)


def main1():
    channel = chan.Channel("files/bottom.wrl")
    channel.readVectors()
    channel.rotate((0.007530334121267357, 0.008571440884751702, 0))
    channel.straighten(.001, False)
    #channel.findCentroids()
    channel.computeMiniSlices()
    #channel.straightenSlices(.001, False)
    channel.showSlices(.001)
    num = 1
    # for s in channel.slices:
    #     print(f"Slice {num}")
    #     print(f"  datamean= {s.datamean} dirV= {s.dirVector}")
    #     print(f"  First v= {s.vectorList[0]} Last v= {s.vectorList[-1]} count= {s.VECTORCOUNT}")
    #     print(f"  centroids: {s.centroids}")
    #     num += 1
    # Find amira documentation for thresholding: None found!
    channel.showChunkDiameter(0)
    #commandLine(channel)
