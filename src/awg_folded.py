import gdsfactory as gf
import numpy as np
from numpy import cos, sin, pi, sqrt, deg2rad, rad2deg
import mydraw

order = 20               # 衍射级次
lambda_center = 1.55     # 工作中心波长
neff = 1.6092             # 阵列波导有效折射率
Narray = 50             # 阵列波导数
Ra = 690.72  # 罗兰圆半径
da = 5.6  # 阵列波导输入端口间隔
gap = 0.1 # 阵列波导出口间隙
waveguide_width = 2.5         # 波导宽度
N_channels = 16  # 输出波导数
# 计算阵列波导长度差ΔL
delta_L = order * lambda_center / neff
wi = 5  # 输入波导开口宽度
wo = 5  # 输出波导开口宽度
dr = 6.5  # 输出波导间距
L0 = 50  # 输入、输出波导长度

L1 = 50  # 第一段锥形波导长度
L2_0 = 0  # 第二段直波导长度，初始值
L3_0 = 0  # 第三段直波导长度，初始值
R1 = 200  # 第一段弯曲波导半径
R2 = 50  # 第二段弯曲波导半径

AWG = gf.Component("AWG")  # 创建AWG容器

array_width = waveguide_width

for i in range(1, Narray + 1):
    theta = - da * (i - (Narray + 1) / 2) / Ra  # 阵列波导倾斜角度
    x1 = Ra * sin(theta)  # 阵列波导端口坐标，原点为罗兰圆圆心
    y1 = Ra * cos(theta)

    # 阵列波导左侧部分第一段直波导，即锥形波导
    x_span = array_width  # taper短边宽度
    y_span_buffer = array_width
    x_span_taper = da - gap + (da - gap - x_span) / L1 * y_span_buffer  # taper长边宽度，需要延伸到星形耦合器内，延伸距离为阵列波导宽度
    y_span = L1
    v1 = [x1 - y_span_buffer * sin(theta) + x_span_taper / 2 * cos(theta),
          y1 - y_span_buffer * cos(theta) - x_span_taper / 2 * sin(theta)]
    v2 = [x1 - y_span_buffer * sin(theta) - x_span_taper / 2 * cos(theta),
          y1 - y_span_buffer * cos(theta) + x_span_taper / 2 * sin(theta)]
    v3 = [x1 + y_span * sin(theta) - x_span / 2 * cos(theta),
          y1 + y_span * cos(theta) + x_span / 2 * sin(theta)]
    v4 = [x1 + y_span * sin(theta) + x_span / 2 * cos(theta),
          y1 + y_span * cos(theta) - x_span / 2 * sin(theta)]
    vtx = [v1,
           v2,
           v3,
           v4]
    AWG.add_polygon(vtx, layer=(1, 0))

    # 阵列波导左侧部分第一段弯曲波导
    x2 = (Ra + L1) * sin(theta)  # 阵列波导第一段直波导端口坐标，原点为罗兰圆圆心
    y2 = (Ra + L1) * cos(theta)
    if theta > 0:
        x0 = x2 - R1 * cos(theta)  # 第一段弯曲波导圆心坐标(x0,y0)
        y0 = y2 + R1 * sin(theta)
        ring1 = mydraw.ring_arc(radius=R1, width=array_width,
                                theta_start=rad2deg(-theta), theta_stop=rad2deg(0),
                                x_center=x0, y_center=y0,
                                angle_resolution=0.5, layer=(1, 0))
    else:
        x0 = x2 + R1 * cos(-theta)  # 第一段弯曲波导圆心坐标(x0,y0)
        y0 = y2 + R1 * sin(-theta)
        ring1 = mydraw.ring_arc(radius=R1, width=array_width,
                                theta_start=rad2deg(pi), theta_stop=rad2deg(pi-theta),
                                x_center=x0, y_center=y0,
                                angle_resolution=0.5, layer=(1, 0))
    AWG.add_ref(ring1)

    if i == 1:
        L = 2 * (R1 * (da * (Narray/2 - 1/2) / Ra) + L2_0 + L3_0)  # 只记录不同的部分
        # 绘制第二段直波导
        x3 = x0 + R1
        y3 = y0
        x4 = x3
        y4 = y3 + L2_0
        wg2 = mydraw.waveguide(start=(x3, y3), end=(x4, y4), width=array_width, layer=(1, 0))
        AWG.add_ref(wg2)

        # 绘制第二段弯曲波导
        x5 = x4 + R2  # 弯曲波导圆心坐标
        y5 = y4
        ring2 = mydraw.ring_arc(radius=R2, width=array_width,
                                theta_start=rad2deg(pi / 2), theta_stop=rad2deg(pi),
                                x_center=x5, y_center=y5,
                                angle_resolution=1.0, layer=(1, 0))
        AWG.add_ref(ring2)

        # 绘制第三段直波导
        x6 = x5
        y6 = y5 + R2
        x7 = x6 + L3_0
        y7 = y6
        x_center = x7  # 阵列波导中心的x坐标
        wg3 = mydraw.waveguide(start=(x6, y6), end=(x7, y7), width=array_width, layer=(1, 0))
        AWG.add_ref(wg3)
    else:
        L = L + delta_L  # 阵列波导总长度
        # 绘制第二段直波导
        if theta > 0:
            x3 = x0 + R1
            y3 = y0
            L3 = x_center - x3 - R2
            L2 = L / 2 - L3 - R1 * (-da * (i - (Narray + 1) / 2) / Ra)
            x4 = x3
            y4 = y3 + L2
        else:
            x3 = x0 - R1
            y3 = y0
            L3 = x_center - x3 - R2
            L2 = L / 2 - L3 + R1 * (-da * (i - (Narray + 1) / 2) / Ra)
            x4 = x3
            y4 = y3 + L2
        wg2 = mydraw.waveguide(start=(x3, y3), end=(x4, y4), width=array_width, layer=(1, 0))
        AWG.add_ref(wg2)

        # 绘制第二段弯曲波导
        x5 = x4 + R2  # 弯曲波导圆心坐标
        y5 = y4
        ring2 = mydraw.ring_arc(radius=R2, width=array_width,
                                theta_start=rad2deg(pi/2), theta_stop=rad2deg(pi),
                                x_center=x5, y_center=y5,
                                angle_resolution=1.0, layer=(1, 0))
        AWG.add_ref(ring2)

        # 绘制第三段直波导
        x6 = x5
        y6 = y5 + R2
        x7 = x6 + L3
        y7 = y6
        wg3 = mydraw.waveguide(start=(x6, y6), end=(x7, y7), width=array_width, layer=(1, 0))
        AWG.add_ref(wg3)

