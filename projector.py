from tkinter import *
from tkinter import ttk

# a subclass of Canvas for dealing with resizing of windows
class ResizingCanvas(Canvas):
  def __init__(self,parent,**kwargs):
    Canvas.__init__(self,parent,**kwargs)
    self.bind("<Configure>", self.on_resize)
    self.height = self.winfo_reqheight()
    self.width = self.winfo_reqwidth()

  def on_resize(self,event):
    # determine the ratio of old width/height to new width/height
    wscale = float(event.width)/self.width
    hscale = float(event.height)/self.height
    self.width = event.width
    self.height = event.height
    # resize the canvas 
    self.config(width=self.width, height=self.height)
    # rescale all the objects tagged with the "all" tag
    self.scale("all",0,0,wscale,hscale)

class Projector:
  root = 0
  canvas = 0
  screen_width = 0
  screen_height = 0
  def __init__(self, size_window = (600, 400)):
    self.root = Tk()
    self.root.title("Bincase - Demo - projector");
    myframe = Frame(self.root)
    myframe.pack(fill=BOTH, expand=YES)
    
    #Get the current screen width and height
    # self.screen_width = self.root.winfo_screenwidth()
    # self.screen_height = self.root.winfo_screenheight()
    self.screen_width = size_window[0]
    self.screen_height = size_window[1]
    
    self.canvas = Canvas(self.root, bd=-2, width=self.screen_width, hei=self.screen_height, bg="black")
    self.canvas.pack(fill=BOTH, expand=YES)