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
# from data_struct.kd_tree import KdTree

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

size_window = (600, 480)

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
  # camera1 = CameraSelf(size_window)
  camera2 = CameraWebIP("http://192.168.42.100:8080/shot.jpg", size_window)

  gamma = 0.5
  mouseComputer_old = (0, 0)

  while True:
    # camera1.updateFrame()
    camera2.updateFrame()

    # imgCam1 = camera1.imgself
    imgCam2 = camera2.imgself

    maCam1 = ((148,309), (441,308), (32,460), (553,454))
    maCam1YXZ = (maCam1[0], maCam1[2], maCam1[1], maCam1[3])

    ##
    res1 = detectHander.process(imgCam2)

    imgCam2Draw = np.copy(imgCam2)
    matrixBincase.draw_line(imgCam2Draw, maCam1YXZ[0], maCam1YXZ[1], maCam1YXZ[2], maCam1YXZ[3], 3)
    detectHander.draw_circle_hands(imgCam2Draw, res1)
    cv2.imshow("Camera test 1", imgCam2Draw)

    list_hands1 = detectHander.get_pos_hands(imgCam2, res1)
    for i in range(len(list_hands1)):
      list_hands1[i] = matrixBincase.tramform_points(list_hands1[i], maCam1YXZ, size_window)
      list_hands1[i] += (0, 10)
    
    imgCam1FTI = matrixBincase.fast_tranform_image_opencv(imgCam2, maCam1YXZ, size_window)

    ### Check pos hand ###
    for i in range(len(list_hands1)):
      cv2.circle(imgCam1FTI, list_hands1[i], 10, (255,0,0),-1)
    cv2.imshow("Camera 2", imgCam1FTI)
    cv2.setMouseCallback("Camera 2", onMouse, param = (imgCam2, gamma))

    ### Check clicked ###
    # maCam2 = ((272,296), (423,287), (180,345), (597,322))
    # maCam2YXZ = (maCam2[0], maCam2[2], maCam2[1], maCam2[3])
    # imgCam2FTI = matrixBincase.fast_tranform_image_opencv(imgCam2, maCam2YXZ, size_window)
    # imgCam2Up = imageProcesser.filter_Color(np.copy(imgCam2FTI), gamma, (0, 90, 30), (15, 180, 130))
    # imgCam2Down = imageProcesser.filter_Color(np.copy(imgCam2FTI), gamma, (0, 100, 0), (20, 160, 10))
    # # imgCam2Down = np.zeros_like(imgCam2Up)
    # imgCam2Hsv = cv2.add(imgCam2Up, imgCam2Down)
    # contours, hierarchy = cv2.findContours(imgCam2Hsv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # imgCam2Draw = imageProcesser.get_hsv_image(np.copy(imgCam2FTI), gamma)
    # cv2.circle(imgCam2Draw, (mouseX, mouseY), 10, (255,0,0),-1)

    # isClicked = False

    # np_contours = np.array(contours)
    # if np_contours.shape[0] > 10:
    #   isClicked = True
    #   print("clicked - ", np_contours.shape[0])

    # imgCam2Hsv = cv2.cvtColor(imgCam2Hsv, cv2.COLOR_GRAY2BGR)
    # cv2.drawContours(imgCam2Hsv, contours, contourIdx = -1, color = (0,255,0), thickness = 3)
    # cv2.imshow("Camera 2", imgCam2Hsv)
    # cv2.setMouseCallback("Camera 2", onMouse, param = (imgCam2, gamma))


    ### Process UI ###
    if len(list_hands1) > 0:
      width, height = pyautogui.size()
      mouseComputer = (int(width - list_hands1[0][0]*width/size_window[0]), int(height - list_hands1[0][1]*height/size_window[1]))

      if mouseComputer[0] > 0 and mouseComputer[1] > 0:
        speed = 5
        length = math.sqrt(pow(mouseComputer[0] - mouseComputer_old[0],2) + pow(mouseComputer[1] - mouseComputer_old[1],2))

        velocityX = (mouseComputer[0] - mouseComputer_old[0]) / length * speed
        velocityY = (mouseComputer[1] - mouseComputer_old[1]) / length * speed

        mouse.position = (mouseComputer[0] + velocityX, mouseComputer[1] + velocityY)
        # mouse.move(velocityX, velocityY)
        mouseComputer_old = mouse.position

    q = cv2.waitKey(1)
    if q == ord('q'):
      break
    elif q == ord('a'):
      print('pos(x,y) = (', mouseX, ",", mouseY, ')',sep='')
    elif q == ord('s'):
      # print(hsv.shape)
      print('hsv = (', imageProcesser.get_hsv_pos(imgCam2, gamma,(mouseY, mouseX)), ')',sep='')

