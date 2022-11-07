import cv2
import mediapipe as mp
import time

class DetectHander():
    size_circle = 10
    color_circle = (255, 0, 255)
    def __init__(self, list_id_hands):
        mpHands = mp.solutions.hands
        self.hands = mpHands.Hands() # using default paramaters of 'Hands()'
        self.mpDraw = mp.solutions.drawing_utils
        self.list_id_hands = list_id_hands
    def process(self, img):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return self.hands.process(imgRGB)
    def get_pos_hands(self, img, results = None):
        if results is None:
            results = self.process(img)
        list_pos_hands = []
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    if(id not in self.list_id_hands):
                        continue
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    list_pos_hands.append((cx, cy))
        return list_pos_hands
    def draw_all_hands(self, img, results = None):
        if results is None:
            results = self.process(img)
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img
    def draw_circle_hands(self, img, results = None):
        if results is None:
            results = self.process(img)
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    if(id not in self.list_id_hands):
                        continue
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (cx, cy), self.size_circle, self.color_circle, cv2.FILLED)
        return img
            