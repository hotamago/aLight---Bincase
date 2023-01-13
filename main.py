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

"""
Function main process
"""
def RunProjector():
  y, size_line, speedRender = 1, 30, 30

  projector = Projector(fullscreensize)

  def update_frame(y, size_line, speedRender):
    projector.canvas.delete("all")
    # projector.canvas.create_rectangle(0,0,projector.screen_width,projector.screen_height, fill="white")
    y += speedRender
    if y + size_line >= projector.screen_height:
      y = 2
    projector.canvas.create_rectangle(1,y,projector.screen_width,y + size_line, fill="white")

    projector.canvas.update_idletasks()
    #projector.canvas.after(10)
    projector.root.after(0, update_frame)

  update_frame(y, size_line, speedRender)

  #projector.root.attributes('-fullscreen', True)
  projector.root.mainloop()

def sub1():
  global size_window, fullscreensize
  """
  Init object
  """
  ### Init camera ###
  if on_cam1:
    # camera1 = CameraWebIP("http://192.168.137.190:8080/shot.jpg", size_window)
    camera1 = CameraSelf(size_window, 100, 0)
    camera1.is_flip = True
    camera1.flip_mode = -1
  if on_cam2:
    camera2 = CameraWebIP("http://192.168.137.10:8080/shot.jpg", size_window)

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

  """
  Loop frame
  """
  FPP = 5
  curFPP = 0
  while True:
    """
    Drop frame
    """
    curFPP += 1
    if curFPP < FPP:
      continue
    else:
      curFPP = 0

    """
    Update frame
    """
    if on_cam1:
      camera1.updateFrame()
    if on_cam2:
      camera2.updateFrame()

    ### Variable frame to image ###
    if on_cam1:
      imgCam1 = camera1.imgself
    if on_cam2:
      imgCam2 = camera2.imgself
      #imgCam2 = camera1.imgself

    """
    Auto detect corners mode
    """
    if not is_detect_corners:
      showQRcorners()
      is_detect_corners_1, maCam1, maCam1YXZ = get4Corners(imgCam1, lambda x: (x[0], x[2], x[1], x[3]))
      is_detect_corners_2, maCam2, maCam2YXZ = get4Corners(imgCam2, lambda x: (x[0], x[2], x[1], x[3]))

      if is_detect_corners_1 and is_detect_corners_2:
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

        q = cv2.waitKey(1)
        if q == ord('q'):
          break
        continue

      """
      Camera 1: Rasberry Pi Camera
      """
      contoursFigue_cam1 = []
      if on_cam1:
        contoursFigue_cam1 = auto_ProcessImage(imgCam1, maCam1YXZ, gamma1, fillCam1_01, noseCam1, on_show_cam1, on_cam1Hsv, "Camera test 1", "Camera 1 test hsv")

      """
      Camera 2: Lan camera
      """
      contoursFigue_cam2 = []
      if on_cam2:
        contoursFigue_cam2 = auto_ProcessImage(imgCam2, maCam2YXZ, gamma2, fillCam2_01, noseCam2, on_show_cam2, on_cam2Hsv, "Camera test 2", "Camera 2 test hsv")
      
      """
      Process, Caculate point
      """
      list_5_bestest_hull_point = []
      if len(contoursFigue_cam1) > 0:
        list_highest_point_hull = contoursFigue_cam1.reshape((contoursFigue_cam1.shape[0], -1, 2)).max(axis = 1, where=[False, True])
        # list_highest_point_hull = []
        # for hulls in contoursFigue_cam1:
        #   highest_point_hull = max(hulls, key=lambda x: x[0][1])
        #   list_highest_point_hull.append(highest_point_hull[0])

        list_highest_point_hull.sort(key=lambda x: -x[1])
        list_5_bestest_hull_point = list_highest_point_hull[:n_points_touch] + delta_Point

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
          cntNear = kdtree.query_radius(contourF, r=maxRadiusFigueWithFigueShallow, count_only=True)
          # for contourFS in np_contours:
          #   di = math.sqrt(math.pow(contourF[0] - contourFS[0], 2) + math.pow(contourF[1] - contourFS[1], 2))
          #   if di <= maxRadiusFigueWithFigueShallow:
          #     cntNear += 1
          valueCntNear[index_contourF].addPrev(cntNear)
          cntArgvanNear = valueCntNear[index_contourF].getAverage()
          if cntArgvanNear > deltaContoursClicked:
            isClickedPoints[index_contourF] = True
            isClicked = True
          index_contourF += 1
      
      """
      Mode: Black points touch screen
      """
      if on_black_points_touch_screen:
        maxRadiusFigueContour = 10
        # imgFigueDraw = np.copy(imgCamFTI)
        imgFigueDraw = np.zeros((size_window[1], size_window[0], 3))
        index_contourF = 0
        for point in list_5_bestest_hull_point:
          if isClickedPoints[index_contourF]:
            cv2.circle(imgFigueDraw, point, maxRadiusFigueContour, (0,0,255), -1, cv2.LINE_AA)
          else:
            cv2.circle(imgFigueDraw, point, maxRadiusFigueContour, (0,255,0), -1, cv2.LINE_AA)
          index_contourF += 1
        imgFigueDraw = cv2.resize(imgFigueDraw, fullscreensize)
        setFullScreenCV("Black points touch screen")
        cv2.imshow("Black points touch screen", imgFigueDraw)

      """
      Process UI, Control mouse or touchscreen
      """
      if on_cam1 and on_cam2 and on_controller:
        if len(list_5_bestest_hull_point) > 0:
          width, height = pyautogui.size()
          pointMouseNow = list_5_bestest_hull_point[0]
          mouseComputer = (int(pointMouseNow[0]*width/size_window[0]), int(pointMouseNow[1]*height/size_window[1]))

          if mouseComputer >= (0, 0):
            mousePos.add(mouseComputer)
            mouse.position = mousePos.getAverage()
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
    Exit action
    """
    q = cv2.waitKey(1)
    if q == ord('q'):
      break

"""
Change between sub programing
"""
def runCamera():
  sub1() 

"""
Multi thead
"""
def RunMultiThead(taskRunner = (True, True)):
  if taskRunner[0]:
    t1 = threading.Thread(target=RunProjector, args=())
  if taskRunner[1]:
    t2 = threading.Thread(target=runCamera, args=())

  if taskRunner[0]:
    t1.start()
  if taskRunner[1]:
    t2.start()

  if taskRunner[0]:
    t1.join()
  if taskRunner[1]:
    t2.join()

RunMultiThead((False, True))
