import math
import cv2
import numpy as np

list_hsv = ((42,40,127),(33,49,115),(43,35,133),(33,48,118),(24,68,101),(20,73,116),(19,66,127),(24,67,106),(17,76,121),(17,75,125))

hsv_min = (179, 255, 255)
hsv_max = (0, 0, 0)

for hsv_color in list_hsv:
    hsv_min = list(hsv_min)
    hsv_max = list(hsv_max)
    hsv_color = list(hsv_color)

    hsv_min[0] = min(hsv_min[0], hsv_color[0])
    hsv_min[1] = min(hsv_min[1], hsv_color[1])
    hsv_min[2] = min(hsv_min[2], hsv_color[2])

    hsv_max[0] = max(hsv_max[0], hsv_color[0])
    hsv_max[1] = max(hsv_max[1], hsv_color[1])
    hsv_max[2] = max(hsv_max[2], hsv_color[2])
    
hsv_min = tuple(hsv_min)
hsv_max = tuple(hsv_max)
print(hsv_min, hsv_max)


      # maxContoursFigue = (0, 0)
      # for contourF in contoursFigue:
      #   if type(contourF) == 'numpy.intc':
      #     print("WTF1??: ", contourF)
      #     continue
      #   if len(contourF) <= 1:
      #     print("WTF2??: ", contourF)
      #     continue
      #   maxContoursFigue = contourF if contourF[1] > maxContoursFigue[1] else maxContoursFigue

      # list_nears_figures = []

      # if (maxContoursFigue[0] + maxRadiusFigueContour <= size_window[0]) and (maxContoursFigue[1]+ maxRadiusFigueContour <= size_window[1]):
      #   for contourF in contoursFigue:
      #     if len(contourF) <= 1 or len(maxContoursFigue) <= 1:
      #         continue
      #     di = math.sqrt(math.pow(contourF[0] - maxContoursFigue[0], 2) + math.pow(contourF[1] - maxContoursFigue[1], 2))
      #     if di <= maxRadiusFigueContour:
      #       list_nears_figures.append(contourF)
      
      # if len(list_nears_figures) > 0:
      #   for contourF in list_nears_figures:
      #     isHasNear = False
      #     for contourFS in contoursFigueShallow:
      #       if type(contourF) == 'numpy.intc' or type(contourF) == contourFS:
      #         print("WTF3??: ", contourF, ", ", contourF)
      #         continue
      #       if len(contourF) <= 1 or len(contourFS) <= 1:
      #         print("WTF4??: ", contourF, ", ", contourF)
      #         continue
      #       di = math.sqrt(math.pow(contourF[0] - contourFS[0], 2) + math.pow(contourF[1] - contourFS[1], 2))
      #       if di <= maxRadiusFigueWithFigueShallow:
      #         isHasNear = True
      #         break
      #     if not isHasNear:
      #       cntNoNear += 1
            
      #   # print(cntNoNear/len(list_nears_figures))
      #   if cntNoNear/len(list_nears_figures) > deltaPeCntNoNear/100:
      #     isClicked = True
