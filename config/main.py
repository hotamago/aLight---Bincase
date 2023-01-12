"""
Config camera main
"""
qr_version, qr_box_size, qr_border = 1, 8, 2

"""
Config camera main
"""
### Mode ###
on_cam1 = True
on_cam2 = True
on_cam1Hsv = False
on_cam2Hsv = False
on_config = False

on_show_cam1 = False
on_show_cam2 = False
on_controller = False

on_black_points_touch_screen = True

### Config camera and detect ###
gamma1 = 0.7
gamma2 = 0.7

noseCam1 = ((3, 3), (5, 5))
noseCam2 = ((3, 3), (5, 5))

fillCam1_01 = [(0, 90, 10), (35, 190, 150)]
fillCam2_01 = [(0, 90, 10), (35, 190, 150)]

### Config event mouse ###
maxFamesClicked = 5

### Config point touch ###
delta_Point = (0, 0)
n_points_touch = 1
deltaContoursClicked = 8
maxRadiusFigueWithFigueShallow = 12
numEleArgvan = 8

speed_smooth = 6