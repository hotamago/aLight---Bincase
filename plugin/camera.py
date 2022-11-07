import urllib
import urllib.request
import cv2
import numpy as np
import ssl

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
  def updateFrame(self):
    imgResp = urllib.request.urlopen(self.url)
    imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
    
    img = cv2.imdecode(imgNp, -1)
    img_resize = cv2.resize(img,self.size_out)
    self.imgself = img_resize

class CameraSelf:
  imgself = None
  success = False
  size_out = (600, 400)
  cap = None
  def __init__(self, size_out = (600, 400)):
    self.size_out = size_out
    self.cap = cv2.VideoCapture(0)
  def updateFrame(self):
    self.success, img = self.cap.read()
    img_resize = cv2.resize(img,self.size_out)
    self.imgself = img_resize