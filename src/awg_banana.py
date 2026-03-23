import math
import numpy as np
from numpy import cos, sin, pi, sqrt, deg2rad, rad2deg
from scipy import constants
import gdsfactory as gf
import mydraw

# 本文件用于香蕉形AWG的版图设计

# NOTE: 所有结构参数单位均为um
c = constants.speed_of_light  # 光速
########################################################################################################################
# 器件性能参数
########################################################################################################################
lambda_center = 1.55     # 工作中心波长
channel_spacing = 0.0032  # 通道间隔，单位um
Lu = 0.2                 # 通道均匀性，单位dB
order = 20               # 衍射级次
########################################################################################################################
# 输入、输出和阵列波导参数
########################################################################################################################
Nin = 1         # 输入波导数
N_channels = 16  # 输出波导数
Narray = 50     # 阵列波导数
neff = 1.6092   # 阵列波导有效折射率
ng = 1.9496    # 阵列波导群折射率
waveguide_width = 1.2         # 波导宽度
array_waveguide_spacing = 4  # 阵列波导间隔
Rmin = 60       # 阵列波导最小半径
output_length = 10  # 输入、输出波导长度
########################################################################################################################
# 星形耦合器参数
########################################################################################################################
neff_slab = 1.6739  # 平板波导有效折射率
Ra = 345.4093              # 罗兰圆半径（初始）
estimate_Ra_from_Lu = False   # 是否使用通道均匀性Lu计算罗兰圆半径Ra
theta_offset = deg2rad(0)   # 星形耦合器倾斜角度

AWG = gf.Component("AWG")  # 创建AWG容器

# 利用通道均匀性估算Ra
if estimate_Ra_from_Lu:
    theta_0 = lambda_center / neff_slab / (waveguide_width * sqrt(2*pi))
    theta_max = sqrt(8.7 * Lu) * theta_0
    # theta_max * 180 / pi
    smax = Narray / 2 * array_waveguide_spacing
    Ra = smax / theta_max

# 计算阵列波导长度差ΔL
delta_L = order * lambda_center / neff

array_pos = np.zeros((4, 1))  # x1, x2, y1, y2

# 计算设计参数
m = order  # 衍射级次
da = array_waveguide_spacing
df = c / lambda_center**2 * channel_spacing
delta_alpha = da / Ra
dr = df * lambda_center / c * ng / neff_slab * delta_L / delta_alpha
mprime = m * ng / neff
FSR_f = c / lambda_center / mprime
FSR_lambda = lambda_center ** 2 / c * FSR_f

