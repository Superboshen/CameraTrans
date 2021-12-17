import numpy as np
from utils.checkPoint import is_point_in_polygon
from utils.extract_box import pkl2List
from utils.vector import Vector
import json
import time
import matplotlib.pyplot as plt


def box2xy(box, width=640, height=480):
    """将框坐标转为图像坐标系(x, y)
        box: [xmin, ymin, xmax, ymax]
    """
    xmin = box[0]
    ymin = box[1]
    xmax = box[2]
    # 计算每个框上边界中点坐标
    x = (xmin + xmax) / 2
    y = ymin
    # 移动坐标原点至图片中心
    x = x - (width / 2)
    y = -(y - (height / 2))
    return x, y


def xy2XZ(cooPic, theta=30, camera_h=350, person_h=165, fx=450, fy=600):
    """
       推算出图像上一个点在相机坐标中的X，Z
       X = x * Z / f
       Y = -h + person_h
            由y / f = (Z * tanΘ + Y) / (Z - Y * tanΘ)得： (其实上下都乘了一个cosθ，约掉了)
       Z = Y * (y * tanΘ + f) / (y - f * tanΘ)

       :param
             cooPic: (x, y) 图像坐标系坐标
             theta: 摄像头与Z轴夹角
             h: 摄像机距地板高度
             f: 焦距
       :return
            （camx, camz）相机坐标系坐标
    """
    tanTheta = np.tan(theta * np.pi / 180)
    camy = -1 * camera_h + person_h
    x = cooPic[0]
    y = cooPic[1]

    # 计算真实Z
    camz = camy * (y * tanTheta + fy) / (y - fy * tanTheta)
    camx = x * camz / fx
    return camx, camz


def camCooToReal(camCoo, camera_coo, camera_shoot_coo):
    """
    将相机坐标系下的点坐标转为物理坐标系下点的坐标
    :param
        camCoo: (x, z) 相机坐标系下坐标
        camera_coo: 相机的实际物理坐标
        camera_shoot_coo: 相机对应朝向点的实际物理坐标
    """
    camera_coo = np.array(camera_coo)
    camera_shoot_coo = np.array(camera_shoot_coo)
    vector_z = Vector(list(camera_shoot_coo - camera_coo))
    norm_vector_z = np.array(vector_z.normalized())  # Z轴单位向量
    norm_vector_x = np.array([-norm_vector_z[1], norm_vector_z[0]])  # X轴单位向量
    camx = camCoo[0]
    camz = camCoo[1]
    dx = abs(camx)
    dz = abs(camz)

    if camx > 0:
        map_coo = tuple(camera_coo + dx * norm_vector_x + dz * norm_vector_z)
    else:
        map_coo = tuple(camera_coo - dx * norm_vector_x + dz * norm_vector_z)

    return tuple(map(lambda x: int(x), map_coo))


def camScope(pic_scope_coos, camCoo, camShoot, theta, camera_h, floor_person_h=0, fx=450, fy=600):
    """
    计算一个摄像机的视野范围
        :param pic_scope_coos: 图像坐标系中四个角点坐标(原点在图像中心) [(-320, 240), (320, 240), (-320, -240), (320, -240)]
        :return: 物理坐标系中四个角点坐标   [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    """
    real_cam_scope_coos = []
    for pic_corner_list in pic_scope_coos:
        tmp = []
        for pic_corner_coo in pic_corner_list:
            cam_scope_coo = xy2XZ(pic_corner_coo, theta=theta, camera_h=camera_h, person_h=floor_person_h, fx=fx, fy=fy)
            real_cam_scope_coo = camCooToReal(cam_scope_coo, camCoo, camShoot)
            tmp.append(real_cam_scope_coo)
        real_cam_scope_coos.append(tmp)
    return real_cam_scope_coos