def sub2():
  global mouseX, mouseY, size_window
  camera = CameraWebIP("http://192.168.137.190:8080/shot.jpg", size_window)
  # camera = CameraSelf(size_window)

  maCam1 = ((2,53), (597,50), (2,318), (600,324))
  ro = maCam1[0]
  x = maCam1[1]
  y = maCam1[2]
  z = maCam1[3]

  # Low dark
  # imgFigueColor = [(5, 120, 150), (12, 255, 255)]
  # Dark
  imgFigueColor = [(5, 120, 160), (20, 255, 255)]
  imgFigueShallowColor = [(5, 100, 20), (20, 200, 100)]

  gamma = 0.8

  BGKFake = False

  while True:

    ### Pre process ###
    camera.updateFrame()

    imgCam1 = np.copy(camera.imgself)
    img = matrixBincase.fast_tranform_image_opencv(imgCam1, (ro, y, x, z), size_window)

    # cv2.imshow("Camera processed", img)
    imgDraw = matrixBincase.draw_line(np.copy(imgCam1), ro, y, x, z, 3)
    cv2.circle(imgDraw, (mouseX, mouseY), 10, (255,0,0),-1)
    if not BGKFake:
      cv2.imshow("Camera origan", imgDraw)
      cv2.setMouseCallback('Camera origan',onMouse, param=(imgCam1, gamma))
    
    ### imgFigue ###
    imgFigue = imageProcesser.filter_Color(img, gamma, imgFigueColor[0], imgFigueColor[1])
    imgFigue = imageProcesser.image_noise_filter(imgFigue, cv2.MORPH_CLOSE, (5,5))
    imgFigue = imageProcesser.image_noise_filter(imgFigue, cv2.MORPH_OPEN, (20,20))
    contoursFigue, hierarchyFigue = cv2.findContours(imgFigue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    imgFigueDraw = cv2.cvtColor(imgFigue, cv2.COLOR_GRAY2RGB)
    # for i in range(len(list_pos_hands)):
    #   cv2.circle(imgFigue, list_pos_hands[i], 10, (255,0,0),-1)

    hull_list = []
    for i in range(len(contoursFigue)):
      hull = cv2.convexHull(contoursFigue[i])
      hull_list.append(hull)
      cv2.drawContours(imgFigueDraw, hull_list, i, color = (255,0,0), thickness = 5)

    # if len(contoursFigue) > 0:
    #   dkd = np.vstack(contoursFigue).reshape(-1, 2)
    #   hull = cv2.convexHull(dkd) 
    #   hull = [hull]
    #   cv2.drawContours(imgFigueDraw, hull, contourIdx = -1, color = (255,0,0), thickness = 10)
    if not BGKFake:
      cv2.drawContours(imgFigueDraw, contoursFigue, contourIdx = -1, color = (0,255,0), thickness = 3)
      cv2.imshow("Camera figue", imgFigueDraw)

    ### imgFigueShallow ###
    imgFigueShallow = imageProcesser.filter_Color(img, gamma, imgFigueShallowColor[0], imgFigueShallowColor[1])
    # imgFigueShallow = imageProcesser.image_noise_filter(imgFigueShallow, cv2.MORPH_CLOSE, (5,5))
    # imgFigueShallow = imageProcesser.image_noise_filter(imgFigueShallow, cv2.MORPH_OPEN, (5,5))
    contoursFigueShallow, hierarchyFigueShallow = cv2.findContours(imgFigueShallow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    imgFigueShallowDraw = cv2.cvtColor(imgFigueShallow, cv2.COLOR_GRAY2RGB)
    # for i in range(len(list_pos_hands)):
    #   cv2.circle(imgFigueShallow, list_pos_hands[i], 10, (255,0,0),-1)
    if not BGKFake:
      cv2.drawContours(imgFigueShallowDraw, contoursFigueShallow, contourIdx = -1, color = (0,255,0), thickness = 3)
      cv2.imshow("Camera figue shallow", imgFigueShallowDraw)

    # print(len(contoursFigue), len(contoursFigueShallow))
    # print(contoursFigue, contoursFigueShallow)
      
    ### Constance ###
    maxRadiusFigueWithFigueShallow = 50
    maxRadiusFigueContour = 30
    deltaCntNoNear = 180
    deltaPeCntNoNear = 90
    isClicked = False

    list_points_clicked = []

    # maxContoursFigue = None

    # print(type(contoursFigue), type(contoursFigueShallow))

    ### Find fingue ###
    list_highest_point_hull = []
    # print(hull_list)
    for hulls in hull_list:
      highest_point_hull = max(hulls, key=lambda x: x[0][1])
      list_highest_point_hull.append(highest_point_hull[0])

    list_highest_point_hull.sort(key=lambda x: -x[1])
    list_5_bestest_hull_point = []
    cnt_5_bestest_hull_point = 3
    for point in list_highest_point_hull:
      list_5_bestest_hull_point.append(point)
      cnt_5_bestest_hull_point-=1
      if cnt_5_bestest_hull_point <= 0:
        break
      
    ### Process all ###
    if len(contoursFigue) > 0: # and len(contoursFigueShallow) > 0
      contoursFigue = np.vstack(contoursFigue).reshape(-1, 2)
      if len(contoursFigueShallow) > 0:
        contoursFigueShallow = np.vstack(contoursFigueShallow).reshape(-1, 2)
      else:
        contoursFigueShallow = []
      
      # hull = cv2.convexHull(contoursFigue)
      # hull = np.vstack(hull).reshape(-1, 2).tolist()
      # # print(type(hull), hull.shape)
      # hull.sort(key=lambda x: -x[1])
      # cnt_5_bestest_hull_point = 5
      # for point in hull:
      #   list_5_bestest_hull_point.append(point)
      #   cnt_5_bestest_hull_point-=1
      #   if cnt_5_bestest_hull_point <= 0:
      #     break

      for point in list_5_bestest_hull_point:
        cntNoNear = 0
        if type(point) == 'numpy.intc':
          print("WTF1??: ", point)
          continue
        if len(point) <= 1:
          print("WTF2??: ", point)
          continue
        
        list_nears_figures = []

        if (point[0] + maxRadiusFigueContour <= size_window[0]) and (point[1]+ maxRadiusFigueContour <= size_window[1]):
          for contourF in contoursFigue:
            if type(contourF) == 'numpy.intc' or type(point) == 'numpy.intc':
                continue
            if len(contourF) <= 1 or len(point) <= 1:
                continue
            di = math.sqrt(math.pow(contourF[0] - point[0], 2) + math.pow(contourF[1] - point[1], 2))
            if di <= maxRadiusFigueContour:
              list_nears_figures.append(contourF)
      
        if len(list_nears_figures) > 0:
          for contourF in list_nears_figures:
            isHasNear = False
            for contourFS in contoursFigueShallow:
              if type(contourF) == 'numpy.intc' or type(contourFS) == 'numpy.intc':
                print("WTF3??: ", contourF, ", ", contourFS)
                continue
              if len(contourF) <= 1 or len(contourFS) <= 1:
                print("WTF4??: ", contourF, ", ", contourFS)
                continue
              di = math.sqrt(math.pow(contourF[0] - contourFS[0], 2) + math.pow(contourF[1] - contourFS[1], 2))
              if di <= maxRadiusFigueWithFigueShallow:
                isHasNear = True
                break
            if not isHasNear:
              cntNoNear += 1
              
          # print(cntNoNear/len(list_nears_figures))
          if cntNoNear/len(list_nears_figures) >= deltaPeCntNoNear/100:
            list_points_clicked.append(point)
            isClicked = True
    
    # if isClicked:
    #   print("Clicked - ", cntNoNear)

    ### TEST CAMERA ###
    imgTest = np.copy(img)
    imgTest = imageProcesser.get_hsv_image(imgTest, gamma)
    for point in list_5_bestest_hull_point:
      cv2.circle(imgTest, point, maxRadiusFigueContour, (0,255,0), -1, cv2.LINE_AA)
    for point in list_points_clicked:
      cv2.circle(imgTest, point, maxRadiusFigueContour, (255,0,0), -1, cv2.LINE_AA)
    cv2.imshow("Camera test", imgTest)
    cv2.setMouseCallback("Camera test",onMouse, param = (img, gamma))

    q = cv2.waitKey(1)
    if q == ord('q'):
      break
    elif q == ord('a'):
      print('pos(x,y) = (', mouseX, ",", mouseY, ')',sep='')
    elif q == ord('s'):
      # print(hsv.shape)
      print('hsv = (', imageProcesser.get_hsv_pos(img, gamma,(mouseY, mouseX)), ')',sep='')

def runCamera():
  sub2() 

# t1 = threading.Thread(target=RunProjector, args=())
# t1.start()
# t1.join()

t2 = threading.Thread(target=runCamera, args=())

t2.start()

t2.join()