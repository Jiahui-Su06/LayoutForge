# 本文件用于AWG器件版图设计
import numpy as np
import math
from numpy import cos, sin, tan, pi, sqrt, deg2rad, rad2deg
import matplotlib.pyplot as plt

# 注意：选择AWG参数时，应使各阵列波导弯曲半径尽可能接近，从而在一定程度上减少器件尺寸

Narray = 30  # 阵列波导数
m = 3  # 衍射级次
lambda_c = 1.5  # 工作中心波长
neff = 1.62  # 阵列波导有效折射率
Ra = 800  # FPR长度
delta_L = m*lambda_c/neff/2  # 阵列波导总长度差一半
# delta_L = 78.6
delta_H = 10  # 阵列波导第二段直波导间距
da = 6  # 阵列波导中心间距
theta_offset = deg2rad(85)  # 星形耦合器倾斜角度
waveguide_width = 1.2  # 波导宽度

# 初始化声明
L1 = np.zeros(Narray)  # 第一段直波导长度
L2 = np.zeros(Narray)  # 第二段直波导长度
theta = np.zeros(Narray)  # 阵列波导起始角度
R = np.zeros(Narray)  # 阵列波导弯曲部分半径
H = np.zeros(Narray)  # 阵列波导第二段直波导间距
# 计算阵列波导倾斜角度

L1[0] = 3000  # 直波导L1的初始长度
L2[0] = 5000    # 直波导L2的初始长度
theta[0] = deg2rad(80)  # 罗兰圆倾斜初始角
R[0] = 1000  # 初始弯曲波导半径
D = 2 * ((Ra + L1[0]) * cos(theta[0]) + R[0] * sin(theta[0]) + L2[0])  # 输入/输出自由传输区顶点间距
H[0] = (L1[0] + Ra) * sin(theta[0]) + R[0] * (1 - cos(theta[0]))  # 阵列波导初始高度
L_0 = 2 * (L1[0] + L2[0] + R[0]*theta[0])  # 阵列波导第一根总长度

for i in range(1, Narray+1):
    theta[i-1] = - da * (i - (Narray + 1)/2) / Ra + theta_offset

for i in range(1, Narray):
    H[i] = H[i-1] + delta_H
    R[i] = (L_0 / 2 + i * delta_L - H[i] * tan(theta[i]/2) - D / 2 + Ra) / (theta[i] - 2 * tan(theta[i] / 2))
    L1[i] = H[i] / sin(theta[i]) - Ra - R[i] * tan(theta[i] / 2)
    L2[i] = D / 2 - (L1[i] + Ra) * cos(theta[i]) - R[i] * sin(theta[i])

channel = np.arange(1, Narray + 1)

# 绘制L1 - i关系图
plt.subplot(2, 2, 1)   # 第 1 个子图
plt.plot(channel, L1, "o", markerfacecolor="none")
plt.xlabel("Channel#")
plt.ylabel("L1")
plt.title("L1 - Channel")
plt.xlim(1, Narray)

# 绘制L2 - i关系图
plt.subplot(2, 2, 2)   # 第 1 个子图
plt.plot(channel, L2, "o", markerfacecolor="none")
plt.xlabel("Channel#")
plt.ylabel("L2")
plt.title("L2 - Channel")
plt.xlim(1, Narray)

# 绘制R - i关系图
plt.subplot(2, 2, 3)
plt.plot(channel, R, "o", markerfacecolor="none")
plt.xlabel("Channel#")
plt.ylabel("R")
plt.title("R - Channel")
plt.xlim(1, Narray)

plt.subplot(2, 2, 4)
plt.plot(channel, rad2deg(theta), "o", markerfacecolor="none")
plt.xlabel("Channel#")
plt.ylabel("theta")
plt.title("theta - Channel")
plt.xlim(1, Narray)

plt.show()

array_width = waveguide_width
R = Rmin
array_pos[2] = 1e20
# 绘制AWG版图
for i in range(1, Narray + 1):
    theta = - da * (i - (Narray + 1) / 2) / Ra + theta_offset
    x1 = Ra * sin(theta) - Ra / 2 * sin(theta_offset)
    y1 = Ra * cos(theta) - Ra / 2 * cos(theta_offset)

    theta_span = pi - 2 * theta
    if math.isclose(i, 1):
        L = last_length = R * theta_span
        x0 = x1 + R * cos(theta)
        y0 = y1 - R * sin(theta)
        xp = x1
        yp = y1
        buffer_angle = 2 * array_width / R
        test_length = theta_span * R
    else:
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

    if theta < 0:
        array_pos[0] = min([array_pos[0], x0 - (R + array_width / 2)])
        array_pos[1] = max([array_pos[1], x0 + (R + array_width / 2)])
    else:
        array_pos[0] = min(
            [array_pos[0], x0 + (R + array_width / 2) * cos(theta), x0 + (R + array_width / 2) * cos(pi - theta)])
        array_pos[1] = max(
            [array_pos[1], x0 + (R + array_width / 2) * cos(theta), x0 + (R + array_width / 2) * cos(pi - theta)])
    array_pos[2] = min(
        [array_pos[2], y0 + (R + array_width / 2) * sin(theta), y0 + (R + array_width / 2) * sin(pi - theta)])
    array_pos[3] = max([array_pos[3], y0 + (R + array_width / 2)])

    # 阵列波导左侧部分直波导
    x11 = x1 - 2 * array_width * sin(theta)
    y11 = y1 - 2 * array_width * cos(theta)
    xp1 = xp + 1e-3 * sin(theta)
    yp1 = yp + 1e-3 * cos(theta)
    xc = (x11 + xp1) / 2
    yc = (y11 + yp1) / 2
    x_span = array_width
    y_span = sqrt((x11 - xp1) ** 2 + (y11 - yp1) ** 2) + 2e-3

    theta = -theta
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
    theta = -theta
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
