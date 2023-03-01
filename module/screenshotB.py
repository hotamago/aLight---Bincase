import cv2
import pyautogui
import threading
import numpy as np

class ScreenshotB():
  imgself = None
  size_out = (600, 400)
  stopped = False
  def __init__(self, size_out = (600, 400)):
    self.size_out = size_out
    self.stopped = False
    self.updateFrame()
  def updateFrame(self):
    self.imgself = cv2.resize(cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR), self.size_out)
    
  def getFrame(self):
    return np.copy(self.imgself)
  
  # Multi theard
  def startTheard(self):
    self.stopped = False
    threading.Thread(target=self.updateTheard, args=()).start()
  def updateTheard(self):
    while not self.stopped:
      self.updateFrame()
  def stop(self):
    self.stopped = True
