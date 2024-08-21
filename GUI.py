from tkinter import *
from tkinter import filedialog
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk) 
import Channel as ch
import VectorReader as vr

class GUI_Handler:
    '''This class handles the GUI for the
    Mesh-Diameter-Plotter'''
    def __init__(self):
        self.mesh:              ch.Channel = None
        '''The mesh the GUI is plotting'''
        self.window:            Tk = None
        '''The window of the GUI'''
        self.plotFrame:         Frame = None
        '''The frame where the 3d visualization will be displayed'''
        self.resolution:        float = .01       # TODO: abstract it
        '''A resolution setting for the number of points to plot'''
        self.diameterCenterlineAxis: int = -1
        '''The axis idx representation from which to measure diameter'''

        # State
        self.diameter: float    = None
        self.diameterWidth: float = 0

        # Flags
        self.foundCentroids:    bool = False    # NOTE: could get this from mesh
        self.straightened:      bool = False
        self.manualDiameterCenterline: bool = False
        
        # Plot
        self.axes               = None          # Holds the plot data
        self.fig                = None
        self.plotCanvas         = None
        self.toolbar            = None

        # Constants
        self.BUTTON_HEIGHT = 2
        self.BUTTON_WIDTH = 12

        # Buttons
        self.plot_button            = None
        self.straighten_button      = None
        self.find_centroid_button   = None
        self.rotate_button          = None
        self.plot_diameter_button   = None
        self.get_diameter_button    = None
        self.read_file_button       = None
        self.reset_button           = None
        self.set_button             = None

        # Entries
        self.slices_entry       = None
        self.resolution_entry   = None
        self.rotation_entry     = None
        self.target_axis_entry  = None
        self.diameter_centerline_entry = None

        # Info Labels
        self.slices_label       =  None
        self.resolution_label   =   None
        self.last_rotation_label    =   None
        self.total_rotation_label   =   None
        self.target_axis_label      =   None
        self.diameter_centerline_label = None
        self.diameter_label         = None


    ### BUTTON ACTIONS ###

    def plot(self):
        '''Creates a Matplotlib figure or updates it if one is already created'''
        # if self.fig == None:
        self.fig = fig = Figure(figsize= (4, 3), dpi= 100)
        # else:
        #     fig = self.fig

        if self.axes == None:
            self.axes = plot1 = fig.add_subplot(projection= '3d')
        else:
            plot1 = self.axes
            plot1.clear()

        if self.mesh == None:
            fig.suptitle("Default Plot")
            plot1.plot([0, 1], [0, 2], [0, 2])
            print("No mesh loaded, default plot")
        else:
            self.mesh.plotMesh(plot1, self.resolution)

        # create Tkinter canvas containing
        # matplotlib figure
        if self.plotCanvas == None:
            self.plotCanvas = canvas = FigureCanvasTkAgg(fig, master = self.plotFrame)
        else:
            canvas = self.plotCanvas

        if self.foundCentroids:
            self.mesh.plotCentroids(self.axes)
        canvas.draw()

        if self.toolbar == None:
            self.toolbar = toolbar = NavigationToolbar2Tk(canvas, self.plotFrame)
        else:
            toolbar = self.toolbar
        toolbar.update()
        canvas.get_tk_widget().pack(fill= BOTH, expand= True)
        self.updateInfoLabels()
        
    
    def getFile(self):
        '''Allows the user to select a file to load'''
        file = filedialog.askopenfile(mode='r', filetypes=[("Mesh files", "*.wrl *.stl")])
        if file == None:
            print("File not found")
        else:
            print(f"Opening {file}")
            file.close()
            print(file.name)
            self.mesh = ch.Channel(file.name)
            self.mesh.readVectors()
        self.updateInfoLabels()
    
    def findCentroids(self):
        self.checkMesh()
        if self.foundCentroids == True:
            return
        # Finds the centroids for the object
        self.mesh.getCentroids()
        self.foundCentroids = True
        self.mesh.plotCentroids(self.axes)
    
    def checkMesh(self) :
        if self.mesh == None:
            raise Exception("Mesh hasn't been loaded yet!")

    def straighten(self):
        self.checkMesh()
        self.updateState()
        # Straightens the mesh
        if self.straightened == True:
            return
        self.mesh.straighten(self.resolution, False)
        self.straightened = True
        self.updatePlot()
        self.updateInfoLabels()

    def rotate(self):
        '''Rotates the mesh by the amount given in the rotation entry box.
        Rotation is given as a space delimited string in radians. Rotates counterclockwise around each axis.'''
        self.checkMesh()
        # Rotates the mesh by the amount in the text box
        self.mesh.rotate(self.getRotationInput())
        self.straightened = False
        self.foundCentroids = False
        self.updateInfoLabels()
        self.updatePlot()

    def plotDiameter(self):
        self.checkMesh()
        # call the plot diameter function of Channel
        # TODO: Add functionality to intake width
        # Apply any settings
        self.updateState()
        self.diameter = self.mesh.getEntireDiameter(self.diameterWidth)
        # Display the new diameter
        self.updateInfoLabels()
        self.mesh.showChunkDiameter(specifiedWidth = 0)

    def getDiameter(self):
        self.checkMesh()
        self.updateState()
        self.diameter = self.mesh.getEntireDiameter(self.diameterWidth)
        self.updateInfoLabels()

    def reset(self):
        '''Resets the window and creates a new one'''
        self.onClose()
        self.__init__()
        self.createGUI()
        self.window.quit()

    ### BUTTON ACTIONS ###

    def setSlices(self, entry: Entry):
        '''Sets the number of slices used to
        compute the channel's centroids'''
        slices = entry.get()
        self.mesh.setSlices(slices)

    def onClose(self):
        self.window.quit()  # Exits mainloop
        self.window.destroy() # Exits mainloop and destroys window

    def updatePlot(self):
        self.plot()

    def updateInfoLabels(self):
        '''Updates the information labels at the bottom of the screen from the mesh's state. 
        Shows 'None' if no mesh is loaded'''
        if self.mesh is None:
            slices = "None"
            resolution = "None"
            currRotation = "None"
            totalRotation = "None"
            targetAxis = "None"
            targetDiameterAxis = "None"
            diameter = "None"
        else:
            slices = self.mesh.getNumSlices()
            currRotation = self.mesh.curRotation
            totalRotation = self.mesh.totalRotation
            targetAxis = self.mesh.axisIdx
            targetDiameterAxis = self.mesh.dirVector
            diameter = self.diameter

        resolution = self.resolution

        self.slices_label.config(text = f"Slices = {slices}")
        self.resolution_label.config(text = f"Resolution: {resolution}")
        self.last_rotation_label.config(text = f"Current Rotation: {currRotation}")
        self.total_rotation_label.config(text = f"Total Rotation: {totalRotation}")
        self.target_axis_label.config(text = f"Target Axis Idx: {targetAxis}")
        if self.manualDiameterCenterline:
            self.diameter_centerline_label.config(text = f"Diameter Axis (manual): {targetDiameterAxis}")
        else:
            self.diameter_centerline_label.config(text = f"Diameter Axis (auto): {targetDiameterAxis}")
        self.diameter_label.config(text = f"Avg Diameter: {diameter}")


    def getSlicesInput(self) -> int:
        '''Gets the input in the slices box. Returns None if empty'''
        slices = self.slices_entry.get()
        if slices != None and slices != "":
            return int(slices)
        else:
            return None
        
    def getResolutionInput(self) -> float:
        '''Gets the input in the resolution box. Returns None if empty'''
        resolution = self.resolution_entry.get()
        if resolution != None and resolution != "":
            return float(resolution)
        else:
            return None
        
    def getRotationInput(self) -> tuple[float, float, float]:
        '''Gets the input in the rotation box. Returns None if empty'''
        rotation = self.rotation_entry.get()
        if rotation != None and rotation != "":
            rotation = tuple([float(element) for element in rotation.split()])
            return rotation
        else:
            return None
    def getTargetAxisInput(self) -> int:
        '''Gets the input in the target axis box. Returns None if empty'''
        targetAxis = self.target_axis_entry.get()
        if targetAxis != None and targetAxis != "":
            return int(targetAxis)
        else:
            return None
        
    def getDiameterCenterline(self) -> int:
        '''Gets the input in the diameter centerline box. Returns None if empty'''
        diameterCenterline = self.diameter_centerline_entry.get()

        # If there is text in the entry
        if diameterCenterline != None and diameterCenterline != "":
            diameterCenterline = int(diameterCenterline)
            if diameterCenterline == -1:
                self.manualDiameterCenterline = False
            else:
                self.manualDiameterCenterline = True
            self.diameterCenterlineAxis = diameterCenterline
            return diameterCenterline
        else:
            return None
        
    def setResolution(self, resolution: float):
        '''Sets the resolution of 3d plotting'''
        if resolution <= 0:
            # throw exception
            raise Exception("Resolution can't be 0 or negative!")
        self.resolution = resolution
        

    def updateState(self):
        '''Takes in the inputs of the entries and sets the state of the mesh'''
        slices = self.getSlicesInput()
        resolution = self.getResolutionInput()
        rotation = self.getRotationInput()
        targetAxis = self.getTargetAxisInput()
        diameterCenterline = self.getDiameterCenterline()

        print(slices)
        print(resolution)
        print(rotation)
        print(targetAxis)
        print(diameterCenterline)

        if slices != None:
            self.mesh.setNumSlices(slices)
        if resolution != None:
            self.setResolution(resolution)
        if rotation != None:
            self.mesh.rotate(rotation)
        if targetAxis != None:
            self.mesh.setTargetAxis(targetAxis)
        else:
            self.mesh.setTargetAxis(-1)
        if diameterCenterline != None:
            self.mesh.setDiameterCenterline(diameterCenterline)
            self.mesh.setTargetAxis(diameterCenterline)
        else:
            self.mesh.setDiameterCenterline(-1)

        self.updateInfoLabels()

    def resetFlags(self):
        '''Resets the flags that mark centroids and straightening finished'''
        self.foundCentroids = False
        self.straightened = False

    def createGUI(self):
        self.window = Tk()
        self.window.protocol("WM_DELETE_WINDOW", self.onClose)
        # Add menubar
        menubar = Menu(self.window)
        self.window.config(menu = menubar)

        # Add file option in menubar
        filemenu = Menu(menubar, tearoff= 0)
        menubar.add_cascade(label= "File", menu = filemenu)
        filemenu.add_command(label= "Open", command = self.getFile)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command = self.window.quit)
        # Add help menu
        helpmenu = Menu(menubar, tearoff= 0)
        menubar.add_cascade(label='Help', menu = helpmenu)
        helpmenu.add_command(label='About')

        self.window.title("Mesh Diameter Plotter")
        self.window.geometry("600x600")

        # Build framing
        topFrame = Frame(self.window, bg= "red", height= 100, width= 300)
        topFrame.pack(side= "top", fill= BOTH, expand= True)
        self.plotFrame = plotFrame = Frame(topFrame, highlightcolor= "blue", height= 100, width= 300)
        plotFrame.pack(side= "left", anchor= "nw", fill= BOTH, expand= True)
        topRightFrame = Frame(topFrame, bg= "green", height = 100, width = 100)
        topRightFrame.pack(side= "right", fill= BOTH, expand= True)
        # Buttons and options
        buttonFrame = Frame(topRightFrame, bg = "yellow", height = 100, width= 100)
        buttonFrame.pack(side = "right", expand= True, anchor= W)
        # Entries
        entryFrame = Frame(topRightFrame, bg = "orange", height = 100, width = 200)
        entryFrame.pack(side = "left", fill= BOTH, expand = True)

        # Bottom frame
        bottomFrame = Frame(self.window, bg= "brown", height = 150, width = 300)
        bottomFrame.pack(side = "bottom", fill= BOTH, expand=True)

        # Create button
        self.plot_button = Button(master = buttonFrame,
                            command = self.plot,
                            height = self.BUTTON_HEIGHT,
                            width = self.BUTTON_WIDTH,
                            text = "Plot")
        self.straighten_button = Button(master = buttonFrame,
                                command = self.straighten,
                                height = self.BUTTON_HEIGHT,
                                width = self.BUTTON_WIDTH,
                                text = "Straighten")
        self.find_centroid_button = Button(master = buttonFrame,
                                    command = self.findCentroids,
                                    height = self.BUTTON_HEIGHT,
                                    width = self.BUTTON_WIDTH,
                                    text = "Find Centroids")
        self.rotate_button = Button(master = buttonFrame,
                            command = self.rotate,
                            height = self.BUTTON_HEIGHT,
                            width = self.BUTTON_WIDTH,
                            text = "Rotate")
        self.plot_diameter_button = Button(master = buttonFrame,
                                    command = self.plotDiameter,
                                    height = self.BUTTON_HEIGHT,
                                    width = self.BUTTON_WIDTH,
                                    text = "Plot Diameter")
        self.read_file_button = Button(master = buttonFrame,
                                command = self.getFile,
                                height = self.BUTTON_HEIGHT,
                                width = self.BUTTON_WIDTH,
                                text = "Read File")
        self.reset_button = Button(master = buttonFrame,
                              command = self.reset,
                              height = self.BUTTON_HEIGHT,
                              width = self.BUTTON_WIDTH,
                              text = "Reset")
        self.set_button = Button(master = buttonFrame,
                            command = self.updateState,
                            height = self.BUTTON_HEIGHT,
                            width = self.BUTTON_WIDTH,
                            text = "Set Options")
        self.get_diameter_button = Button(master= buttonFrame,
                                          command = self.getDiameter,
                                          height = self.BUTTON_HEIGHT,
                                          width = self.BUTTON_WIDTH,
                                          text = "Get Diameter")
        
        # Entry options
        #rotate_text = Text(rotate_Frame,
        #                   height = self.BUTTON_HEIGHT / 2,
        #                   width = self.BUTTON_WIDTH)
        slices_entry_label = Label(master = entryFrame,
                                   text = "Slices")
        self.slices_entry = Entry(master = entryFrame)
        resolution_entry_label = Label(master = entryFrame,
                                       text = "Resolution (number 0-1)")
        self.resolution_entry = Entry(master = entryFrame)
        rotation_entry_label = Label(master = entryFrame,
                                   text = "Rotation")
        self.rotation_entry = Entry(master = entryFrame)
        target_axis_entry_label = Label(master = entryFrame, 
                                        text = "Target Axis (-1 - 2)")
        self.target_axis_entry = Entry(master = entryFrame)
        diameter_centerline_entry_label = Label(master = entryFrame,
                                            text = "Diameter Centerline (-1 - 2)")
        self.diameter_centerline_entry = Entry(master = entryFrame)

        ## Info box
        self.slices_label = Label(master = bottomFrame)
        self.resolution_label = Label(master= bottomFrame)
        self.last_rotation_label = Label(master = bottomFrame)
        self.total_rotation_label = Label(master = bottomFrame)
        self.target_axis_label = Label(master = bottomFrame)
        self.diameter_centerline_label = Label(master = bottomFrame)
        self.diameter_label = Label(master = bottomFrame)
        self.updateInfoLabels()

        ### Packing
        # AKA placing button onto window
        self.read_file_button.pack()
        self.plot_button.pack()
    #    find_centroid_button.pack()
        self.straighten_button.pack()
        self.rotate_button.pack()
        self.plot_diameter_button.pack()
        self.get_diameter_button.pack()
        self.reset_button.pack()
        self.set_button.pack()

        # Entries
        slices_entry_label.pack()
        self.slices_entry.pack()
        resolution_entry_label.pack()
        self.resolution_entry.pack()
        rotation_entry_label.pack()
        self.rotation_entry.pack()
        target_axis_entry_label.pack()
        self.target_axis_entry.pack()
        diameter_centerline_entry_label.pack()
        self.diameter_centerline_entry.pack()

        # Info Section
        self.slices_label.pack()
        self.resolution_label.pack()
        self.last_rotation_label.pack()
        self.total_rotation_label.pack()
        self.target_axis_label.pack()
        self.diameter_centerline_label.pack()
        self.diameter_label.pack()
        # Options
        #rotate_Frame.pack()
        # rotate_text.pack()
        # Start mainloop
        self.window.mainloop()

gui = GUI_Handler()
gui.createGUI()
