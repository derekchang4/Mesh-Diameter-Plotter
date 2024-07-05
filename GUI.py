from tkinter import *
from tkinter import filedialog
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk) 
import Channel as ch

class GUI_Handler:
    def __init__(self):
        self.mesh:              ch.Channel = None
        self.window:            Tk = None
        self.plotFrame:         Frame = None
        self.foundCentroids:    bool = False
        self.straightened:      bool = False
        self.resolution:        float = 1       # TODO: abstract it

    def plot(self):
        fig: Figure = Figure(figsize= (4, 3), dpi= 100)

        plot1 = fig.add_subplot(projection= '3d')
        if self.mesh == None:
            plot1.plot([0, 1], [0, 2], [0, 2])
            print("No mesh loaded, default plot")
        else:
            self.mesh.plotMesh(plot1, self.resolution)

        # create Tkinter canvas containing
        # matplotlib figure
        canvas = FigureCanvasTkAgg(fig, master = self.plotFrame)

        canvas.draw()

        toolbar = NavigationToolbar2Tk(canvas, self.plotFrame)
        toolbar.update()
        canvas.get_tk_widget().pack(fill= BOTH, expand= True)
        
    # Reads vectors
    def getFile(self):
        file = filedialog.askopenfile(mode='r', filetypes=[("Mesh files", "*.wrl *.stl")])
        if file == None:
            print("File not found")
        else:
            print(f"Opening {file}")
            file.close()
            print(file.name)
            self.mesh = ch.Channel(file.name)
            self.mesh.readVectors()
    
    def findCentroids(self):
        self.checkMesh()
        if self.foundCentroids == True:
            return
        # Finds the centroids for the object
        self.mesh.findCentroids()
        self.foundCentroids = True
    
    def checkMesh(self) :
        if self.mesh == None:
            raise Exception("Mesh hasn't been loaded yet!")

    def straighten(self):
        self.checkMesh()
        # Straightens the mesh
        if self.straightened == True:
            return
        self.mesh.straighten(self.resolution, True)
        self.straightened = True

    def rotate(self):
        self.checkMesh()
        # Rotates the mesh by the amount in the text box
        self.mesh.rotate((x, y, z))
        self.straightened = False
        self.foundCentroids = False

    def plotDiameter(self):
        self.checkMesh()
        # call the plot diameter function of Channel
        # TODO: Add functionality to intake width
        self.mesh.plotChunkDiameter(specifiedWidth = 0)

    def createGUI(self):
        self.window = Tk()
        # Add menubar
        menubar = Menu(self.window)
        self.window.config(menu = menubar)

        # Add file option in menubar
        filemenu = Menu(menubar, tearoff= 0)
        menubar.add_cascade(label= "File", menu= filemenu)
        filemenu.add_command(label= "Open", command= self.getFile)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.window.quit)
        # Add help menu
        helpmenu = Menu(menubar, tearoff= 0)
        menubar.add_cascade(label='Help', menu=helpmenu)
        helpmenu.add_command(label='About')

        self.window.title("Mesh Diameter Plotter")
        self.window.geometry("500x500")

        # Build framing
        topFrame = Frame(self.window, bg= "red", height= 100, width= 300)
        topFrame.pack(side= "top", fill= BOTH, expand= True)
        self.plotFrame = plotFrame = Frame(topFrame, highlightcolor= "blue", height= 100, width= 100)
        plotFrame.pack(side= "left", anchor= "nw", fill= BOTH, expand= True)
        topRightFrame = Frame(topFrame, bg= "green", height = 100, width = 100)
        topRightFrame.pack(side= "right")

        buttonFrame = Frame(topRightFrame, bg = "yellow", height = 100, width= 100)
        buttonFrame.pack(side = "right")
        optionsFrame = Frame(topRightFrame, bg = "orange", height = 100, width = 100)
        optionsFrame.pack(side = "left")

        # Bottom frame
        bottomFrame = Frame(self.window, bg= "brown", height = 150, width = 300)
        bottomFrame.pack(side = "bottom", fill= BOTH, expand=True)

        # Create button
        plot_button = Button(master = buttonFrame,
                            command = self.plot,
                            height = 2,
                            width = 10,
                            text = "Plot")
        straighten_button = Button(master = buttonFrame,
                                command = self.straighten,
                                height = 2,
                                width = 10,
                                text = "Straighten")
        find_centroid_button = Button(master = buttonFrame,
                                    command = self.findCentroids,
                                    height = 2,
                                    width = 10,
                                    text = "Find Centroids")
        rotate_button = Button(master = buttonFrame,
                            command = self.rotate,
                            height = 2,
                            width = 10,
                            text = "Rotate")
        plot_diameter_button = Button(master = buttonFrame,
                                    command = self.plotDiameter,
                                    height = 2,
                                    width = 10,
                                    text = "Plot Diameter")
        read_file_button = Button(master = buttonFrame,
                                command = self.getFile,
                                height = 2,
                                width = 10,
                                text = "Read File")

        # read file
        # calculate centroids, datamean, etc
        # fitGeometry
        # straighten

        # Place button onto window
        read_file_button.pack()
        plot_button.pack()
        find_centroid_button.pack()
        straighten_button.pack()
        rotate_button.pack()
        plot_diameter_button.pack()
        # Start mainloop
        self.window.mainloop()

gui = GUI_Handler()
gui.createGUI()
