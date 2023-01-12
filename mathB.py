import numpy as np
import cv2

class MatrixBincase:
  #ma is matrix 2x3
  def __init__(self):
    print("New MatrixBincase")
  def find_coeffs(self, pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])

    A = np.matrix(matrix, dtype=np.float)
    B = np.array(pb).reshape(8)

    res = np.dot(np.linalg.inv(A), B)
    res = np.array(res).reshape(8)
    xyz3x3 = np.zeros((3, 3), dtype=np.float32)
    for i in range(0, 8):
      xyz3x3[i//3][i%3] = res[i]
    xyz3x3[2][2] = 1
    return xyz3x3
  def tranform_from_matrix(self, xy, ma):
    return np.array([(ma[0][0]*xy[0] + ma[0][1]*xy[1] + ma[0][2])/(ma[2][0]*xy[0] + ma[2][1]*xy[1] + ma[2][2]), (ma[1][0]*xy[0] + ma[1][1]*xy[1] + ma[1][2])/(ma[2][0]*xy[0] + ma[2][1]*xy[1] + ma[2][2])])
  def tranform_image_maxtrix(self, img, ma):
    height, width = img.shape
    imgFinal = np.zeros((height,width,3), np.uint8)
    ma = np.linalg.inv(ma)
    for i in range(0, img.shape[0]):
      for j in range(0, img.shape[1]):
        ji = np.array([j, i])
        newXY = self.tranform_from_matrix(ji, ma)
        newYX = np.array([newXY[1], newXY[0]])
        if(int(newYX[0]) < 0 or int(newYX[0]) >= img.shape[0]):
          continue
        if(int(newYX[1]) < 0 or int(newYX[1]) >= img.shape[1]):
          continue
        imgFinal[i][j] = img[int(newYX[0])][int(newYX[1])]
    return imgFinal
  def tramform_points(self, pos, po4, wh):
    M = cv2.getPerspectiveTransform(np.float32(po4), np.float32(((0, 0), (0, wh[1]), (wh[0], 0), (wh[0], wh[1]))))
    # ma = np.linalg.inv(M)
    newXY = self.tranform_from_matrix(pos, M)
    newYX = np.array([int(newXY[0]), int(newXY[1])])
    return newYX
  def slow_tranform_image(self, img, po4, wh):
    M = self.find_coeffs(po4, ((0, 0), (0, wh[1]), (wh[0], 0), (wh[0], wh[1])))
    imgFinal = self.tranform_image_maxtrix(img, M)
    return imgFinal
  def fast_tranform_image_opencv(self, img, po4, wh):
    M = cv2.getPerspectiveTransform(np.float32(po4), np.float32(((0, 0), (0, wh[1]), (wh[0], 0), (wh[0], wh[1]))))
    imgFinal = cv2.warpPerspective(img,M,(wh[0], wh[1]),flags=cv2.INTER_LINEAR)
    return imgFinal
  def draw_line(self, img, ro, x, y, z, size_line):
    img = cv2.line(img, ro, y, (255, 255, 255), size_line) #bl -> tl
    img = cv2.line(img, ro, x, (255, 255, 255), size_line) #bl -> br
    img = cv2.line(img, y, z, (255, 255, 255), size_line) #tl -> tr
    img = cv2.line(img, x, z, (255, 255, 255), size_line) #br -> tr
    return img