import numpy as np
from .. import VectorAnalyzer as va
import os as os
import Channel as ch

# Finds the diameter value of all surface files
# in a folder

# Will not read files exceeding 3 GB
BYTESINMEG = 1000000
MAXMEGS = 3000
MAXSIZE = MAXMEGS * BYTESINMEG

# Enter the folder
directory = r"C:\Users\dchan\Downloads\Illinois\CT\derekmc2_49_longsample sonicated_184809\Data\surf\test"
fileDiameters = {}
for filename in os.listdir(directory):
    print(filename)
    f = os.path.join(directory, filename)
    size = os.path.getsize(f)
    if ".wrl" not in filename and ".stl" not in filename:
        print(f"{filename} incompatible file")
        continue
    if size > MAXSIZE:
        print(f"Skipping {filename}, greater than {MAXSIZE} megabytes")
        continue
    channel = ch.Channel(f)
    channel.readVectors()
    channel.straighten(show=False)
    channel.plotDiameter()
    channel.saveDiameterPlot(fr"{filename[:-4]}")
    diameter = channel.getEntireDiameter(0)
    fileDiameters[filename] = diameter
    print("\n")

print("\nDiameters found")
for f, diameter in fileDiameters.items():
    print(f"{f} = {diameter}")
