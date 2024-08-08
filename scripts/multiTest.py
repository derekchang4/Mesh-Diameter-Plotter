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
directory = r"C:\Users\dchan\Downloads\Illinois\CT\Research Rush 7,31\Low\surf"
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
    channel.setTargetAxis(2)
    channel.setDiameterCenterline(2)
    # channel.straighten(show=False)
    # channel.saveDiameterPlot(fr"{directory}\{filename[:-4]}")
    channel.getEntireDiameter(0)
    channel.cropDiameter(10, 500)
    diameter = channel.getEntireDiameter(0)
    fileDiameters[filename] = diameter
    ###############

    print("\n")

### Prints out all the found diameters
print("\nDiameters found")
for f, diameter in fileDiameters.items():
    print(f"{f} = {diameter}")
