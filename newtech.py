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
import module.screenshotB as screenshotB

"""
Init object
"""
# 4, 8, 12, 16, 20
# 8, 12, 16
# detectHander = DetectHander([8])

mouse = Controller()
matrixBincase = MatrixBincase()
imageProcesser = ImageProcessor()
pm1 = patternMakerB.PatternMaker(size_chess, fullscreensize[0], fullscreensize[1], corner_chess_size)
pm1.make_checkerboard_pattern()
cvt_c = pm1.get_size_chess()
print("Chess size: ", cvt_c)
calibration = calibrationB.Calibration(cvt_c, num_image_cal)
# ~ screenshotB = screenshotB.ScreenshotB(size_window)

detectQR = cv2.QRCodeDetector()
qr = QRCodeB(version=qr_version, box_size=qr_box_size, border=qr_border)

np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)

### Init camera ###
if on_cam1:
  camera1 = CameraSelf(size_window, cam1_exposure, cam1_exposure_auto, fps_cam1)
  camera1.is_flip = is_cam1_flip
  camera1.flip_mode = cam1_flip_mode
  # camera1 = CameraWebIP("http://192.168.137.217:8080/shot.jpg", size_window)

imgPattern = pm1.get()

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
  
  maCam2 = ((0,0), (0,0), (0,0), (0,0))
  maCam2YXZ = (maCam1[0], maCam1[2], maCam1[1], maCam1[3])
  
  # Case status
  is_detect_corners = False
  is_detect_corners_1 = False
  is_detect_corners_2 = False

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
  
  ### Currunt system config ###
  # 0 = hand, 1 = pen
  mode_running = 0
  
  """
  Loop frame
  """
  FPP = FramePerProcess
  curFPP = 0
  while True:
    """
    Exit action
    """
    q = cv2.waitKey(1)
    # ~ if q == ord('q') or camera1.stopped or screenshotB.stopped:
    if q == ord('q') or camera1.stopped:
      camera1.stop()
      # ~ screenshotB.stop()
      break
    if q == ord('s'):
      mode_running ^= 1
      if mode_running == 0:
        print("switch to hand mode")
      elif mode_running == 1:
        print("switch to lazer mode")
      
    """
    Drop frame
    """
    curFPP += 1
    if curFPP < FPP:
      continue
    else:
      curFPP = 0
    
    """
    Count FPS
    """
    counterFrame+=1
    if (time.time() - start_time) > everyX :
      if show_FPS_console:
        print("FPS: ", counterFrame / (time.time() - start_time))
      counterFrame = 0
      start_time = time.time()

    ### Variable frame to image ###
    if on_cam1:
      imgCam1 = camera1.getFrame()

    # cv2.imshow("Camera test 1", imgCam1)
    # cv2.setMouseCallback("Camera test 1", onMouse, param = (imgCam1, gamma1))
    
    if is_detect_corners_1:
      imgCam1 = matrixBincase.fast_tranform_image_opencv(imgCam1, maCam1YXZ, size_window)
    if is_detect_corners_2:
      imgCam1 = matrixBincase.fast_tranform_image_opencv(imgCam1, maCam2YXZ, size_window)
      
    if calibration.done:
      mtx, dist, newcameramtx, roi = calibration.get()
      imgCam1 = imageProcesser.undistort(imgCam1, mtx, dist, newcameramtx, roi)

    if (not is_detect_corners) or (not calibration.done):
      gray = cv2.cvtColor(imgCam1, cv2.COLOR_BGR2GRAY)
      cv2.imshow("Camera test 1", gray)
      
      if not is_detect_corners_1:
        showQRcorners()
        is_detect_corners_1, maCam1, maCam1YXZ = get4Corners(imgCam1, lambda x: (x[0], x[2], x[1], x[3]), (20, 20))
        if is_detect_corners_1:
          cv2.destroyAllWindows()
      else:
          if not calibration.done:
            setFullScreenCV("imgPattern")
            cv2.imshow("imgPattern", imgPattern)
            calibration.add(imgCam1)
            if calibration.done:
              # ~ screenshotB.startTheard()
              cv2.destroyAllWindows()
          else:
            showQRcorners()
            is_detect_corners_2, maCam2, maCam2YXZ = get4Corners(imgCam1, lambda x: (x[0], x[2], x[1], x[3]))
              
            if is_detect_corners_2:
              is_detect_corners = True
              cv2.destroyAllWindows()
        
    else:
      """
      Process find interaction
      """
      if mode_running == 0: # Mode figue
        camera1.setExposure(cam1_exposure, cam1_exposure_auto)
        
        """
        Camera 1: camera
        """
        contoursFigue_cam1 = []
        if on_cam1:
          contoursFigue_cam1 = auto_ProcessImage_nofti(imgCam1, gamma1, fillCam1_01, noseCam1, on_show_cam1, on_cam1Hsv, on_cam1Ycbcr, on_cam1FTI, "Camera test 1")

      elif mode_running == 1: # Mode lazer pen
        camera1.setExposure(10, 1)
        
        """
        Camera 1: lazer
        """
        contoursFigue_cam1 = []
        if on_cam1:
          imgCam, maCamYXZ, gamma, fillCam_01, noseCam, on_show_cam, on_camHsv, on_camYcbcr, on_camFTI, title_on_show_cam = imgCam1, maCam1YXZ, gamma1, fillCam1_01, noseCam1, on_show_cam1, on_cam1Hsv, on_cam1Ycbcr, on_cam1FTI, "Camera test 1"
          
          imgCamFTI = np.copy(imgCam)
          imgFigue = cv2.inRange(imgCamFTI, (0, 0, 100), (255, 255, 255))
          
          # cv2.RETR_EXTERNAL - Get outside
          # cv2.RETR_LIST - Get all
          contoursFigue_cam1, hierarchyFigue = cv2.findContours(imgFigue, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
          ### Debug mode ###
          if on_show_cam:
            imgFigueDraw = cv2.cvtColor(imgFigue, cv2.COLOR_GRAY2RGB)
            cv2.imshow(title_on_show_cam, imgFigueDraw)
            cv2.setMouseCallback(title_on_show_cam, onMouse, param = (imgCam, gamma))
          if on_camHsv:
            imgCamDraw = imageProcesser.get_hsv_image(np.copy(imgCamFTI), gamma)
            cv2.imshow(title_on_show_cam + "Hsv", imgCamDraw)
            cv2.setMouseCallback(title_on_show_cam + "Hsv", onMouse, param = (imgCamFTI, gamma))
          if on_camYcbcr:
            imgCamDraw = imageProcesser.get_ycbcr_image(np.copy(imgCamFTI), gamma)
            cv2.imshow(title_on_show_cam + "Ycbcr", imgCamDraw)
            cv2.setMouseCallback(title_on_show_cam + "Ycbcr", onMouse, param = (imgCamFTI, gamma))
          if on_camFTI:
            imgCamDraw = np.copy(imgCamFTI)
            cv2.imshow(title_on_show_cam + "FTI", imgCamDraw)
            cv2.setMouseCallback(title_on_show_cam + "FTI", onMouse, param = (imgCamFTI, gamma))
      
      """
      Only for cams activate
      """
      if (not on_cam1):
        continue
      
      """
      Process, Caculate point
      """
      list_5_bestest_hull_point = []
      if len(contoursFigue_cam1) > 0:
        
        if mode_running == 0:
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
              
        elif mode_running == 1:
          cnt_5_bestest_hull_point = n_points_touch
          for hulls in contoursFigue_cam1:
            point = np.median(hulls, axis=0)[0]
            point.astype(int)
            list_5_bestest_hull_point.append((int(point[0] + delta_Point[0]), int(point[1] + delta_Point[1])))
            cnt_5_bestest_hull_point-=1
            if cnt_5_bestest_hull_point <= 0:
              break
        
      """
      Check clicked points touch
      """
      isClicked = True
      isClickedPoints = [True] * len(list_5_bestest_hull_point)
      
      """
      Mode: Black points touch screen
      """
      if on_black_points_touch_screen:
        # imgFigueDraw = np.copy(imgCamFTI)
        imgFigueDraw = np.zeros((size_window[1], size_window[0], 3))
        imgFigueDraw.fill(255)
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
      if on_cam1 and on_controller:
        if len(list_5_bestest_hull_point) > 0:
          # Time
          if not is_mouse_time_start:
            mouse_time_start = time.time()
            is_mouse_time_start = True
          
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
            if isClicked and (not old_clicked):
              # Press and release
              mouse.click(Button.left)

              # Double click
              # mouse.click(Button.left, 2)

              # Scroll two steps down
              # mouse.scroll(0, 2)
            elif isClicked and ((time.time() - mouse_time_start) > time_delay_press):
              mouse.press(Button.left)
              
          old_clicked = True
        else:
          if is_mouse_time_start:
            if ((time.time() - mouse_time_start) > time_delay_press):
              mouse.release(Button.left)
            
            if (not old_right_clicked) and ((time.time() - mouse_time_start) > time_delay_press and (time.time() - mouse_time_start) < time_delay_right_click):
              mouse.click(Button.right)
              old_right_clicked = True
              
            # mouse.position = (0, 0)
          
          old_clicked = False
          old_right_clicked = False
          is_mouse_time_start = False

"""
Run function main
"""
main_process()
