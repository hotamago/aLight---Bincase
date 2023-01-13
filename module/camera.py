import urllib
import urllib.request
import cv2
import numpy as np
import ssl
import threading

class CameraWebIP:
  imgself = None
  size_out = (600, 400)
  url = ""
  def __init__(self, url, size_out = (600, 400)):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    self.size_out = size_out
    self.url = url
    self.updateFrame()
  def updateFrame(self):
    imgResp = urllib.request.urlopen(self.url)
    imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
    
    img = cv2.imdecode(imgNp, -1)
    img = cv2.resize(img,self.size_out)
    self.imgself = img
    
    self.success = True
  def getFrame(self):
    return np.copy(self.imgself)
  
  # Multi theard
  def startTheard(self):
    self.stopped = False
    threading.Thread(target=self.updateTheard, args=()).start()
  def updateTheard(self):
    while not self.stopped:
      if not self.success:
        self.stop()
      else:
        self.updateFrame()
  def stop(self):
    self.stopped = True

class CameraSelf:
  imgself = None
  success = False
  size_out = (600, 400)
  is_flip = False
  flip_mode = 0
  cap = None
  def __init__(self, size_out = (600, 400), exposure_value = 80, exposure_auto_value = 0, fps_value = 30):
    self.size_out = size_out
    self.cap = cv2.VideoCapture(0)
    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, size_out[0])
    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size_out[1])
    self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, exposure_auto_value)
    self.cap.set(cv2.CAP_PROP_EXPOSURE, exposure_value)
    self.cap.set(cv2.CAP_PROP_FPS,fps_value) 
    
    self.updateFrame()
  def setProperty(self, cap_prop, value):
    self.cap.set(cap_prop, value)
  def setExposure(self, exposure_value, exposure_auto_value = 0):
    self.setProperty(cv2.CAP_PROP_AUTO_EXPOSURE, exposure_auto_value)
    self.setProperty(cv2.CAP_PROP_EXPOSURE, exposure_value)
  def setFPS(self, fps_value):
    self.setProperty(cv2.CAP_PROP_FPS, fps_value)
  def updateFrame(self):
    self.success, img = self.cap.read()
    if self.success:
      img = cv2.resize(img,self.size_out)
      if self.is_flip:
        img = cv2.flip(img, self.flip_mode)
      self.imgself = img
    else:
      print("can't find camera")
  def getFrame(self):
    return np.copy(self.imgself)
  
  # Multi theard
  def startTheard(self):
    self.stopped = False
    threading.Thread(target=self.updateTheard, args=()).start()
  def updateTheard(self):
    while not self.stopped:
      if not self.success:
        self.stop()
      else:
        self.updateFrame()
  def stop(self):
    self.stopped = True

