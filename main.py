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

from matplotlib import pyplot as plt

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
qr = QRCodeB(version=qr_version, box_size=qr_box_size, border=qr_border)
np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
stereo = cv2.StereoBM_create(numDisparities=numDisparitiesDepth, blockSize=blockSizeDepth)

### Init camera ###
if on_cam1:
  camera1 = CameraWebIP(urlcam1, size_window)
  # camera1 = CameraSelf(size_window, cam1_exposure, cam1_exposure_auto, fps_cam1)
  # camera1.is_flip = is_cam1_flip
  # camera1.flip_mode = cam1_flip_mode
if on_cam2:
  # camera2 = CameraWebIP(urlcam2, size_window)
  camera2 = CameraSelf(size_window, cam2_exposure, cam2_exposure_auto, fps_cam2)
  camera2.is_flip = is_cam2_flip
  camera2.flip_mode = cam2_flip_mode

"""
Function main process
"""
def main_process():
  global size_window, fullscreensize
  
  if on_cam1:
    camera1.startTheard()
  if on_cam2:
    camera2.startTheard()
  
  """
  Status system
  """
  # Matrix screen
  maCam1 = ((0,0), (0,0), (0,0), (0,0))
  maCam1YXZ = (maCam1[0], maCam1[2], maCam1[1], maCam1[3])

  maCam2 = ((0,0), (0,0), (0,0), (0,0))
  maCam2YXZ = (maCam2[0], maCam2[2], maCam2[1], maCam2[3])
  
  # Case status
  is_detect_corners = False

  # Event mouse
  mousePos = smoothB.average_vecN_smooth(numAverageMouseMove)

  ### Smooth system ###
  valueCntNear = [smoothB.average_smooth(numEleArgvan)] * n_points_touch
  
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
    if q == ord('q') or (on_cam1 and camera1.stopped) or (on_cam2 and camera2.stopped):
      if on_cam1:
        camera1.stop()
      if on_cam2:
        camera2.stop()
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
    if on_cam2:
      imgCam2 = camera2.getFrame()
      #imgCam2 = camera1.imgself
    
    """
    Debug
    """
    if on_debug:
      if on_cam1:
        cv2.imshow("Camera test 1", imgCam1)
        cv2.setMouseCallback("Camera test 1", onMouse, param = (imgCam1, gamma1))
      
      if on_cam2:
        cv2.imshow("Camera test 2", imgCam2)
        cv2.setMouseCallback("Camera test 2", onMouse, param = (imgCam2, gamma2))
      continue

    """
    Auto detect corners mode
    """
    if not is_detect_corners:
      showQRcorners()
      is_detect_corners_1, is_detect_corners_2 = False, False
      if on_cam1:
        is_detect_corners_1, maCam1, maCam1YXZ = get4Corners(imgCam1, lambda x: (x[0], x[2], x[1], x[3]))
      if on_cam2:
        is_detect_corners_2, maCam2, maCam2YXZ = get4Corners(imgCam2, lambda x: (x[0], x[2], x[1], x[3]))

      if (is_detect_corners_1 or not on_cam1) and (is_detect_corners_2 or not on_cam2):
        is_detect_corners = True
        destroyQRcorners()
    else:
      """
      Config mode
      """
      if on_config:
        if on_cam1:
          imgCam1Draw = np.copy(imgCam1)
          matrixBincase.draw_line(imgCam1Draw, maCam1YXZ[0], maCam1YXZ[1], maCam1YXZ[2], maCam1YXZ[3], 3)
          # detectHander.draw_circle_hands(imgCam1Draw, res1)
          cv2.imshow("Camera test 1", imgCam1Draw)
          cv2.setMouseCallback("Camera test 1", onMouse, param = (imgCam1, gamma1))
        
        if on_cam2:
          imgCam2Draw = np.copy(imgCam2)
          matrixBincase.draw_line(imgCam2Draw, maCam2YXZ[0], maCam2YXZ[1], maCam2YXZ[2], maCam2YXZ[3], 3)
          # detectHander.draw_circle_hands(imgCam2Draw, res2)
          cv2.imshow("Camera test 2", imgCam2Draw)
          cv2.setMouseCallback("Camera test 2", onMouse, param = (imgCam2, gamma2))

        continue

      """
      Camera 1: Lan camera
      """
      contoursFigue_cam1 = []
      if on_cam1:
        contoursFigue_cam1 = auto_ProcessImage(imgCam1, maCam1YXZ, gamma1, fillCam1_01, noseCam1, on_show_cam1, on_cam1Hsv, on_cam1Ycbcr, on_cam1FTI, "Camera test 1")

      """
      Camera 2: Rasberry Pi Camera
      """
      contoursFigue_cam2 = []
      if on_cam2:
        contoursFigue_cam2 = auto_ProcessImage(imgCam2, maCam2YXZ, gamma2, fillCam2_01, noseCam2, on_show_cam2, on_cam2Hsv, on_cam2Ycbcr, on_cam2FTI, "Camera test 2")
      
      """
      Only for 2 cam activate
      """
      if (not on_cam1) or (not on_cam2):
        continue
      
      imgCamFTI1 = auto_ProcessImage_onlyfti(imgCam1, maCam1YXZ) #, gamma1, fillCam1_01, noseCam1)
      imgCamFTI2 = auto_ProcessImage_onlyfti(imgCam2, maCam2YXZ) #, gamma2, fillCam2_01, noseCam2)
      
      imgCamFTI1Mask = auto_ProcessImage_onlyhand(imgCam1, maCam1YXZ, gamma1, fillCam1_01, noseCam1)
      imgCamFTI2Mask = auto_ProcessImage_onlyhand(imgCam2, maCam2YXZ, gamma2, fillCam2_01, noseCam2)
      
      imgCamFTI1gray = cv2.cvtColor(imgCamFTI1, cv2.COLOR_BGR2GRAY)
      imgCamFTI2gray = cv2.cvtColor(imgCamFTI2, cv2.COLOR_BGR2GRAY)
      
      res1 = cv2.bitwise_and(imgCamFTI1gray, imgCamFTI1gray, mask=imgCamFTI1Mask)
      res2 = cv2.bitwise_and(imgCamFTI2gray, imgCamFTI2gray, mask=imgCamFTI2Mask)
      
      kernel = np.ones((3, 3), np.float32)/9
      res1 = cv2.filter2D(res1, -1, kernel)
      res2 = cv2.filter2D(res2, -1, kernel)
      
      disparity = stereo.compute(res1, res2)
      norm_disparity = cv2.normalize(disparity, None, 10, 245, cv2.NORM_MINMAX)
      color_disparity = cv2.applyColorMap(norm_disparity.astype(np.uint8), cv2.COLORMAP_HSV)
      bul_map = cv2.addWeighted(res1, 0.5, res2, 0.5, 0)
      cv2.imshow("Debug 1", color_disparity)
      cv2.imshow("Debug 2", bul_map)
      
      """
      Process, Caculate point
      """
      list_5_bestest_hull_point = []
      if len(contoursFigue_cam1) > 0:
        list_highest_point_hull = []
        for hulls in contoursFigue_cam1:
          highest_point_hull = max(hulls, key=lambda x: x[0][1])
          list_highest_point_hull.append(highest_point_hull[0])
        list_highest_point_hull.sort(key=lambda x: -x[1])
        cnt_5_bestest_hull_point = n_points_touch
        for point in list_highest_point_hull:
          list_5_bestest_hull_point.append(point + delta_Point)
          cnt_5_bestest_hull_point-=1
          if cnt_5_bestest_hull_point <= 0:
            break
        """
        arr = np.array(contoursFigue_cam1)
        if arr.ndim > 3:
          arr = arr.reshape((arr.shape[0], -1, 2))
          list_ele = arr.argmax(axis = 1)[0:,1]
          list_highest_point_hull = arr[np.arange(arr.shape[0]), list_ele]

          ind = list_highest_point_hull.argsort(axis = 0)[-n_points_touch:, 1]
          list_5_bestest_hull_point = list_highest_point_hull[ind]
          list_5_bestest_hull_point += delta_Point
          list_5_bestest_hull_point = tuple(list_5_bestest_hull_point)
        else:
          #print(contoursFigue_cam1)
          print(arr.shape)
          print(arr)
        """

      """
      Check clicked points touch
      """
      isClicked = False
      isClickedPoints = [False] * len(list_5_bestest_hull_point)

      for i in range(0, n_points_touch):
        valueCntNear[i].add(0)

      if len(contoursFigue_cam2) > 0:
        np_contours = np.vstack(contoursFigue_cam2).reshape(-1, 2)
        index_contourF = 0
        kdtree = KDTree(np_contours, leaf_size=2)

        for contourF in list_5_bestest_hull_point:
          cntNear = 0
          contourF = contourF.reshape(1, -1)
          cntNear = kdtree.query_radius(contourF, r=maxRadiusFigueWithFigueShallow, count_only=True)
          # for contourFS in np_contours:
          #   di = math.sqrt(math.pow(contourF[0] - contourFS[0], 2) + math.pow(contourF[1] - contourFS[1], 2))
          #   if di <= maxRadiusFigueWithFigueShallow:
          #     cntNear += 1
          valueCntNear[index_contourF].addPrev(cntNear)
          cntArgvanNear = valueCntNear[index_contourF].getAverage()
          if is_debug_clicked:
            print(cntArgvanNear)
          if cntArgvanNear > deltaContoursClicked:
            isClickedPoints[index_contourF] = True
            isClicked = True
          index_contourF += 1
      
      """
      Mode: Black points touch screen
      """
      if on_black_points_touch_screen:
        # imgFigueDraw = np.copy(imgCamFTI)
        imgFigueDraw = np.zeros((size_window[1], size_window[0], 3))
        index_contourF = 0
        for point in list_5_bestest_hull_point:
          if isClickedPoints[index_contourF]:
            cv2.circle(imgFigueDraw, point, maxRadiusFigueContour, color_clicked, -1, cv2.LINE_AA)
          else:
            cv2.circle(imgFigueDraw, point, maxRadiusFigueContour, color_nonClicked, -1, cv2.LINE_AA)
          index_contourF += 1
        imgFigueDraw = cv2.resize(imgFigueDraw, fullscreensize)
        if not is_debug_clicked:
          setFullScreenCV("Black points touch screen")
        cv2.imshow("Black points touch screen", imgFigueDraw)

      """
      Process UI, Control mouse or touchscreen
      """
      mousePos.add((0, 0))
      if on_cam1 and on_cam2 and on_controller:
        if len(list_5_bestest_hull_point) > 0:
          width, height = pyautogui.size()
          pointMouseNow = list_5_bestest_hull_point[0]
          if is_flip_mouse:
            mouseComputer = (int(pointMouseNow[0]*width/size_window[0]), int(pointMouseNow[1]*height/size_window[1]))
          else:
            mouseComputer = (int(width - pointMouseNow[0]*width/size_window[0]), int(height - pointMouseNow[1]*height/size_window[1]))

          if mouseComputer >= (0, 0):
            mousePos.addPrev(mouseComputer)
            mouse.position = mouseComputer
            # # mouse.move(velocityX, velocityY)
            if isClicked:
              # Press and release
              # mouse.press(Button.left)
              mouse.click(Button.left)

              # Double click
              # mouse.click(Button.left, 2)

              # Scroll two steps down
              # mouse.scroll(0, 2)
"""
Run function main
"""
main_process()
