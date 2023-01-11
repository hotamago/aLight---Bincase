import math
import cv2
import numpy as np
from mathB import MatrixBincase
from projector import Projector
from camera import CameraWebIP, CameraSelf
# from detectB import DetectHander
from imageProcess import ImageProcessor
import logging
import threading
import time

import pyautogui
from pynput.mouse import Button, Controller

### Constant and init object ###
# 4, 8, 12, 16, 20
# 8, 12, 16
# detectHander = DetectHander([8])
matrixBincase = MatrixBincase()
imageProcesser = ImageProcessor()
mouse = Controller()

fullscreensize = (1024, 700)
size_window = (640, 480)

### Support function ###
mouseX, mouseY = 0,0
list4Points = []
def onMouse(event, x, y, flags, param):
  global mouseX, mouseY, list4Points
  mouseX, mouseY = x,y
  if event == cv2.EVENT_LBUTTONDOWN:
    print('pos(x,y) = (', mouseX, ",", mouseY, ')',sep='')
    hsv_color = imageProcesser.get_hsv_pos(param[0], param[1],(mouseY, mouseX))
    print('hsv = (', hsv_color[0],",", hsv_color[1],",", hsv_color[2] , ')',sep='')

    list4Points.append((mouseX, mouseY))

    if len(list4Points) >= 4:
      print('(', end = '', sep='')
      for i in range(0, 4):
        print('(', list4Points[i][0], ',', list4Points[i][1], ')', end = '', sep='')
        if i<3:
          print(',', end = '', sep='')
      print(')')
      list4Points.clear()

