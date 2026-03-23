import math
import numpy as np
from numpy import cos, sin, pi, sqrt, deg2rad, rad2deg
from scipy import constants
import gdsfactory as gf
import mydraw


# 本文件用于折叠型AWG的版图设计

# NOTE: 所有结构参数单位均为um
c = constants.speed_of_light  # 光速
########################################################################################################################
# 器件性能参数
########################################################################################################################
lambda_center = 1.5  # 工作中心波长
channel_spacing = 0.02  # 通道间隔，单位dB
Lu = 0.2  # 通道均匀性，单位dB
order = 3  # 衍射级次
########################################################################################################################
# 输入、输出和阵列波导参数
########################################################################################################################
Nin = 1  # 输入波导数
N_channels = 25  # 输出波导数
Narray = 100  # 阵列波导数
neff = 1.62  # 阵列波导有效折射率
ng = 1.96  # 阵列波导群折射率
waveguide_width = 1.2  # 波导宽度
array_waveguide_spacing = 6  # 阵列波导间隔
Rmin = 700  # 阵列波导最小半径
output_length = 5  # 输入、输出波导长度
########################################################################################################################
# 星形耦合器参数
########################################################################################################################
neff_slab = 1.68  # 平板波导有效折射率
Ra = 800  # 罗兰圆半径（初始）
estimate_Ra_from_Lu = False  # 是否使用通道均匀性Lu计算罗兰圆半径Ra
theta_offset = deg2rad(35)  # 星形耦合器倾斜角度

AWG = gf.Component("AWG")  # 创建AWG容器

# 利用通道均匀性估算Ra
if estimate_Ra_from_Lu:
    theta_0 = lambda_center / neff_slab / (waveguide_width * sqrt(2 * pi))
    theta_max = sqrt(8.7 * Lu) * theta_0
    smax = Narray / 2 * array_waveguide_spacing
    Ra = smax / theta_max

# 计算阵列波导长度差ΔL
delta_L = order * lambda_center / neff

# 计算设计参数
m = order  # 衍射级次
da = array_waveguide_spacing
df = c / lambda_center ** 2 * channel_spacing
delta_alpha = da / Ra
dr = df * lambda_center / c * ng / neff_slab * delta_L / delta_alpha

########################################################################################################################
# 创建阵列波导
########################################################################################################################
array_width = waveguide_width
R = Rmin
wg_length_1 = 20  # 第一段直波导长度
wg_length_2 = 30  # 第二段直波导长度
wg_length_3 = 40  # 第三段直波导长度
bend_radius_1 = 50  # 第一段弯曲波导半径
bend_radius_2 = 100  # 第二段弯曲波导半径
for i in range(1, Narray + 1):
    theta = - da * (i - (Narray + 1) / 2) / Ra + theta_offset
    x1 = Ra * sin(theta) - Ra / 2 * sin(theta_offset)  # 阵列波导入口点 (x1, y1) 的坐标
    y1 = Ra * cos(theta) - Ra / 2 * cos(theta_offset)

    theta_span = theta  # 第一段弯曲波导弯曲角度
    L = last_length = (bend_radius_1 * theta_span + wg_length_2 + bend_radius_2 * pi/2 + wg_length_3) * 2
    x2 = x1 + wg_length_1 * sin(theta)  # 第一段直波导末端坐标(x2, y2)
    y2 = y1 + wg_length_1 * cos(theta)
    if theta > 0:
        x0 = x2 - R * cos(theta)
        y0 = y2 + R * sin(theta)
    else:
        x0 = x2 + R * cos(theta)
        y0 = y2 - R * sin(theta)
    buffer_angle = 2 * array_width / R
    test_length = theta_span * R
    L = last_length + delta_L
    dL = (L * cos(theta) - (x0 - x1) * theta_span) / (2 * cos(theta) - sin(theta) * theta_span)
    xp = x1 + dL * sin(theta)
    yp = y1 + dL * cos(theta)
    R = (x0 - xp) / cos(theta)
    y0 = yp - R * sin(theta)
    buffer_angle = 0
    test_length = 2 * sqrt((xp - x1) ** 2 + (yp - y1) ** 2) + theta_span * R
    # 绘制阵列波导弯曲部分
    array_bend = mydraw.ring_arc(radius=R, width=array_width,
                                 theta_start=rad2deg(theta - buffer_angle),
                                 theta_stop=180 - rad2deg(theta - buffer_angle),
                                 x_center=x0, y_center=y0, angle_resolution=1.0).copy()
    AWG.add_ref(array_bend)

    # 阵列波导左侧部分直波导
    x11 = x1 - 2 * array_width * sin(theta)
    y11 = y1 - 2 * array_width * cos(theta)
    xp1 = xp + 1e-3 * sin(theta)
    yp1 = yp + 1e-3 * cos(theta)
    xc = (x11 + xp1) / 2
    yc = (y11 + yp1) / 2
    x_span = array_width
    y_span = sqrt((x11 - xp1) ** 2 + (y11 - yp1) ** 2) + 2e-3

    theta = - theta  #
    v1 = [xc + x_span / 2 * cos(theta) + y_span / 2 * sin(theta),
          yc + x_span / 2 * sin(theta) - y_span / 2 * cos(theta)]
    v2 = [xc + x_span / 2 * cos(theta) - y_span / 2 * sin(theta),
          yc + x_span / 2 * sin(theta) + y_span / 2 * cos(theta)]
    v3 = [xc - x_span / 2 * cos(theta) - y_span / 2 * sin(theta),
          yc - x_span / 2 * sin(theta) + y_span / 2 * cos(theta)]
    v4 = [xc - x_span / 2 * cos(theta) + y_span / 2 * sin(theta),
          yc - x_span / 2 * sin(theta) - y_span / 2 * cos(theta)]
    vtx = [v1,
           v2,
           v3,
           v4]
    AWG.add_polygon(vtx, layer=(1, 0))

    # 阵列波导右侧部分直波导
    theta = - theta
    x11 = x1 - 2 * array_width * sin(theta)
    y11 = y1 - 2 * array_width * cos(theta)
    xp1 = xp + 1e-3 * sin(theta)
    yp1 = yp + 1e-3 * cos(theta)
    xc = 2 * x0 - ((x11 + xp1) / 2)
    x_span = array_width
    y_span = sqrt((x11 - xp1) ** 2 + (y11 - yp1) ** 2) + 2e-3
    yc = (y11 + yp1) / 2

    v1 = [xc + x_span / 2 * cos(theta) + y_span / 2 * sin(theta),
          yc + x_span / 2 * sin(theta) - y_span / 2 * cos(theta)]
    v2 = [xc + x_span / 2 * cos(theta) - y_span / 2 * sin(theta),
          yc + x_span / 2 * sin(theta) + y_span / 2 * cos(theta)]
    v3 = [xc - x_span / 2 * cos(theta) - y_span / 2 * sin(theta),
          yc - x_span / 2 * sin(theta) + y_span / 2 * cos(theta)]
    v4 = [xc - x_span / 2 * cos(theta) + y_span / 2 * sin(theta),
          yc - x_span / 2 * sin(theta) - y_span / 2 * cos(theta)]
    vtx = [v1,
           v2,
           v3,
           v4]
    AWG.add_polygon(vtx, layer=(1, 0))

    last_length = L