for i in range(Narray, 0, -1):
    theta = - da * (i - (Narray + 1) / 2) / Ra  # 阵列波导倾斜角度
    x1 = Ra * sin(theta)  # 阵列波导端口坐标，原点为罗兰圆圆心
    y1 = Ra * cos(theta)

    # 阵列波导右侧部分第一段直波导，即锥形波导
    x_span = array_width
    y_span_buffer = array_width
    x_span_taper = da - gap + (da - gap - x_span) / L1 * y_span_buffer  # taper长边宽度，需要延伸到星形耦合器内，延伸距离为阵列波导宽度
    y_span = L1
    v1 = [x1 - y_span_buffer * sin(theta) + x_span_taper / 2 * cos(theta) + x_center * 2,
          y1 - y_span_buffer * cos(theta) - x_span_taper / 2 * sin(theta)]
    v2 = [x1 - y_span_buffer * sin(theta) - x_span_taper / 2 * cos(theta) + x_center * 2,
          y1 - y_span_buffer * cos(theta) + x_span_taper / 2 * sin(theta)]
    v3 = [x1 + y_span * sin(theta) - x_span / 2 * cos(theta) + x_center * 2,
          y1 + y_span * cos(theta) + x_span / 2 * sin(theta)]
    v4 = [x1 + y_span * sin(theta) + x_span / 2 * cos(theta) + x_center * 2,
          y1 + y_span * cos(theta) - x_span / 2 * sin(theta)]
    vtx = [v1,
           v2,
           v3,
           v4]
    AWG.add_polygon(vtx, layer=(1, 0))
    # 阵列波导左侧部分第一段弯曲波导
    x2 = (Ra + L1) * sin(theta) + x_center * 2  # 阵列波导第一段直波导端口坐标
    y2 = (Ra + L1) * cos(theta)
    if theta > 0:
        x0 = x2 - R1 * cos(theta)  # 第一段弯曲波导圆心坐标(x0,y0)
        y0 = y2 + R1 * sin(theta)
        ring1 = mydraw.ring_arc(radius=R1, width=array_width,
                                theta_start=rad2deg(-theta), theta_stop=rad2deg(0),
                                x_center=x0, y_center=y0,
                                angle_resolution=0.5, layer=(1, 0))
    else:
        x0 = x2 + R1 * cos(-theta)  # 第一段弯曲波导圆心坐标(x0,y0)
        y0 = y2 + R1 * sin(-theta)
        ring1 = mydraw.ring_arc(radius=R1, width=array_width,
                                theta_start=rad2deg(pi), theta_stop=rad2deg(pi - theta),
                                x_center=x0, y_center=y0,
                                angle_resolution=0.5, layer=(1, 0))
    AWG.add_ref(ring1)

    if i == Narray:
        L = 2 * (R1 * (da * (Narray / 2 - 1 / 2) / Ra) + L2_0 + L3_0)  # 只记录不同的部分
        # 绘制右侧第二段直波导
        x3 = x0 - R1
        y3 = y0
        x4 = x3
        y4 = y3 + L2_0
        wg2 = mydraw.waveguide(start=(x3, y3), end=(x4, y4), width=array_width, layer=(1, 0))
        AWG.add_ref(wg2)

        # 绘制第二段弯曲波导
        x5 = x4 - R2  # 弯曲波导圆心坐标
        y5 = y4
        ring2 = mydraw.ring_arc(radius=R2, width=array_width,
                                theta_start=rad2deg(0), theta_stop=rad2deg(pi/2),
                                x_center=x5, y_center=y5,
                                angle_resolution=1.0, layer=(1, 0))
        AWG.add_ref(ring2)

        # 绘制第三段直波导
        x6 = x5
        y6 = y5 + R2
        x7 = x6 - L3_0
        y7 = y6
        wg3 = mydraw.waveguide(start=(x6, y6), end=(x7, y7), width=array_width, layer=(1, 0))
        AWG.add_ref(wg3)
    else:
        L = L + delta_L  # 阵列波导总长度
        # 绘制第二段直波导
        if theta < 0:
            x3 = x0 - R1
            y3 = y0
            L3 = x3 - x_center - R2
            L2 = L / 2 - L3 + R1 * (-da * (i - (Narray + 1) / 2) / Ra)
            x4 = x3
            y4 = y3 + L2
        else:
            x3 = x0 + R1
            y3 = y0
            L3 = x3 - x_center - R2
            L2 = L / 2 - L3 - R1 * (-da * (i - (Narray + 1) / 2) / Ra)
            x4 = x3
            y4 = y3 + L2
        wg2 = mydraw.waveguide(start=(x3, y3), end=(x4, y4), width=array_width, layer=(1, 0))
        AWG.add_ref(wg2)

        # 绘制第二段弯曲波导
        x5 = x4 - R2  # 弯曲波导圆心坐标
        y5 = y4
        ring2 = mydraw.ring_arc(radius=R2, width=array_width,
                                theta_start=rad2deg(0), theta_stop=rad2deg(pi/2),
                                x_center=x5, y_center=y5,
                                angle_resolution=1.0, layer=(1, 0))
        AWG.add_ref(ring2)

        # 绘制第三段直波导
        x6 = x5
        y6 = y5 + R2
        x7 = x6 - L3
        y7 = y6
        wg3 = mydraw.waveguide(start=(x6, y6), end=(x7, y7), width=array_width, layer=(1, 0))
        AWG.add_ref(wg3)

