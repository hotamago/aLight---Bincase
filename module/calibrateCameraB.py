import cv2
import numpy as np

class Calibration():
    def __init__(self, size_chess, num_image_cal = 15):
        self.size_chess = size_chess
        self.num_image_cal = num_image_cal

        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        self.objp = np.zeros((size_chess[0]*size_chess[1],3), np.float32)
        self.objp[:,:2] = np.mgrid[0:size_chess[0],0:size_chess[1]].T.reshape(-1,2)
        # Arrays to store object points and image points from all the images.
        self.objpoints = [] # 3d point in real world space
        self.imgpoints = [] # 2d points in image plane.

        self.done = False
        self.mtx, self.dist, self.newcameramtx, self.roi = None, None, None, None
    
    def add(self, img):
        if self.done == True:
           return
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        if self.num_image_cal > 0:
          # Find the chess board corners
          ret, corners = cv2.findChessboardCorners(gray, self.size_chess, flags=cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)

          # If found, add object points, image points (after refining them)
          if ret == True:
            self.num_image_cal -= 1

            self.objpoints.append(self.objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), self.criteria)
            self.imgpoints.append(corners2)
        
        if self.num_image_cal <= 0:
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(self.objpoints, self.imgpoints, gray.shape[::-1], None, None)
            # Cal new matrix
            h,  w = img.shape[:2]
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

            self.mtx, self.dist, self.newcameramtx, self.roi = mtx, dist, newcameramtx, roi
            self.done = True

    def get(self):
        return self.mtx, self.dist, self.newcameramtx, self.roi
          
        