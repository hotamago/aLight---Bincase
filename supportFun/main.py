"""
Open library
"""
import cv2
import numpy as np

from pyzbar.pyzbar import decode as detectAndDecodeQR
from pyzbar.pyzbar import ZBarSymbol

"""
Bincase library
"""
from module.mathB import MatrixBincase
from module.imageProcess import ImageProcessor
from module.qrcodeB import QRCodeB

from config.main import *
from constant.main import *

"""
Init object
"""
matrixBincase = MatrixBincase()
imageProcesser = ImageProcessor()
detectQR = cv2.QRCodeDetector()
qr = QRCodeB(version=qr_version, box_size=qr_box_size, border=qr_border)

"""
Main
"""
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

# Detect hand
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

# Auto detect corners
imgQRcorners = qr.given_image_corners_qr(fullscreensize, core_value_qr)
def setFullScreenCV(nameWindow):
  cv2.namedWindow(nameWindow, cv2.WND_PROP_FULLSCREEN)
  cv2.setWindowProperty(nameWindow, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
def showQRcorners():
  """
  Show QR code corners
  """
  setFullScreenCV("imgQRcorners")
  cv2.imshow("imgQRcorners", imgQRcorners)
def destroyQRcorners():
  cv2.destroyWindow("imgQRcorners")
  
def get4Corners(imgCam, lambda_format_ma):
  global imgQRcorners
  maCam = ((0, 0), (0, 0), (0, 0), (0, 0))
  maCamYXZ = ((0, 0), (0, 0), (0, 0), (0, 0))
  is_detect_corners = False

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
    maCamYXZ = lambda_format_ma(maCam)
  return is_detect_corners, maCam, maCamYXZ
