"""
Config Multi thead mode
"""
is_multi_thead = False

"""
Config camera main
"""
qr_version, qr_box_size, qr_border = 1, 12, 1

"""
Config camera main
"""
### Mode ###
on_cam1 = True
on_cam2 = True
on_cam1Hsv = False
on_cam2Hsv = False
on_cam1FTI = False
on_cam2FTI = False
on_config = False

on_show_cam1 = False
on_show_cam2 = False
on_controller = True

on_black_points_touch_screen = False

### Config camera and detect ###
gamma1 = 0.6
gamma2 = 0.7

noseCam1 = ((3, 3), (5, 5))
noseCam2 = ((3, 3), (5, 5))

fillCam1_01 = [(0, 90, 10), (35, 190, 150)]
fillCam2_01 = [(0, 90, 10), (35, 190, 150)]

is_cam1_flip = True
is_cam2_flip = True

cam1_flip_mode = -1
cam2_flip_mode = -1

cam1_exposure, cam1_exposure_auto = 100, 0
cam2_exposure, cam2_exposure_auto = 100, 0

urlcam1 = "http://192.168.137.85:8080/shot.jpg"
urlcam2 = "http://192.168.137.85:8080/shot.jpg"

### Config frame ###
FramePerProcess = 1

### Config event mouse ###
maxFamesClicked = 5

### Config point touch ###
is_flip_mouse = True

delta_Point = (0, 0)
n_points_touch = 1
deltaContoursClicked = 6
maxRadiusFigueWithFigueShallow = 12

numEleArgvan = 8
numAverageMouseMove = 8

### Config UI ###
maxRadiusFigueContour = 10

color_nonClicked = (0,255,0)
color_clicked = (0,0,255)
