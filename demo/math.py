import numpy as np
import cv2

class MatrixBincase:
  # def __init__():
    #nothing
  #ma is matrix 2x3
  def find_coeffs(self, pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])

    A = np.matrix(matrix, dtype=np.float)
    B = np.array(pb).reshape(8)

    res = np.dot(np.linalg.inv(A.T * A) * A.T, B)
    return np.array(res).reshape(8)

matrixBincase = MatrixBincase()

height = 400
width = 600
aw = 3

blank_image = np.zeros((height,width,3), np.uint8)
# img = cv2.imdecode(blank_image, -1)
img = np.copy(blank_image)
# img_600x400 = cv2.resize(img,(600,400))

ro = (0,0)
y = (143, 390)
x = (324, 29)
z = (578, 285)

imgProcess = cv2.line(img, ro, y, (255, 255, 255), aw) #bl -> tl
imgProcess = cv2.line(imgProcess, ro, x, (255, 255, 255), aw) #bl -> br
imgProcess = cv2.line(imgProcess, y, z, (255, 255, 255), aw) #tl -> tr
imgProcess = cv2.line(imgProcess, x, z, (255, 255, 255), aw) #br -> tr

print(imgProcess.shape)

xyzDemo = matrixBincase.find_coeffs((ro, x, y, z), ((0, 0), (0, height), (width, 0), (width, height)))
print(xyzDemo)

quit()

imgFinal = np.copy(blank_image)
for i in range(0, imgProcess.shape[0]):
  for j in range(0, imgProcess.shape[1]):
    ij = np.array([i, j])
    x2 = ij + x
    y2 = ij + y
    z2 = ij + z
    xyz = np.array([x2, y2, z2])
    xyz2T = matrixBincase.QuaToRec2x3(xyz.transpose())
    xyz = xyz2T.transpose()
    # print(xyz.shape)
    if xyz[0][1]<=width and xyz[0][0]<=height:
      if x2[1]<=height and x2[0]<=width:
        imgFinal[xyz[0][1]-1][xyz[0][0]-1] = imgProcess[x2[1]-1][x2[0]-1]
    if xyz[1][1]<=width and xyz[1][0]<=height:
      if y2[1]<=height and y2[0]<=width:
        imgFinal[xyz[1][1]-1][xyz[1][0]-1] = imgProcess[y2[1]-1][y2[0]-1]
    if xyz[2][1]<=width and xyz[2][0]<=height:
      if z2[1]<=height and z2[0]<=width:
        imgFinal[xyz[2][1]-1][xyz[2][0]-1] = imgProcess[z2[1]-1][z2[0]-1]

# imgFinal = imgProcess

cv2.imshow('temp',imgFinal)
cv2.waitKey(0)
cv2.destroyAllWindows()