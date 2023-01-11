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

"""
Bincase library
"""
from mathB import MatrixBincase
from projector import Projector
from camera import CameraWebIP, CameraSelf
# from detectB import DetectHander
from imageProcess import ImageProcessor
from qrcodeB import QRCodeB

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
qr = QRCodeB(version=1, box_size=6, border=1)

"""
Init constant
"""
# Screen
fullscreensize = (1024, 700)
size_window = (640, 480)
# QR
core_value_qr = "bin"
set_detect_value_qr = ["tl", "tr", "bl", "br"]
set_detect_value_qr = map(lambda x: core_value_qr + x, set_detect_value_qr)
# QR lambda
lambda_qr_t = lambda point: point[0]
lambda_qr_l = lambda point: point[1]
lambda_qr_b = lambda point: -point[0]
lambda_qr_r = lambda point: -point[1]
def get_corner_qr(list_points, cmp1, cmp2):
  list_points.sort(key=cmp1)
  list_points = [list_points[i] for i in range(2)]
  list_points.sort(key=cmp2)
  return list_points[0]
array_get_corner_qr = [
  lambda x: get_corner_qr(x, lambda_qr_t, lambda_qr_l),
  lambda x: get_corner_qr(x, lambda_qr_t, lambda_qr_r),
  lambda x: get_corner_qr(x, lambda_qr_b, lambda_qr_l),
  lambda x: get_corner_qr(x, lambda_qr_b, lambda_qr_r),
  ]

"""
Function main process
"""
def sub1():
  global size_window
  """
  Init object
  """
  camera = CameraSelf(size_window)
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
      # imgQRcorners = cv2.resize(imgQRcorners, fullscreensize)
      cv2.imshow("imgQRcorners", imgQRcorners)

      """
      Detect corners by QR
      """
      values, decoded_info, points, straight_qrcode = detectQR.detectAndDecodeMulti(imgCam)
      list_is_detect_corners = [False] * 4
      if (decoded_info is not None) and (points is not None):
        for qr_value, points4 in zip(decoded_info, points):
          if qr_value in set_detect_value_qr:
            index_a = set_detect_value_qr.index(qr_value)
            list_is_detect_corners[index_a] = True
            maCam[index_a] = array_get_corner_qr[index_a](points4)

      if list_is_detect_corners.count(True) == 4:
        is_detect_corners = True
      if is_detect_corners:
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