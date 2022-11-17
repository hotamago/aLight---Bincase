import cv2
import numpy as np

class ImageProcessor:
    def __init__(self):
        print("Installed ImageProcessor")

    def adjust_gamma(self, image, gamma):
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
        return cv2.LUT(image, table)

    def get_hsv_image(self, img, gamma):
        blurred = cv2.GaussianBlur(img, (9, 1), 0)
        # blurred = cv2.dilate(img, np.ones((15, 1), np.uint8))
        adjusted = self.adjust_gamma(blurred, gamma)
        hsv = cv2.cvtColor(adjusted,cv2.COLOR_BGR2HSV)
        return hsv

    def filter_Color(self, img, gamma, lower, upper):
        hsv = self.get_hsv_image(img, gamma)
        mask = cv2.inRange(hsv, lower, upper)
        ret, otsu = cv2.threshold(mask,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return otsu

    def get_hsv_pos(self, img, gamma, pos):
        hsv = self.get_hsv_image(img, gamma)
        return hsv[pos[0]][pos[1]]

    # cv2.MORPH_CLOSE cv2.MORPH_OPEN
    def image_noise_filter(self, img, type_filter, size, type_box = cv2.MORPH_RECT):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, size)
        img = cv2.morphologyEx(img, type_filter, kernel)
        return img