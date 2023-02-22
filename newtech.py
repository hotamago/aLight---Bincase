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

from sklearn.neighbors import KDTree

"""
Bincase library
"""
from module.mathB import MatrixBincase
from module.projector import Projector
from module.camera import CameraWebIP, CameraSelf
# from module.detectB import DetectHander
from module.imageProcess import ImageProcessor
from module.qrcodeB import QRCodeB

from config.main import *
from constant.main import *
from supportFun.main import *

import module.smoothB as smoothB
import module.patternMakerB as patternMakerB
import module.calibrateCameraB as calibrationB

"""
Init object
"""
# 4, 8, 12, 16, 20
# 8, 12, 16
# detectHander = DetectHander([8])

mouse = Controller()
matrixBincase = MatrixBincase()
imageProcesser = ImageProcessor()
calibration = calibrationB.Calibration(size_chess, num_image_cal)

np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)

### Init camera ###
if on_cam1:
  # camera1 = CameraSelf(size_window, cam1_exposure, cam1_exposure_auto, fps_cam1)
  # camera1.is_flip = is_cam1_flip
  # camera1.flip_mode = cam1_flip_mode
  camera1 = CameraWebIP("http://192.168.137.217:8080/shot.jpg", size_window)

pm1 = patternMakerB.PatternMaker(size_chess[0]+1, size_chess[1]+1, fullscreensize[0], fullscreensize[1], corner_chess_size)
pm1.make_checkerboard_pattern()
pm2 = patternMakerB.PatternMaker(size_chess[0]+1, size_chess[1]+1, fullscreensize[0], fullscreensize[1], corner_chess_size)
pm2.make_circle_pattern(radius_c_chess)
imgPattern = pm1.get()
imgPatternCorner = pm2.get()

"""
Function main process
"""
def main_process():
  global size_window, fullscreensize
  
  camera1.startTheard()

  """
  Status system
  """
  # Matrix screen
  maCam1 = ((0,0), (0,0), (0,0), (0,0))
  maCam1YXZ = (maCam1[0], maCam1[2], maCam1[1], maCam1[3])
  
  # Case status
  is_detect_corners = False

  # Event mouse
  mousePos = smoothB.average_vecN_smooth(numAverageMouseMove)
  is_mouse_time_start = False
  mouse_time_start = 0

  ### Smooth system ###
  valueCntNear = [smoothB.average_smooth(numEleArgvan)] * n_points_touch
  old_clicked = False
  old_right_clicked = False
  
  ### FPS system ###
  start_time = time.time()
  everyX = 1 # displays the frame rate every 1 second
  counterFrame = 0
  
  """
  Loop frame
  """
  FPP = FramePerProcess
  curFPP = 0
  while True:
    """
    Count FPS
    """
    counterFrame+=1
    if (time.time() - start_time) > everyX :
      if show_FPS_console:
        print("FPS: ", counterFrame / (time.time() - start_time))
      counterFrame = 0
      start_time = time.time()
      
    """
    Exit action
    """
    q = cv2.waitKey(1)
    if q == ord('q') or camera1.stopped:
      camera1.stop()
      break
    
    """
    Drop frame
    """
    curFPP += 1
    if curFPP < FPP:
      continue
    else:
      curFPP = 0

    ### Variable frame to image ###
    if on_cam1:
      imgCam1 = camera1.getFrame()

    # cv2.imshow("Camera test 1", imgCam1)
    # cv2.setMouseCallback("Camera test 1", onMouse, param = (imgCam1, gamma1))

    if calibration.done:
      mtx, dist, newcameramtx, roi = calibration.get()
      imgCam1 = imageProcesser.undistort(imgCam1, mtx, dist, newcameramtx, roi)

    if not is_detect_corners:
      if not calibration.done:
        setFullScreenCV("imgPattern")
        cv2.imshow("imgPattern", imgPattern)
        calibration.add(imgCam1)
        if calibration.done:
          cv2.destroyAllWindows()
      else:
        setFullScreenCV("imgPattern")
        cv2.imshow("imgPattern", imgPatternCorner)

        gray = cv2.cvtColor(imgCam1, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
        if (circles is not None):
          circles = np.uint16(np.around(circles))
          for i in circles[0,:]:
            cv2.circle(gray, (i[0], i[1]), i[2], (0, 255, 0), 2)
        cv2.imshow("Camera test 1", gray)

        is_detect_corners_1, maCam1, maCam1YXZ = get4Corners_circle(imgCam1, lambda x: (x[0], x[2], x[1], x[3]), minDist, param1, param2, minRadius, maxRadius, (0, 0))
        if is_detect_corners_1:
          is_detect_corners = True
          cv2.destroyAllWindows()
    else:
      imgCamFTI = matrixBincase.fast_tranform_image_opencv(imgCam1, maCam1YXZ, size_window)
      cv2.imshow("Camera test 1", imgCamFTI)
      myScreenshot = pyautogui.screenshot()
      cv_myScreenshot = cv2.resize(cv2.cvtColor(np.array(myScreenshot), cv2.COLOR_RGB2BGR), size_window)
      cv2.imshow("Camera test 2", cv_myScreenshot)

      # compute difference
      difference = cv2.subtract(cv_myScreenshot, imgCamFTI)
      Conv_hsv_Gray = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)

      cv2.imshow("Camera diff", Conv_hsv_Gray)


"""
Run function main
"""
main_process()