# 绘制左侧星形耦合器
theta_buffer = deg2rad(10)
sector1 = mydraw.sector(radius=Ra,
                        angle_start=rad2deg(-da * (Narray/2 - 1/2) / Ra - theta_buffer + pi/2),
                        angle_stop=rad2deg(da * (Narray/2 - 1/2) / Ra + theta_buffer + pi/2),
                        x_center=0, y_center=0,
                        angle_resolution=1.0, layer=(1, 0))
AWG.add_ref(sector1)
theta_span = dr * (N_channels/2 - 1/2) * 2 / Ra
sector2 = mydraw.sector(radius=Ra/2,
                        angle_start=-90 - rad2deg(theta_span + theta_buffer),
                        angle_stop=-90 + rad2deg(theta_span + theta_buffer),
                        x_center=0, y_center=Ra/2,
                        angle_resolution=1.0, layer=(1, 0))
AWG.add_ref(sector2)
v1 = [Ra * cos(-da * (Narray/2 - 1/2) / Ra - theta_buffer + pi/2),
      Ra * sin(-da * (Narray/2 - 1/2) / Ra - theta_buffer + pi/2)]
v2 = [Ra * cos(da * (Narray/2 - 1/2) / Ra + theta_buffer + pi/2),
      Ra * sin(da * (Narray/2 - 1/2) / Ra + theta_buffer + pi/2)]
v3 = [Ra/2 * cos(-pi/2-theta_span-theta_buffer),
      Ra/2 + Ra/2 * sin(-pi/2-theta_span-theta_buffer)]
v4 = [Ra/2 * cos(-pi/2+theta_span+theta_buffer),
      Ra/2 + Ra/2 * sin(-pi/2+theta_span+theta_buffer)]
vtx = [v1,
       v2,
       v3,
       v4]
AWG.add_polygon(vtx, layer=(1, 0))

# 绘制右侧星形耦合器
theta_buffer = deg2rad(10)
sector1 = mydraw.sector(radius=Ra,
                        angle_start=rad2deg(-da * (Narray/2 - 1/2) / Ra - theta_buffer + pi/2),
                        angle_stop=rad2deg(da * (Narray/2 - 1/2) / Ra + theta_buffer + pi/2),
                        x_center=0 + x_center * 2, y_center=0,
                        angle_resolution=1.0, layer=(1, 0))
