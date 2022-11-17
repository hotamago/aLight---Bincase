import math
import cv2
import numpy as np
from mathB import MatrixBincase
from projector import Projector
from camera import CameraWebIP, CameraSelf
from detectB import DetectHander
from imageProcess import ImageProcessor
import logging
import threading
import time

import pyautogui
from pynput.mouse import Button, Controller
mouse = Controller()

matrixBincase = MatrixBincase()
# 4, 8, 12, 16, 20
# 8, 12, 16
detectHander = DetectHander([8])
imageProcesser = ImageProcessor()

y = 1
size_line = 30
speedRender = 30

projector = 0
def RunProjector():
  global projector, y, size_line, projector
  projector = Projector()

  def update_frame():
    global y, size_line, projector 
    projector.canvas.delete("all")
    # projector.canvas.create_rectangle(1,y,projector.screen_width,y + size_line, fill="black")
    y += speedRender
    if y + size_line >= projector.screen_height:
      y = 2
    projector.canvas.create_rectangle(1,y,projector.screen_width,y + size_line, fill="white")
    projector.canvas.update_idletasks()
    # projector.canvas.after(0)
    projector.root.after(0, update_frame)

  update_frame()

  # projector.root.attributes('-fullscreen', True)
  projector.root.mainloop()

size_window = (800, 450)

mouseX, mouseY = 0,0
def onMouse(event, x, y, flags, param):
  global mouseX, mouseY
  mouseX, mouseY = x,y
  if event == cv2.EVENT_LBUTTONDOWN:
    print('pos(x,y) = (', mouseX, ",", mouseY, ')',sep='')
    hsv_color = imageProcesser.get_hsv_pos(param[0], param[1],(mouseY, mouseX))
    print('hsv = (', hsv_color[0],",", hsv_color[1],",", hsv_color[2] , ')',sep='')

