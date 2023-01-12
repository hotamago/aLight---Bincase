"""
Open library
"""
import math
import cv2
import numpy as np
import logging
import threading
import time
# from data_struct.kd_tree import KdTree
import pyautogui
from pynput.mouse import Button, Controller

from pyzbar.pyzbar import decode as detectAndDecodeQR
from pyzbar.pyzbar import ZBarSymbol

"""
Bincase library
"""
from module.mathB import MatrixBincase
from module.projector import Projector
from module.camera import CameraWebIP, CameraSelf
# from module.detectB import DetectHander
from module.imageProcess import ImageProcessor
from module.qrcodeB import QRCodeB

"""
Init object
"""
# 4, 8, 12, 16, 20
# 8, 12, 16
# detectHander = DetectHander([8])

mouse = Controller()
matrixBincase = MatrixBincase()
imageProcesser = ImageProcessor()
detectQR = cv2.QRCodeDetector()
qr = QRCodeB(version=1, box_size=8, border=2)

"""
Init constant
"""
from constant.main import *

"""
Function main process
"""
def sub1():
  global size_window
  """
  Init object
  """
  camera = CameraSelf(size_window, 60, 10)
  camera.is_flip = True
  camera.flip_mode = -1
  """
  Config system
  """

  """
  Status system
  """
  # Matrix screen
  maCam = ((0, 0), (0, 0), (0, 0), (0, 0))
  maCamYXZ = (maCam[0], maCam[2], maCam[1], maCam[3])
  
  # Case status
  is_detect_corners = False

  """
  Loop frame
  """
  while True:
    """
    Update frame
    """
    camera.updateFrame()
    imgCam = camera.imgself
    
    """
    Process
    """
    if not is_detect_corners:
      """
      Show QR code corners
      """
      imgQRcorners = qr.given_image_corners_qr(fullscreensize, core_value_qr)
      cv2.namedWindow("imgQRcorners", cv2.WND_PROP_FULLSCREEN)
      cv2.setWindowProperty("imgQRcorners", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
      cv2.imshow("imgQRcorners", imgQRcorners)

      """
      Detect corners by QR
      """
      list_is_detect_corners = [False] * 4
      maCam_beta = [[0, 0]] * 4
      
      grey = cv2.cvtColor(imgCam, cv2.COLOR_BGR2GRAY)
      height, width = imgCam.shape[:2]
      values = detectAndDecodeQR((grey.tobytes(), width, height), symbols=[ZBarSymbol.QRCODE])
      if len(values) > 0:
        for value in values:
          qr_value = value.data.decode()
          points4 = list(map(lambda point: (point.x, point.y), value.polygon))
          if qr_value in set_detect_value_qr:
            index_a = set_detect_value_qr.index(qr_value)
            list_is_detect_corners[index_a] = True
            array_get_corner_qr[index_a](points4)
            maCam_beta[index_a] = array_get_corner_qr[index_a](points4)
      
      # cv2.imshow("imgCam", imgCam)
      # print(list_is_detect_corners)
      
      if list_is_detect_corners.count(True) == 4:
        is_detect_corners = True
      if is_detect_corners:
        maCam = tuple(maCam_beta)
        maCamYXZ = (maCam[0], maCam[2], maCam[1], maCam[3])
        cv2.destroyWindow("imgQRcorners")
    else:
      """
      Run main programing
      """
      imgCamDraw = np.copy(imgCam)
      matrixBincase.draw_line(imgCamDraw, maCamYXZ[0], maCamYXZ[1], maCamYXZ[2], maCamYXZ[3], 1)
      cv2.imshow("Camera test", imgCamDraw)

    """
    Press Q to exit loop
    """
    q = cv2.waitKey(1)
    if q == ord('q'):
      break

"""
Multi sub case
"""
def runCamera():
  sub1() 

# t1 = threading.Thread(target=RunProjector, args=())
# t1.start()
# t1.join()

"""
Run multi thread
"""
t2 = threading.Thread(target=runCamera, args=())
t2.start()
t2.join()
