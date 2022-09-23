from projector import Projector
from camera import Camera
import logging
import threading
import time

y = 1
size_line = 50
speedRender = 50

projector = 0
def RunProjector():
  global projector, y, size_line, projector
  projector = Projector()

  

  def update_frame():
    global y, size_line, projector
    projector.canvas.delete("all")
    # projector.canvas.create_rectangle(1,y,projector.screen_width,y + size_line, fill="black")
    y += speedRender
    if y + size_line >= projector.screen_height:
      y = 2
    projector.canvas.create_rectangle(1,y,projector.screen_width,y + size_line, fill="white")
    projector.canvas.update_idletasks()
    projector.canvas.after(5)
    projector.root.after(10, update_frame)

  update_frame()

  # projector.root.attributes('-fullscreen', True)
  projector.root.mainloop()

def runCamera():
  camera = Camera("http://10.90.148.134:8080/shot.jpg")

t1 = threading.Thread(target=RunProjector, args=())
# t2 = threading.Thread(target=runCamera, args=())
t1.start()
# t2.start()
t1.join()
# t2.join()