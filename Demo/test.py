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

size_window = (600, 480)

mouseX, mouseY = 0,0
def onMouse(event, x, y, flags, param):
  global mouseX, mouseY
  mouseX, mouseY = x,y
  if event == cv2.EVENT_LBUTTONDOWN:
    print('pos(x,y) = (', mouseX, ",", mouseY, ')',sep='')
    print('hsv = (', imageProcesser.get_hsv_pos(param[0], param[1],(mouseY, mouseX)), ')',sep='')

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
  camera = CameraWebIP("http://192.168.42.100:8080/shot.jpg", size_window)
  # camera = CameraSelf(size_window)

  ro = (148,309)
  x = (441,308)
  y = (32,460)
  z = (553,454)

  while True:
    camera.updateFrame()
    
    img = matrixBincase.fast_tranform_image_opencv(camera.imgself, (ro, y, x, z), size_window)

    # resultsFigue = detectHander.process(camera.imgself)
    # list_pos_hands = detectHander.get_pos_hands(camera.imgself, resultsFigue)
    # for i in range(len(list_pos_hands)):
    #   list_pos_hands[i] = matrixBincase.tramform_points(list_pos_hands[i], (ro, y, x, z), size_window)
    #   list_pos_hands[i] += (0, 10)
    # print(len(list_pos_hands))

    # cv2.imshow("Camera processed", img)
    imgDraw = matrixBincase.draw_line(np.copy(camera.imgself), ro, y, x, z, 3)
    cv2.circle(imgDraw, (mouseX, mouseY), 10, (255,0,0),-1)
    cv2.imshow("Camera origan", imgDraw)
    cv2.setMouseCallback('Camera origan',onMouse)

    gamma = 0.5

    imgFigue = imageProcesser.filter_Color(img, gamma, (5, 110, 140), (20, 200, 255))
    # imgFigue = cv2.cvtColor(imgFigue, cv2.COLOR_GRAY2RGB)
    # for i in range(len(list_pos_hands)):
    #   cv2.circle(imgFigue, list_pos_hands[i], 10, (255,0,0),-1)
    cv2.imshow("Camera figue", imgFigue)

    imgFigueShallow = imageProcesser.filter_Color(img, gamma, (5, 100, 20), (20, 200, 100))
    # imgFigueShallow = cv2.cvtColor(imgFigueShallow, cv2.COLOR_GRAY2RGB)
    # for i in range(len(list_pos_hands)):
    #   cv2.circle(imgFigueShallow, list_pos_hands[i], 10, (255,0,0),-1)
    cv2.imshow("Camera figue shallow", imgFigueShallow)


    # # params for ShiTomasi corner detection
    # feature_params = dict( maxCorners = 5,
    #                       qualityLevel = 0.3,
    #                       minDistance = 6,
    #                       blockSize = 7 )
    # # Parameters for lucas kanade optical flow
    # lk_params = dict( winSize  = (15, 15),
    #                   maxLevel = 3,
    #                   criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
    # p0 = cv2.goodFeaturesToTrack(imgFigue, mask = None, **feature_params)
    # p1, st, err = cv2.calcOpticalFlowPyrLK(imgFigue, imgFigueShallow, p0, None, **lk_params)

    # # Select good points
    # if p1 is not None:
    #     good_new = p1[st==1]
    #     good_old = p0[st==1]
    # # draw the tracks
    # mask, frame = np.zeros_like(img), np.copy(img)
    # for i, (new, old) in enumerate(zip(good_new, good_old)):
    #   a, b = new.ravel()
    #   c, d = old.ravel()
    #   mask = cv2.line(mask, (int(a), int(b)), (int(c), int(d)), (0, 255, 0), 2)
    #   frame = cv2.circle(frame, (int(a), int(b)), 5, (0, 255, 0), -1)
    # imgTest = cv2.add(frame, mask)

    imgTest = np.copy(img)
    imgTest = imageProcesser.get_hsv_image(imgTest, gamma)
    # # for i in range(len(list_pos_hands)):
    # #   cv2.circle(imgTest, list_pos_hands[i], 10, (255,0,0),-1)
    cv2.imshow("Camera test", imgTest)
    cv2.setMouseCallback("Camera test",onMouse)

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