########################################################################################################################
# 创建星形耦合器区域
########################################################################################################################
input_width = waveguide_width
Nintemp = [Nin, N_channels]
xpos = [0, 2 * x0]
theta_offset_sign = [1, -1]
for j in range(0, 2):
    coupler = mydraw.sector(radius=Ra / 2, theta_start=180 - rad2deg(theta_offset * theta_offset_sign[j]),
                            theta_stop=360 - rad2deg(theta_offset * theta_offset_sign[j]),
                            x_center=xpos[j], y_center=0, angle_resolution=1.0).copy()
    AWG.add_ref(coupler)  # 扇形

    theta_max = (Narray + 10) * da / 2 / Ra
    if j == 0:
        theta_max = deg2rad(90)
    coupler = mydraw.sector(radius=Ra,
                            theta_start=90 - rad2deg(theta_max) - rad2deg(theta_offset * theta_offset_sign[j]),
                            theta_stop=90 + rad2deg(theta_max) - rad2deg(theta_offset * theta_offset_sign[j]),
                            x_center=-Ra / 2 * sin(theta_offset * theta_offset_sign[j]) + xpos[j],
                            y_center=-Ra / 2 * cos(theta_offset), angle_resolution=1.0).copy()
    AWG.add_ref(coupler)  # 扇形

    v1 = [xpos[j] + Ra / 2, 0]
    v2 = [xpos[j] + cos(pi / 2 - theta_max) * Ra, sin(pi / 2 - theta_max) * Ra - Ra / 2]
    v3 = [xpos[j] - cos(pi / 2 - theta_max) * Ra, sin(pi / 2 - theta_max) * Ra - Ra / 2]
    v4 = [xpos[j] - Ra / 2, 0]
    vtx = [v1,
           v2,
           v3,
           v4]
    vtx = np.array(vtx)
    angle_rotate = -theta_offset * theta_offset_sign[j]  # 设置旋转角度，单位弧度
    center = (vtx[0] + vtx[-1]) / 2  # 旋转中心
    shifted = vtx - center  # 平移到旋转点
    R = np.array([
        [cos(angle_rotate), -sin(angle_rotate)],
        [sin(angle_rotate), cos(angle_rotate)]
    ])  # 建立旋转矩阵
    rotated = shifted @ R.T + center  # 旋转并平移回去
    AWG.add_polygon(rotated, layer=(1, 0))

    L = output_length + Ra / 2
    for i in range(1, Nintemp[j] + 1):
        theta = dr * (i - (Nintemp[j] + 1) / 2) * 2 / Ra - theta_offset * theta_offset_sign[j]
        xc = L / 2 * sin(theta) + xpos[j]
        x_span = input_width
        y_span = L
        yc = -L / 2 * cos(theta)
        v1 = [xc + x_span / 2 * cos(theta) + y_span / 2 * sin(theta),
              yc + x_span / 2 * sin(theta) - y_span / 2 * cos(theta)]
        v2 = [xc + x_span / 2 * cos(theta) - y_span / 2 * sin(theta),
              yc + x_span / 2 * sin(theta) + y_span / 2 * cos(theta)]
        v3 = [xc - x_span / 2 * cos(theta) - y_span / 2 * sin(theta),
              yc - x_span / 2 * sin(theta) + y_span / 2 * cos(theta)]
        v4 = [xc - x_span / 2 * cos(theta) + y_span / 2 * sin(theta),
              yc - x_span / 2 * sin(theta) - y_span / 2 * cos(theta)]
        vtx = [v1,
               v2,
               v3,
               v4]
        AWG.add_polygon(vtx, layer=(1, 0))

AWG.show()