def allCamScope(camera_params):
    """
    计算一个店所有摄像机的多边形区域
    Args:
        camera_params: [{'cameraID': 'C4c9020edc56680fe', 'camCoo': (693, 958), 'camShoot': (675, 187), 'theta': 29, 'camHeight': 300,
            'fx': 450, 'fy': 600},...]
    return: [[(x1, y1), (x2, y2), (x3, y3), (x4, y4)],...]
    """
    real_cam_scopes = []
    for cam in camera_params:
        cam_coo = cam['camCoo']
        cam_shoot_coo = cam['camShoot']
        cam_theta = cam['theta']
        cam_height = cam['camHeight']
        fx = cam['fx']
        fy = cam['fy']
        # 物理坐标系下摄像机视野范围角点(最后要加上第一个点，形成闭合回路)
        pic_floor_coos = [[[-320, 240], [-320, -240], [320, -240], [320, 240], [-320, 240]]]
        real_cam_scope_coos = camScope(pic_floor_coos, cam_coo, cam_shoot_coo,
                                       theta=cam_theta, camera_h=cam_height, fx=fx, fy=fy)
        real_cam_scopes.append(real_cam_scope_coos)
    return real_cam_scopes


def checkCamScope(real_cam_scopes, real_point):
    """判断物理坐标系下一个坐标点被几个相机的分摊比例
        Args:
            real_coo: (X', Z')
    """
    check_res = []  # eg. [True, False, True]   表示该点同时存在于1，3摄像机范围内
    for real_cam_scope in real_cam_scopes:
        res = is_point_in_polygon(real_point, real_cam_scope, True)
        check_res.append(res)
    try:
        rate = round(1 / sum(check_res), 2)
    except ZeroDivisionError:
        rate = 1
    return [real_point[0], real_point[1], rate]


if __name__ == '__main__':
    data_set = pkl2List('/path...')
    result = {}

    cameras = [
        {'cameraID': 'C000095', 'camCoo': (1290, 394), 'camShoot': (1282, 531), 'theta': 36, 'camHeight': 300,
         'fx': 370, 'fy': 500},
        {'cameraID': 'C000109', 'camCoo': (829, 1266), 'camShoot': (1055, 953), 'theta': 44, 'camHeight': 300,
         'fx': 370, 'fy': 500},
        {'cameraID': 'C000098', 'camCoo': (1235, 1504), 'camShoot': (1756, 1515), 'theta': 39, 'camHeight': 267,
         'fx': 370, 'fy': 500},
        {'cameraID': 'C000110', 'camCoo': (684, 569), 'camShoot': (1460, 270), 'theta': 31, 'camHeight': 300,
         'fx': 450, 'fy': 600},
        {'cameraID': 'C000111', 'camCoo': (765, 911), 'camShoot': (843, 510), 'theta': 27, 'camHeight': 300,
         'fx': 450, 'fy': 600},
        {'cameraID': 'C000112', 'camCoo': (1231, 1687), 'camShoot': (2042, 2263), 'theta': 26, 'camHeight': 267,
         'fx': 450, 'fy': 600},
    ]
    all_real_cam_scopes = allCamScope(cameras)

    start = time.time()
    print('start: ', start)
    all_len = 0
    for camera in cameras[2:3]:
        cameraid = camera['cameraID']
        camera_coo = camera['camCoo']
        cameraShoot = camera['camShoot']
        theta = camera['theta']
        camHeight = camera['camHeight']
        fx = camera['fx']
        fy = camera['fy']

        if cameraid not in result:
            result[cameraid] = []

        for box in data_set['C000098']:
            pic_coo = box2xy(box)
            cam_coo = xy2XZ(pic_coo, theta=theta, camera_h=camHeight, fx=fx, fy=fy)
            rea_coo = camCooToReal(cam_coo, camera_coo, cameraShoot)
            final_coo = checkCamScope(all_real_cam_scopes, rea_coo)
            result[cameraid].append(final_coo)
    end = time.time()
    print('end: ', end)
    print('time: ', (end - start))




