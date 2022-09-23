import urllib
import urllib.request
import cv2
import numpy as np
import ssl

cv2.destroyAllWindows()

class Camera:
  def __init__(self, url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    while True:
      imgResp = urllib.request.urlopen(url)
      imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
      
      img = cv2.imdecode(imgNp, -1)
      img_600x400 = cv2.resize(img,(600,400))
      cv2.imshow('temp',img_600x400)
      q = cv2.waitKey(1)
      if q == ord("q"):
          break;