def auto_ProcessImage(imgCam, maCamYXZ, gamma, fillCam_01, noseCam,on_show_cam, on_camHsv, title_on_show_cam, title_on_camHsv):
  ### Process image: Perspective, filter_color, filter_noise, findContours ###
  imgCamFTI = matrixBincase.fast_tranform_image_opencv(imgCam, maCamYXZ, size_window)
  imgFigue = imageProcesser.filter_Color(imgCamFTI, gamma, fillCam_01[0], fillCam_01[1])
  imgFigue = imageProcesser.image_noise_filter(imgFigue, cv2.MORPH_CLOSE, noseCam[0])
  imgFigue = imageProcesser.image_noise_filter(imgFigue, cv2.MORPH_OPEN, noseCam[1])
  contoursFigue, hierarchyFigue = cv2.findContours(imgFigue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  
  ### Debug mode ###
  if on_show_cam:
    imgFigueDraw = cv2.cvtColor(imgFigue, cv2.COLOR_GRAY2RGB)
    cv2.imshow(title_on_show_cam, imgFigueDraw)
    cv2.setMouseCallback(title_on_show_cam, onMouse, param = (imgCam, gamma))
  if on_camHsv:
    #imgCamDraw = imageProcesser.get_hsv_image(np.copy(imgCamFTI), gamma)
    imgCamDraw = np.copy(imgCamFTI)
    cv2.imshow(title_on_camHsv, imgCamDraw)
    cv2.setMouseCallback(title_on_camHsv, onMouse, param = (imgCamFTI, gamma))
  
  return contoursFigue

### Main function ###
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
  global mouseX, mouseY, size_window, fullscreensize

  ### Mode ###
  on_cam1 = True
  on_cam2 = False
  on_cam1Hsv = True
  on_cam2Hsv = False
  on_config = False

  on_show_cam1 = True
  on_show_cam2 = False
  on_controller = False

  on_black_points_touch_screen = True

  ### Init camera ###
  if on_cam1:
    # camera1 = CameraWebIP("http://192.168.137.190:8080/shot.jpg", size_window)
    camera1 = CameraSelf(size_window, 100, 0)
    camera1.is_flip = True
    camera1.flip_mode = -1
  if on_cam2:
    camera2 = CameraWebIP("http://192.168.137.57:8080/shot.jpg", size_window)

  ### Config ###
  gamma1 = 0.7
  gamma2 = 0.7

  noseCam1 = ((3, 3), (5, 5))
  noseCam2 = ((3, 3), (5, 5))

  fillCam1_01 = [(0, 90, 10), (35, 190, 150)]
  fillCam2_01 = [(0, 90, 10), (35, 190, 150)]

  maCam1 = ((133,86), (522,82), (110,386), (548,386))
  maCam1YXZ = (maCam1[0], maCam1[2], maCam1[1], maCam1[3])

  maCam2 = ((106,80), (460,82), (96,351), (466,350))
  maCam2YXZ = (maCam2[0], maCam2[2], maCam2[1], maCam2[3])

  mouseComputer_old = (0, 0)

  maxFamesClicked = 5
  curFamesClicked = 0
  
  delta_Point = (0, 0)
  n_points_touch = 1
  deltaContoursClicked = 8
  maxRadiusFigueWithFigueShallow = 12
  numEleArgvan = 8

  speed_smooth = 6

  ### Smooth system ###
  cntListNear = [[0] * numEleArgvan] * n_points_touch
  indexAgven = [0] * n_points_touch

  ### Run process frame ###
  while True:
    ### Update frame ###
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

    ### Config mode ###
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

    ### Camera 1: Rasberry Pi Camera ###
    contoursFigue_cam1 = []
    if on_cam1:
      ### Format variable ###
      imgCam, maCamYXZ, gamma, fillCam_01, noseCam = imgCam1, maCam1YXZ, gamma1, fillCam1_01, noseCam1
      on_show_cam, on_camHsv = on_show_cam1, on_cam1Hsv
      title_on_show_cam, title_on_camHsv = "Camera test 1", "Camera 1 test hsv"

      contoursFigue_cam1 = auto_ProcessImage(imgCam, maCamYXZ, gamma, fillCam_01, noseCam, on_show_cam, on_camHsv, title_on_show_cam, title_on_camHsv)

    ### Camera 2: Lan camera ###
    contoursFigue_cam2 = []
    if on_cam2:
      ### Format variable ###
      imgCam, maCamYXZ, gamma, fillCam_01, noseCam = imgCam2, maCam2YXZ, gamma2, fillCam2_01, noseCam2
      on_show_cam, on_camHsv = on_show_cam2, on_cam2Hsv
      title_on_show_cam, title_on_camHsv = "Camera test 2", "Camera 2 test hsv"

      contoursFigue_cam2 = auto_ProcessImage(imgCam, maCamYXZ, gamma, fillCam_01, noseCam, on_show_cam, on_camHsv, title_on_show_cam, title_on_camHsv)
    
    ### Process, Caculate point ###
    if len(contoursFigue_cam1) > 0:
      list_highest_point_hull = []
      for hulls in contoursFigue_cam1:
        highest_point_hull = max(hulls, key=lambda x: x[0][1])
        list_highest_point_hull.append(highest_point_hull[0])

      list_highest_point_hull.sort(key=lambda x: -x[1])
      list_5_bestest_hull_point = []
      cnt_5_bestest_hull_point = n_points_touch
      for point in list_highest_point_hull:
        list_5_bestest_hull_point.append(point + delta_Point)
        cnt_5_bestest_hull_point-=1
        if cnt_5_bestest_hull_point <= 0:
          break

    ### Check clicked points touch ###
    isClicked = False
    isClickedPoints = [False] * len(list_5_bestest_hull_point)

    for i in range(0, n_points_touch):
      cntListNear[i][indexAgven[i]] = 0
      indexAgven[i] = (indexAgven[i] + 1) % numEleArgvan

    if len(contoursFigue_cam2) > 0:
      np_contours = np.vstack(contoursFigue_cam2).reshape(-1, 2)
      index_contourF = 0
      for contourF in list_5_bestest_hull_point:
        cntNear = 0
        for contourFS in np_contours:
          di = math.sqrt(math.pow(contourF[0] - contourFS[0], 2) + math.pow(contourF[1] - contourFS[1], 2))
          if di <= maxRadiusFigueWithFigueShallow:
            cntNear += 1
        cntListNear[index_contourF][(indexAgven[index_contourF] - 1 + numEleArgvan) % numEleArgvan] = cntNear
        cntArgvanNear = np.sum(np.array(cntListNear[index_contourF]))/numEleArgvan
        if cntArgvanNear > deltaContoursClicked:
          isClickedPoints[index_contourF] = True
          isClicked = True
          # print("clicked - ", np_contours.shape[0])
        index_contourF += 1
    
    ### Mode: Black points touch screen ###
    if on_black_points_touch_screen:
      maxRadiusFigueContour = 10
      # imgFigueDraw = np.copy(imgCamFTI)
      imgFigueDraw = np.zeros((size_window[0], size_window[1], 3))
      index_contourF = 0
      for point in list_5_bestest_hull_point:
        if isClickedPoints[index_contourF]:
          cv2.circle(imgFigueDraw, point, maxRadiusFigueContour, (0,0,255), -1, cv2.LINE_AA)
        else:
          cv2.circle(imgFigueDraw, point, maxRadiusFigueContour, (0,255,0), -1, cv2.LINE_AA)
        index_contourF += 1
      imgFigueDraw = cv2.resize(imgFigueDraw, fullscreensize)
      cv2.imshow("Black points touch screen", imgFigueDraw)
    
    ### Smooth frame clicked ###
    # if curFamesClicked == 0:
    #   curFamesClicked-=1
    #   mouse.click(Button.left, 2)
    #   # mouse.release(Button.left)
    # else:
    #   curFamesClicked-=1

    ### Process UI, Control mouse or touchscreen ###
    if on_cam1 and on_cam2 and on_controller:
      if len(list_5_bestest_hull_point) > 0:
        width, height = pyautogui.size()
        pointMouseNow = list_5_bestest_hull_point[0]
        mouseComputer = (int(pointMouseNow[0]*width/size_window[0]), int(pointMouseNow[1]*height/size_window[1]))

        if mouseComputer[0] > 0 and mouseComputer[1] > 0:
          length = math.sqrt(pow(mouseComputer[0] - mouseComputer_old[0],2) + pow(mouseComputer[1] - mouseComputer_old[1],2))

          velocityX = (mouseComputer[0] - mouseComputer_old[0]) / (length+1) * speed_smooth
          velocityY = (mouseComputer[1] - mouseComputer_old[1]) / (length+1) * speed_smooth

          mouse.position = (mouseComputer[0] + velocityX, mouseComputer[1] + velocityY)
          # # mouse.move(velocityX, velocityY)
          if isClicked:
          #   # Press and release
          #   # mouse.press(Button.left)
            mouse.click(Button.left)
            curFamesClicked = maxFamesClicked

          #   # Double click; this is different from pressing and releasing
          #   # twice on macOS
          #   mouse.click(Button.left, 2)

          #   # Scroll two steps down
          #   mouse.scroll(0, 2)

          mouseComputer_old = mouse.position

    ### Exit action ###
    q = cv2.waitKey(1)
    if q == ord('q'):
      break

### Change between sub programing ###
def runCamera():
  sub1() 

### Multi thead ###
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