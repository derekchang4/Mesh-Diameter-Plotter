import numpy as np
import os as os
import sys as sys

# Manually adding parent folder to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#for path in sys.path:
#    print(path)
import Channel as ch
import VectorAnalyzer as va

# Finds the diameter value of all surface files
# in a folder

# Will not read files exceeding 3 GB
BYTESINMEG = 1000000
MAXMEGS = 3000
MAXSIZE = MAXMEGS * BYTESINMEG

# Enter the folder path
directory = r"C:\Users\dchan\Downloads\Illinois\ETRL\OneDrive_2024-08-20\8.13 Z1~Z4 Samples\clean"
fileDiameters = {}

# Accessing each file in the folder
for filename in os.listdir(directory):
    print(filename)
    f = os.path.join(directory, filename)
    size = os.path.getsize(f)
    # Checking for the correct file extension
    if ".wrl" not in filename and ".stl" not in filename:
        print(f"{filename} incompatible file")
        continue
    # Checking for the size of file
    if size > MAXSIZE:
        print(f"Skipping {filename}, greater than {MAXSIZE} megabytes")
        continue

    ##### Your code here
    channel = ch.Channel(f)
    channel.readVectors()
    channel.setTargetAxis(-1)    # Set which axis to target to slice from and straighten to
    # channel.setDiameterCenterline(2)    # Set which axis to measure diameter from
    channel.straighten(show=False)
    channel.saveDiameterPlot(fr"{directory}\{filename[:-4]}.png")

    # Crop off the ends that enclose the mesh
    # The axis values can be checked by plotting the diameter
    #channel.cropDiameter(100, 4800)  
    diameter = channel.getEntireDiameter(0)
    fileDiameters[filename] = diameter
    ###############

    print("\n")

### Prints out all the found diameters
print("\nDiameters found")
for f, diameter in fileDiameters.items():
    print(f"{f} = {diameter}")


def getAllDiameters(directory: str, maxMegabytes = MAXMEGS):
    # Enter the folder
    fileDiameters = {}
    for filename in os.listdir(directory):
        print(filename)
        f = os.path.join(directory, filename)
        size = os.path.getsize(f)
        if ".wrl" not in filename and ".stl" not in filename:
            print(f"{filename} incompatible file")
            continue
        if size > maxMegabytes * BYTESINMEG:
            print(f"Skipping {filename}, greater than {maxMegabytes} megabytes")
            continue
        channel = ch.Channel(f)
        channel.readVectors()
        channel.straighten(show=False)
        diameter = channel.getEntireDiameter(0)
        fileDiameters[filename] = diameter
        print("\n")

    print("\nDiameters found")
    for f, diameter in fileDiameters.items():
        print(f"{f} = {diameter}")
