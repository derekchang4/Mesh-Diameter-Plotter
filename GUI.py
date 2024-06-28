from tkinter import *
import matplotlib as plt


def plot():
    fig = plt.axes()
    # create Tkinter canvas containing
    # matplotlib figure
    canvas = plt.FigureCanvasTkAgg(fig, master = window)

    canvas.draw()

    canvas.getTKwidget().pack()

    toolbar = plt.NavitionToolbar2Tk(canvas, window)


window = Tk()

window.title("Mesh Diameter Approximation")
window.geometry("500x500")


# Create button
plot_button = Button(master = window,
                     command = plot,
                     height = 2,
                     width = 10,
                     text = "Plot")

# Place button onto window
plot_button.pack()

window.mainloop()