########################################################################################################################
# 创建阵列波导
########################################################################################################################
array_width = waveguide_width
R = Rmin
for i in range(1, Narray+1):
    theta = -da * (i-(Narray+1) / 2) / Ra + theta_offset
    x1 = Ra * sin(theta)-Ra / 2 * sin(theta_offset)
    y1 = Ra * cos(theta)-Ra / 2 * cos(theta_offset)

    theta_span = pi - 2*theta
    if math.isclose(i, 1):
        L = last_length = R * theta_span
        x0 = x1+R * cos(theta)
        y0 = y1-R * sin(theta)
        xp = x1
        yp = y1
        buffer_angle = 2 * array_width / R
    else:
        L = last_length + delta_L
        dL = (L * cos(theta)-(x0-x1) * theta_span) / (2 * cos(theta)-sin(theta) * theta_span)
        xp = x1+dL * sin(theta)
        yp = y1+dL * cos(theta)
        R = (x0-xp) / cos(theta)
        y0 = yp - R * sin(theta)
        buffer_angle = 0

    # 绘制阵列波导弯曲部分
    array_bend = mydraw.ring_arc(radius=R, width=array_width,
                                 theta_start=rad2deg(theta-buffer_angle), theta_stop=180-rad2deg(theta-buffer_angle),
                                 x_center=x0, y_center=y0, angle_resolution=1.0).copy()
    AWG.add_ref(array_bend)

    if theta < 0:
        array_pos[0] = min([array_pos[0], x0-(R+array_width / 2)])
        array_pos[1] = max([array_pos[1], x0+(R+array_width / 2)])
    else:
        array_pos[0] = min([array_pos[0], x0+(R+array_width / 2) * cos(theta), x0+(R+array_width / 2) * cos(pi-theta)])
        array_pos[1] = max([array_pos[1], x0+(R+array_width / 2) * cos(theta), x0+(R+array_width / 2) * cos(pi-theta)])
    array_pos[2] = min([array_pos[2], y0+(R+array_width / 2) * sin(theta), y0+(R+array_width / 2) * sin(pi-theta)])
    array_pos[3] = max([array_pos[3], y0+(R+array_width / 2)])
    
    # 阵列波导左侧部分直波导
    x11 = x1 - 2 * array_width * sin(theta)
    y11 = y1 - 2 * array_width * cos(theta)
    xp1 = xp + 1e-3 * sin(theta)
    yp1 = yp + 1e-3 * cos(theta)
    xc = (x11+xp1) / 2
    yc = (y11+yp1) / 2
    x_span = array_width
    y_span = sqrt((x11-xp1) ** 2 + (y11-yp1) ** 2) + 2e-3

    theta = -theta
    v1 = [xc + x_span/2 * cos(theta) + y_span/2 * sin(theta), yc + x_span/2 * sin(theta) - y_span/2 * cos(theta)]
    v2 = [xc + x_span/2 * cos(theta) - y_span/2 * sin(theta), yc + x_span/2 * sin(theta) + y_span/2 * cos(theta)]
    v3 = [xc - x_span/2 * cos(theta) - y_span/2 * sin(theta), yc - x_span/2 * sin(theta) + y_span/2 * cos(theta)]
    v4 = [xc - x_span/2 * cos(theta) + y_span/2 * sin(theta), yc - x_span/2 * sin(theta) - y_span/2 * cos(theta)]
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
    xc = 2 * x0 - ((x11+xp1) / 2)
    x_span = array_width
    y_span = sqrt((x11-xp1) ** 2 + (y11-yp1) ** 2) + 2e-3
    yc = (y11+yp1) / 2

    v1 = [xc + x_span/2 * cos(theta) + y_span/2 * sin(theta), yc + x_span/2 * sin(theta) - y_span/2 * cos(theta)]
    v2 = [xc + x_span/2 * cos(theta) - y_span/2 * sin(theta), yc + x_span/2 * sin(theta) + y_span/2 * cos(theta)]
    v3 = [xc - x_span/2 * cos(theta) - y_span/2 * sin(theta), yc - x_span/2 * sin(theta) + y_span/2 * cos(theta)]
    v4 = [xc - x_span/2 * cos(theta) + y_span/2 * sin(theta), yc - x_span/2 * sin(theta) - y_span/2 * cos(theta)]
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
xpos = [0, 2*x0]
theta_offset_sign = [1, -1]
for j in range(0, 2):  # 分别绘制输入和输出FPR
    theta_max_down = (N_channels + 50) * dr / Ra
    coupler = mydraw.sector(radius=Ra/2,
                            angle_start=270-rad2deg(theta_offset * theta_offset_sign[j] + theta_max_down),
                            angle_stop=270-rad2deg(theta_offset * theta_offset_sign[j] - theta_max_down),
                            x_center=xpos[j], y_center=0, angle_resolution=1.0).copy()
    AWG.add_ref(coupler)  # 扇形

    theta_max_up = (Narray + 50) * da / 2 / Ra
    coupler = mydraw.sector(radius=Ra,
                            angle_start=90-rad2deg(theta_max_up)-rad2deg(theta_offset*theta_offset_sign[j]),
                            angle_stop=90 + rad2deg(theta_max_up)-rad2deg(theta_offset*theta_offset_sign[j]),
                            x_center=-Ra/2 * sin(theta_offset * theta_offset_sign[j]) + xpos[j],
                            y_center=-Ra/2 * cos(theta_offset), angle_resolution=1.0).copy()
    AWG.add_ref(coupler)  # 扇形

    # 绘制梯形
    v1 = [xpos[j] + Ra / 2 * cos(3 * pi/2 + theta_max_down),
          Ra / 2 * sin(3 * pi/2 + theta_max_down)]
    v2 = [xpos[j] + cos(pi / 2-theta_max_up) * Ra, sin(pi / 2-theta_max_up) * Ra-Ra / 2]
    v3 = [xpos[j] - cos(pi / 2-theta_max_up) * Ra, sin(pi / 2-theta_max_up) * Ra-Ra / 2]
    v4 = [xpos[j] + Ra / 2 * cos(3 * pi/2 - theta_max_down),
          Ra / 2 * sin(3 * pi/2 - theta_max_down)]
    # v1 = [xpos[j] + Ra / 2 * cos(3 * pi / 2 - (theta_offset * theta_offset_sign[j] - theta_max_down)),
    #       Ra / 2 * sin(3 * pi / 2 - (theta_offset * theta_offset_sign[j] - theta_max_down))]
    # v2 = [xpos[j] + cos(pi / 2 - theta_max_up) * Ra, sin(pi / 2 - theta_max_up) * Ra - Ra / 2]
    # v3 = [xpos[j] - cos(pi / 2 - theta_max_up) * Ra, sin(pi / 2 - theta_max_up) * Ra - Ra / 2]
    # v4 = [xpos[j] + Ra / 2 * cos(3 * pi / 2 - (theta_offset * theta_offset_sign[j] + theta_max_down)),
    #       Ra / 2 * sin(3 * pi / 2 - (theta_offset * theta_offset_sign[j] + theta_max_down))]
    vtx = [v1,
           v2,
           v3,
           v4]
    vtx = np.array(vtx)
    angle_rotate = -theta_offset * theta_offset_sign[j]  # 设置旋转角度，单位弧度
    # center = (vtx[0] + vtx[-1]) / 2  # 旋转中心
    center = [xpos[j] + Ra / 2 * cos(3 * pi/2), Ra / 2 * sin(3 * pi/2)]
    shifted = vtx - center  # 平移到旋转点
    R = np.array([
        [cos(angle_rotate), -sin(angle_rotate)],
        [sin(angle_rotate), cos(angle_rotate)]
    ])  # 建立旋转矩阵
    rotated = shifted @ R.T  # 旋转并平移回去
    AWG.add_polygon(rotated, layer=(1, 0))

    L = output_length + Ra / 2
    for i in range(1, Nintemp[j]+1):
        theta = dr * (i - (Nintemp[j] + 1) / 2) * 2 / Ra - theta_offset * theta_offset_sign[j]
        xc = L / 2 * sin(theta) + xpos[j]
        x_span = input_width
        y_span = L
        yc = -L / 2 * cos(theta)
        v1 = [xc + x_span/2 * cos(theta) + y_span/2 * sin(theta), yc + x_span/2 * sin(theta) - y_span/2 * cos(theta)]
        v2 = [xc + x_span/2 * cos(theta) - y_span/2 * sin(theta), yc + x_span/2 * sin(theta) + y_span/2 * cos(theta)]
        v3 = [xc - x_span/2 * cos(theta) - y_span/2 * sin(theta), yc - x_span/2 * sin(theta) + y_span/2 * cos(theta)]
        v4 = [xc - x_span/2 * cos(theta) + y_span/2 * sin(theta), yc - x_span/2 * sin(theta) - y_span/2 * cos(theta)]
        vtx = [v1,
               v2,
               v3,
               v4]
        AWG.add_polygon(vtx, layer=(1, 0))

# c = gf.boolean(A=AWG, B=AWG, operation="or", layer=(1, 0))
# c.show()
AWG.show()
