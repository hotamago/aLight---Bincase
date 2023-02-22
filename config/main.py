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

on_cam1Hsv = True
on_cam2Hsv = True
on_cam1Ycbcr = False
on_cam2Ycbcr = False
on_cam1FTI = False
on_cam2FTI = False

on_config = False

on_show_cam1 = False
on_show_cam2 = False
on_controller = False

on_black_points_touch_screen = True

on_debug = False

### Config camera and detect ###
gamma1 = 0.6
gamma2 = 0.6

noseCam1 = ((3, 3), (5, 5))
noseCam2 = ((3, 3), (5, 5))

fillCam1_01 = [[(0, 90, 10), (35,190,150)], [(0, 0, 0), (255,180,135)]]
fillCam2_01 = [[(0, 90, 10), (35,190,150)], [(0, 0, 0), (255,180,135)]]

# fillCam1_01 = [[(0, 15, 0), (35,170,255)], [(0, 135, 85), (255,180,135)]]
# fillCam2_01 = [[(0, 15, 0), (35,170,255)], [(0, 135, 85), (255,180,135)]]

# fillCam1_01 = [(0, 90, 10), (35, 190, 150)]
# fillCam2_01 = [(0, 90, 10), (35, 190, 150)]

is_cam1_flip = False
is_cam2_flip = False

cam1_flip_mode = -1
cam2_flip_mode = -1

cam1_exposure, cam1_exposure_auto = 100, 0
cam2_exposure, cam2_exposure_auto = 100, 0

urlcam1 = "http://192.168.137.192:8080/shot.jpg"
urlcam2 = "http://192.168.137.192:8080/shot.jpg"

fps_cam1 = 30
fps_cam2 = 15

### Config frame ###
FramePerProcess = 2

### Config event mouse ###
maxFamesClicked = 5

### Config point touch ###
is_flip_mouse = True

delta_Point = (0, 0)
n_points_touch = 1
deltaContoursClicked = 8
maxRadiusFigueWithFigueShallow = 12

is_debug_clicked = False

numEleArgvan = 8
numAverageMouseMove = 8

time_delay_press = 0.5
time_delay_right_click = 1.5

### Config UI ###
maxRadiusFigueContour = 10

color_nonClicked = (0,255,0)
color_clicked = (0,0,255)

show_FPS_console = False