AWG.add_ref(sector1)
theta_span = dr * (N_channels/2 - 1/2) * 2 / Ra
sector2 = mydraw.sector(radius=Ra/2,
                        angle_start=-90-rad2deg(theta_span+theta_buffer),
                        angle_stop=-90+rad2deg(theta_span+theta_buffer),
                        x_center=0 + x_center * 2, y_center=Ra/2,
                        angle_resolution=1.0, layer=(1, 0))
AWG.add_ref(sector2)
v1 = [Ra * cos(-da * (Narray/2 - 1/2) / Ra - theta_buffer + pi/2) + x_center * 2,
      Ra * sin(-da * (Narray/2 - 1/2) / Ra - theta_buffer + pi/2)]
v2 = [Ra * cos(da * (Narray/2 - 1/2) / Ra + theta_buffer + pi/2) + x_center * 2,
      Ra * sin(da * (Narray/2 - 1/2) / Ra + theta_buffer + pi/2)]
v3 = [Ra/2 * cos(-pi/2-theta_span-theta_buffer) + x_center * 2,
      Ra/2 + Ra/2 * sin(-pi/2-theta_span-theta_buffer)]
v4 = [Ra/2 * cos(-pi/2+theta_span+theta_buffer) + x_center * 2,
      Ra/2 + Ra/2 * sin(-pi/2+theta_span+theta_buffer)]
vtx = [v1,
       v2,
       v3,
       v4]
AWG.add_polygon(vtx, layer=(1, 0))

input_width = output_width = waveguide_width
# 绘制输入波导
x_span = input_width  # taper短边宽度
y_span_buffer = input_width
x_span_taper = wi + (wi - x_span) / L0 * y_span_buffer  # taper长边宽度，需要延伸到星形耦合器内，延伸距离为阵列波导宽度
y_span = L0
v1 = [x1 - y_span_buffer * sin(theta) + x_span_taper / 2 * cos(theta),
      y1 - y_span_buffer * cos(theta) - x_span_taper / 2 * sin(theta)]
v2 = [x1 - y_span_buffer * sin(theta) - x_span_taper / 2 * cos(theta),
      y1 - y_span_buffer * cos(theta) + x_span_taper / 2 * sin(theta)]
v3 = [x1 + y_span * sin(theta) - x_span / 2 * cos(theta),
      y1 + y_span * cos(theta) + x_span / 2 * sin(theta)]
v4 = [x1 + y_span * sin(theta) + x_span / 2 * cos(theta),
      y1 + y_span * cos(theta) - x_span / 2 * sin(theta)]
vtx = [v1,
       v2,
       v3,
       v4]
AWG.add_polygon(vtx, layer=(1, 0))
v1 = [0+input_width/2, Ra/2]
v2 = [0-input_width/2, Ra/2]
v3 = [0-input_width/2, -L0]
v4 = [0+input_width/2, -L0]
vtx = [v1,
       v2,
       v3,
       v4]
AWG.add_polygon(vtx, layer=(1, 0))
# 绘制输出波导
for i in range(1, N_channels+1):
    theta = - dr * (i - (N_channels + 1) / 2) * 2 / Ra
    xc = 0 + (Ra/2+L0) * sin(theta) + x_center * 2
    yc = Ra/2 - (Ra/2+L0) * cos(theta)
    if theta > 0:
        v1 = [x_center * 2 + output_width/2 * cos(theta),
              Ra/2 + output_width/2 * sin(theta)]
        v2 = [x_center * 2 - output_width/2 * cos(theta),
              Ra/2 - output_width/2 * sin(theta)]
        v3 = [xc - output_width/2 * cos(theta),
              yc - output_width/2 * sin(theta)]
        v4 = [xc + output_width/2 * cos(theta),
              yc + output_width/2 * sin(theta)]
        vtx = [v1,
               v2,
               v3,
               v4]
        AWG.add_polygon(vtx, layer=(1, 0))
    else:
        theta = -theta
        v1 = [x_center * 2 + output_width / 2 * cos(theta),
              Ra / 2 - output_width / 2 * sin(theta)]
        v2 = [x_center * 2 - output_width / 2 * cos(theta),
              Ra / 2 + output_width / 2 * sin(theta)]
        v3 = [xc - output_width / 2 * cos(theta),
              yc + output_width / 2 * sin(theta)]
        v4 = [xc + output_width / 2 * cos(theta),
              yc - output_width / 2 * sin(theta)]
        vtx = [v1,
               v2,
               v3,
               v4]
        AWG.add_polygon(vtx, layer=(1, 0))

c = gf.boolean(A=AWG, B=AWG, operation="or", layer=(1, 0))
c.show()
# AWG.show()
