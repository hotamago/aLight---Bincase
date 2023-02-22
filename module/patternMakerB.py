import cv2
import numpy as np

class PatternMaker:
    def __init__(self, cols, rows, width, height, conner_size = (5, 5)):
        self.cols = cols
        self.rows = rows
        self.width = width
        self.height = height
        self.conner_size = conner_size
        self.g = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.g.fill(255)

    def make_circle_pattern(self, radius = 20):
        xspacing = self.conner_size[0] // 2 + radius
        yspacing = self.conner_size[1] // 2 + radius

        cv2.circle(self.g, (xspacing, yspacing), radius, (0, 0, 0), -1, cv2.LINE_AA)
        cv2.circle(self.g, (self.width - xspacing, yspacing), radius, (0, 0, 0), -1, cv2.LINE_AA)
        cv2.circle(self.g, (xspacing, self.height - yspacing), radius, (0, 0, 0), -1, cv2.LINE_AA)
        cv2.circle(self.g, (self.width - xspacing, self.height - yspacing), radius, (0, 0, 0), -1, cv2.LINE_AA)

    def make_checkerboard_pattern(self):
        xspacing = self.conner_size[0] // 2
        yspacing = self.conner_size[1] // 2
        size_x_q = (self.width - self.conner_size[0]) // self.cols
        size_y_q = (self.height - self.conner_size[1]) // self.rows

        for x in range(-1, self.cols + 1):
            for y in range(-1, self.rows + 1):
                py = yspacing + y*size_y_q
                px = xspacing + x*size_x_q
                if x % 2 == y % 2:
                    self.g[max(0, py): min(py + size_y_q, self.height), max(0, px): min(px + size_x_q, self.width)].fill(0)
                else:
                    self.g[max(0, py): min(py + size_y_q, self.height), max(0, px): min(px + size_x_q, self.width)].fill(255)

    def get(self):
        return self.g