def sub1():
  global mouseX, mouseY, size_window
  on_cam1 = True
  on_cam2 = True
  on_cam2Hsv = False
  on_config = False

  on_show_cam1 = False
  on_show_cam2 = False

  # camera1 = CameraSelf(size_window)
  if on_cam1:
    camera1 = CameraWebIP("http://192.168.137.190:8080/shot.jpg", size_window)
  if on_cam2:
    camera2 = CameraWebIP("http://192.168.137.112:8080/shot.jpg", size_window)

  gamma = 0.4
  gammaFingue = 0.7

  noseCam1 = ((5, 5), (15, 15))
  noseCam2 = ((5, 5), (10, 10))

  imgFigueColor = [(0, 100, 20), (20, 150, 120)]
  deltaContoursClicked = 150

  maCam1 = ((189,61), (613,55), (53,169), (734,158))
  maCam1YXZ = (maCam1[0], maCam1[2], maCam1[1], maCam1[3])

  maCam2 = ((211,357), (630,357), (12,414), (782,420))
  maCam2YXZ = (maCam2[0], maCam2[2], maCam2[1], maCam2[3])

  fillCam2_01 = [(0, 100, 10), (20, 180, 120)]
  isFillCam2_02 = False
  fillCam2_02 = [(150, 80, 85), (190, 150, 120)]

  mouseComputer_old = (0, 0)

  maxFamesClicked = 5
  curFamesClicked = 0

  while True:
    if on_cam1:
      camera1.updateFrame()
    if on_cam2:
      camera2.updateFrame()

    if on_cam1:
      imgCam1 = camera1.imgself
    if on_cam2:
      imgCam2 = camera2.imgself

    if on_config:
      imgCam1Draw = np.copy(imgCam1)
      matrixBincase.draw_line(imgCam1Draw, maCam1YXZ[0], maCam1YXZ[1], maCam1YXZ[2], maCam1YXZ[3], 3)
      # detectHander.draw_circle_hands(imgCam1Draw, res1)
      cv2.imshow("Camera test 1", imgCam1Draw)
      cv2.setMouseCallback("Camera test 1", onMouse, param = (imgCam1, gamma))

      imgCam2Draw = np.copy(imgCam2)
      matrixBincase.draw_line(imgCam2Draw, maCam2YXZ[0], maCam2YXZ[1], maCam2YXZ[2], maCam2YXZ[3], 3)
      # detectHander.draw_circle_hands(imgCam2Draw, res2)
      cv2.imshow("Camera test 2", imgCam2Draw)
      cv2.setMouseCallback("Camera test 2", onMouse, param = (imgCam2, gamma))
      
      q = cv2.waitKey(1)
      if q == ord('q'):
        break
      continue

    ### Camera test ###
    imgCamTest =  np.copy(imgCam2)
    matrixBincase.draw_line(imgCamTest, maCam2YXZ[0], maCam2YXZ[1], maCam2YXZ[2], maCam2YXZ[3], 3)
    # detectHander.draw_circle_hands(imgCamTest, res1)
    if on_show_cam1:
      cv2.imshow("Camera test 1", imgCamTest)
      cv2.setMouseCallback("Camera test 1", onMouse, param = (imgCam2, gamma))

    ### Camera 1: pos hand ###
    if on_cam1:
      # res1 = detectHander.process(imgCam1)

      # list_hands1 = detectHander.get_pos_hands(imgCam1, res1)
      # for i in range(len(list_hands1)):
      #   list_hands1[i] = matrixBincase.tramform_points(list_hands1[i], maCam1YXZ, size_window)
      #   list_hands1[i] += (0, 10)
      
      imgCam1FTI = matrixBincase.fast_tranform_image_opencv(imgCam1, maCam1YXZ, size_window)

      ### Check pos hand ###
      # for i in range(len(list_hands1)):
      #   cv2.circle(imgCam1FTI, list_hands1[i], 10, (255,0,0),-1)
      # cv2.imshow("Camera 1", imgCam1FTI)
      # cv2.setMouseCallback("Camera 1", onMouse, param = (imgCam1, gamma))

      # imgFigueShallowColor = [(5, 100, 20), (20, 200, 100)]
      imgFigue = imageProcesser.filter_Color(imgCam1FTI, gammaFingue, imgFigueColor[0], imgFigueColor[1])
      imgFigue = imageProcesser.image_noise_filter(imgFigue, cv2.MORPH_CLOSE, noseCam1[0])
      imgFigue = imageProcesser.image_noise_filter(imgFigue, cv2.MORPH_OPEN, noseCam1[0])
      contoursFigue, hierarchyFigue = cv2.findContours(imgFigue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      imgFigueDraw = cv2.cvtColor(imgFigue, cv2.COLOR_GRAY2RGB)
      # for i in range(len(list_pos_hands)):
      #   cv2.circle(imgFigue, list_pos_hands[i], 10, (255,0,0),-1)

      # hull_list = []
      # for i in range(len(contoursFigue)):
      #   hull = cv2.convexHull(contoursFigue[i])
      #   hull_list.append(hull)
      #   cv2.drawContours(imgFigueDraw, hull_list, i, color = (255,0,0), thickness = 5)

       ### Find fingue ###
      list_highest_point_hull = []
      # print(hull_list)
      for hulls in contoursFigue:
        highest_point_hull = max(hulls, key=lambda x: x[0][1])
        list_highest_point_hull.append(highest_point_hull[0])

      list_highest_point_hull.sort(key=lambda x: -x[1])
      list_5_bestest_hull_point = []
      cnt_5_bestest_hull_point = 1
      for point in list_highest_point_hull:
        list_5_bestest_hull_point.append(point + (0, 40))
        cnt_5_bestest_hull_point-=1
        if cnt_5_bestest_hull_point <= 0:
          break
      
      # cv2.drawContours(imgFigueDraw, contoursFigue, contourIdx = -1, color = (0,255,0), thickness = 3)
      # cv2.imshow("Camera figue", imgFigueDraw)

      # imgCam1Draw = imageProcesser.get_hsv_image(np.copy(imgCam1FTI), gamma)
      # # cv2.circle(imgCam2Draw, (mouseX, mouseY), 10, (255,0,0),-1)
      # cv2.imshow("Camera 1 test hsv", imgCam1Draw)
      # cv2.setMouseCallback("Camera 1 test hsv", onMouse, param = (imgCam1FTI, gamma))

    ### Camera 2: Check clicked ###
    if on_cam2:
      imgCam2FTI = matrixBincase.fast_tranform_image_opencv(imgCam2, maCam2YXZ, size_window)
      imgCam2Up = np.zeros_like(imgCam2FTI)

      imgCam2Up = imageProcesser.filter_Color(np.copy(imgCam2FTI), gamma, fillCam2_01[0], fillCam2_01[1])
      imgCam2Down = np.zeros_like(imgCam2Up)
      if isFillCam2_02:
        imgCam2Down = imageProcesser.filter_Color(np.copy(imgCam2FTI), gamma, fillCam2_02[0], fillCam2_02[1])
      imgCam2Hsv = cv2.add(imgCam2Up, imgCam2Down)
      imgCam2Hsv = imageProcesser.image_noise_filter(imgCam2Hsv, cv2.MORPH_CLOSE, noseCam2[0])
      imgCam2Hsv = imageProcesser.image_noise_filter(imgCam2Hsv, cv2.MORPH_OPEN, noseCam2[1])
      contours, hierarchy = cv2.findContours(imgCam2Hsv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

      if on_cam2Hsv:
        imgCam2Draw = imageProcesser.get_hsv_image(np.copy(imgCam2FTI), gamma)
        # cv2.circle(imgCam2Draw, (mouseX, mouseY), 10, (255,0,0),-1)
        cv2.imshow("Camera 2 test hsv", imgCam2Draw)
        cv2.setMouseCallback("Camera 2 test hsv", onMouse, param = (imgCam2FTI, gamma))

      isClicked = False

      if len(contours) > 0:
        np_contours = np.vstack(contours).squeeze()
        if np_contours.shape[0] > deltaContoursClicked:
          isClicked = True
          # print("clicked - ", np_contours.shape[0])

      imgCam2Hsv = cv2.cvtColor(imgCam2Hsv, cv2.COLOR_GRAY2BGR)
      cv2.drawContours(imgCam2Hsv, contours, contourIdx = -1, color = (0,255,0), thickness = 3)
      if on_show_cam2:
        cv2.imshow("Camera 2", imgCam2Hsv)
        cv2.setMouseCallback("Camera 2", onMouse, param = (imgCam2, gamma))

      maxRadiusFigueContour = 10
      imgFigueDraw2 = np.copy(imgCam1FTI)
      for point in list_5_bestest_hull_point:
        if isClicked:
          cv2.circle(imgFigueDraw2, point, maxRadiusFigueContour, (0,0,255), -1, cv2.LINE_AA)
        else:
          cv2.circle(imgFigueDraw2, point, maxRadiusFigueContour, (0,255,0), -1, cv2.LINE_AA)
      imgFigueDraw2 = cv2.resize(imgFigueDraw2, (1920, 1080))
      cv2.imshow("Camera 1 figue 2", imgFigueDraw2)

    # if curFamesClicked == 0:
    #   curFamesClicked-=1
    #   mouse.click(Button.left, 2)
    #   # mouse.release(Button.left)
    # else:
    #   curFamesClicked-=1
    ### Process UI ###
    if on_cam1 and on_cam2:
      if len(list_5_bestest_hull_point) > 0:
        width, height = pyautogui.size()
        pointMouseNow = list_5_bestest_hull_point[0]
        mouseComputer = (int(width - pointMouseNow[0]*width/size_window[0]), int(height - pointMouseNow[1]*height/size_window[1]))

        if mouseComputer[0] > 0 and mouseComputer[1] > 0:
          speed = 5
          length = math.sqrt(pow(mouseComputer[0] - mouseComputer_old[0],2) + pow(mouseComputer[1] - mouseComputer_old[1],2))

          velocityX = (mouseComputer[0] - mouseComputer_old[0]) / length * speed
          velocityY = (mouseComputer[1] - mouseComputer_old[1]) / length * speed

          # mouse.position = (mouseComputer[0] + velocityX, mouseComputer[1] + velocityY)
          # # mouse.move(velocityX, velocityY)
          # if isClicked:
          # #   # Press and release
          #   # mouse.press(Button.left)
          #   mouse.click(Button.left, 2)
          #   curFamesClicked = maxFamesClicked

          #   # Double click; this is different from pressing and releasing
          #   # twice on macOS
          #   mouse.click(Button.left, 2)

          #   # Scroll two steps down
          #   mouse.scroll(0, 2)

          mouseComputer_old = mouse.position

    q = cv2.waitKey(1)
    if q == ord('q'):
      break
    elif q == ord('a'):
      print('pos(x,y) = (', mouseX, ",", mouseY, ')',sep='')
    elif q == ord('s'):
      # print(hsv.shape)
      print('hsv = (', imageProcesser.get_hsv_pos(imgCam2, gamma,(mouseY, mouseX)), ')',sep='')

def runCamera():
  sub1() 

# t1 = threading.Thread(target=RunProjector, args=())
# t1.start()
# t1.join()

t2 = threading.Thread(target=runCamera, args=())

t2.start()

t2.join()