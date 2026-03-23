import gdsfactory as gf
import numpy as np
from numpy import cos, sin, pi, sqrt, deg2rad, rad2deg
import mydraw

order = 2              # 衍射级次
lambda_center = 1.55     # 工作中心波长
neff = 1.6092             # 阵列波导有效折射率
Narray = 42             # 阵列波导数，需为偶数，奇数需测试
Ra = 150  # 罗兰圆半径
# da = 2.04  # 阵列波导输入端口间隔
da = 3.2  # 阵列波导输入端口间隔
gap = 0.2 # 阵列波导出口间隙
waveguide_width = 1         # 波导宽度
N_channels = 24  # 输出波导数
# 计算阵列波导长度差ΔL
delta_L = order * lambda_center / neff
wi = 3.3  # 输入波导开口宽度
wo = 3.3  # 输出波导开口宽度
dr = 1.534  # 输出波导间距
L0 = 10  # 输入、输出波导长度

L1 = 75  # 第一段直波导长度
R1 = 100  # 第一段弯曲波导半径
L2_0 = 200  # 第二段直波导长度，初始值
R2 = 100  # 第二段弯曲波导半径
L3_0 = 0  # 第三段直波导长度，初始值
R3 = 100  # 第三段弯曲波导半径
L4_0 = 0  # 第四段直波导长度，初始值

AWG = gf.Component("AWG")  # 创建AWG容器

array_width = waveguide_width

# 绘制左侧星形耦合器
theta_buffer = deg2rad(10)
sector1 = mydraw.sector(radius=Ra,
                        angle_start=rad2deg(-da * (Narray/2 - 1/2) / Ra - theta_buffer),
                        angle_stop=rad2deg(da * (Narray/2 - 1/2) / Ra + theta_buffer),
                        x_center=0, y_center=0,
                        angle_resolution=1.0, layer=(1, 0))
AWG.add_ref(sector1)
theta_span = dr * (N_channels/2 - 1/2) * 2 / Ra
sector2 = mydraw.sector(radius=Ra/2,
                        angle_start=180 - rad2deg(theta_span + theta_buffer),
                        angle_stop=180 + rad2deg(theta_span + theta_buffer),
                        x_center=Ra/2, y_center=0,
                        angle_resolution=1.0, layer=(1, 0))
AWG.add_ref(sector2)
v1 = [Ra * cos(-da * (Narray/2 - 1/2) / Ra - theta_buffer),
      Ra * sin(-da * (Narray/2 - 1/2) / Ra - theta_buffer)]
v2 = [Ra * cos(da * (Narray/2 - 1/2) / Ra + theta_buffer),
      Ra * sin(da * (Narray/2 - 1/2) / Ra + theta_buffer)]
v3 = [Ra/2 + Ra/2 * cos(pi-theta_span-theta_buffer),
      Ra/2 * sin(pi-theta_span-theta_buffer)]
v4 = [Ra/2 + Ra/2 * cos(pi+theta_span+theta_buffer),
      Ra/2 * sin(pi+theta_span+theta_buffer)]
vtx = [v1,
       v2,
       v3,
       v4]
AWG.add_polygon(vtx, layer=(1, 0))

for i in range(1, Narray + 1):
    theta = - da * (i - (Narray + 1) / 2) / Ra  # 阵列波导偏离中线角度
    x1 = Ra * cos(theta)  # 阵列波导端口坐标，原点为罗兰圆圆心
    y1 = -Ra * sin(theta)

    # 阵列波导左侧部分第一段直波导，即锥形波导
    x_span = array_width  # taper短边宽度
    y_span_buffer = array_width
    x_span_taper = da - gap + (da - gap - x_span) / L1 * y_span_buffer  # taper长边宽度，需要延伸到星形耦合器内，延伸距离为阵列波导宽度
    y_span = L1
    v1 = [x1 - y_span_buffer * cos(theta) - x_span_taper / 2 * sin(theta),
          y1 + y_span_buffer * sin(theta) - x_span_taper / 2 * cos(theta)]
    v2 = [x1 - y_span_buffer * cos(theta) + x_span_taper / 2 * sin(theta),
          y1 + y_span_buffer * sin(theta) + x_span_taper / 2 * cos(theta)]
    v3 = [x1 + y_span * cos(theta) + x_span / 2 * sin(theta),
          y1 - y_span * sin(theta) + x_span / 2 * cos(theta)]
    v4 = [x1 + y_span * cos(theta) - x_span / 2 * sin(theta),
          y1 - y_span * sin(theta) - x_span / 2 * cos(theta)]
    vtx = [v1,
           v2,
           v3,
           v4]
    AWG.add_polygon(vtx, layer=(1, 0))

    # 阵列波导左侧部分第一段弯曲波导
    x2 = (Ra + L1) * cos(theta)  # 阵列波导第一段直波导端口坐标，原点为罗兰圆圆心
    y2 = -(Ra + L1) * sin(theta)
    if theta > 0:
        x0 = x2 + R1 * sin(theta)  # 第一段弯曲波导圆心坐标(x0,y0)
        y0 = y2 + R1 * cos(theta)
        ring1 = mydraw.ring_arc(radius=R1, width=array_width,
                                theta_start=rad2deg(-pi/2-theta), theta_stop=rad2deg(-pi/2),
                                x_center=x0, y_center=y0,
                                angle_resolution=0.5, layer=(1, 0))
    else:
        x0 = x2 + R1 * sin(-theta)  # 第一段弯曲波导圆心坐标(x0,y0)
        y0 = y2 - R1 * cos(-theta)
        ring1 = mydraw.ring_arc(radius=R1, width=array_width,
                                theta_start=rad2deg(pi/2), theta_stop=rad2deg(pi/2 - theta),
                                x_center=x0, y_center=y0,
                                angle_resolution=0.5, layer=(1, 0))
    AWG.add_ref(ring1)

    if i == 1:
        L = 2 * (R1 * (da * (Narray / 2 - 1 / 2) / Ra) + L2_0 + L3_0 + L4_0)  # 只记录不同的部分
        # 绘制第二段直波导
        x3 = x0
        y3 = y0 - R1
        y_temp = y3  # 临时值，用于计算第三段直波导位置坐标
        x4 = x3 + L2_0
        y4 = y3
        wg2 = mydraw.waveguide(start=(x3, y3), end=(x4, y4), width=array_width, layer=(1, 0))
        AWG.add_ref(wg2)

        # 绘制第二段弯曲波导
        x5 = x4  # 弯曲波导圆心坐标
        y5 = y4 + R2
        ring2 = mydraw.ring_arc(radius=R2, width=array_width,
                                theta_start=rad2deg(-pi / 2), theta_stop=rad2deg(0),
                                x_center=x5, y_center=y5,
                                angle_resolution=1.0, layer=(1, 0))
        AWG.add_ref(ring2)

        # 绘制第三段直波导
        x6 = x5 + R2
        y6 = y5
        x_temp = x6  # 临时值，用于计算第三段直波导位置坐标
        x7 = x6
        y7 = y6 + L3_0
        wg3 = mydraw.waveguide(start=(x6, y6), end=(x7, y7), width=array_width, layer=(1, 0))
        AWG.add_ref(wg3)

        # 绘制第三段弯曲波导
        x8 = x7 + R3  # 弯曲波导圆心坐标
        y8 = y7
        ring3 = mydraw.ring_arc(radius=R3, width=array_width,
                                theta_start=rad2deg(pi/2), theta_stop=rad2deg(pi),
                                x_center=x8, y_center=y8,
                                angle_resolution=1.0, layer=(1, 0))
        AWG.add_ref(ring3)

        # 绘制第四段直波导
        x9 = x8
        y9 = y8 + R3
        x10 = x9 + L4_0
        y10 = y9
        x_center = x10  # 阵列波导中心的x坐标
        wg4 = mydraw.waveguide(start=(x9, y9), end=(x10, y10), width=array_width, layer=(1, 0))
        AWG.add_ref(wg4)
    else:
        L = L + delta_L  # 阵列波导总长度
        const = x_center - x0 - R2 - R3  # L2 + L4

        # 绘制第三段直波导
        if theta > 0:
            L3 = L / 2 - R1 * theta - const
            x3 = x0
            y3 = y0 - R1
            delta_y = y3 - y_temp
            x6 = x_temp - delta_y  # 第三段直波导起始坐标
            y6 = y3 + R2
            y_temp = y3  # 临时值，用于计算第三段直波导位置坐标
            x_temp = x6
            x7 = x6  # 第三段直波导终止坐标
            y7 = y6 + L3
            wg3 = mydraw.waveguide(start=(x6, y6), end=(x7, y7), width=array_width, layer=(1, 0))
            AWG.add_ref(wg3)
            x4 = x6 - R2
            y4 = y6 - R2
            L2 = x4 - x3
            wg2 = mydraw.waveguide(start=(x3, y3), end=(x4, y4), width=array_width, layer=(1, 0))
            AWG.add_ref(wg2)
            L4 = const - L2
            x9 = x7 + R3
            y9 = y7 + R3
            x10 = x9 + L4
            y10 = y9
            wg4 = mydraw.waveguide(start=(x9, y9), end=(x10, y10), width=array_width, layer=(1, 0))
            AWG.add_ref(wg4)
            x5 = x4
            y5 = y6
            ring2 = mydraw.ring_arc(radius=R2, width=array_width,
                                    theta_start=rad2deg(-pi / 2), theta_stop=rad2deg(0),
                                    x_center=x5, y_center=y5,
                                    angle_resolution=1.0, layer=(1, 0))
            AWG.add_ref(ring2)
            x8 = x9
            y8 = y7
            ring3 = mydraw.ring_arc(radius=R3, width=array_width,
                                    theta_start=rad2deg(pi / 2), theta_stop=rad2deg(pi),
                                    x_center=x8, y_center=y8,
                                    angle_resolution=1.0, layer=(1, 0))
            AWG.add_ref(ring3)
        else:
            L3 = L / 2 + R1 * theta - const
            x3 = x0
            y3 = y0 + R1
            delta_y = y3 - y_temp
            x6 = x_temp - delta_y  # 第三段直波导起始坐标
            y6 = y3 + R2
            y_temp = y3  # 临时值，用于计算第三段直波导位置坐标
            x_temp = x6
            x7 = x6  # 第三段直波导终止坐标
            y7 = y6 + L3
            wg3 = mydraw.waveguide(start=(x6, y6), end=(x7, y7), width=array_width, layer=(1, 0))
            AWG.add_ref(wg3)
            x4 = x6 - R2
            y4 = y6 - R2
            L2 = x4 - x3
            wg2 = mydraw.waveguide(start=(x3, y3), end=(x4, y4), width=array_width, layer=(1, 0))
            AWG.add_ref(wg2)
            L4 = const - L2
            x9 = x7 + R3
            y9 = y7 + R3
            x10 = x9 + L4
            y10 = y9
            wg4 = mydraw.waveguide(start=(x9, y9), end=(x10, y10), width=array_width, layer=(1, 0))
            AWG.add_ref(wg4)
            x5 = x4
            y5 = y6
            ring2 = mydraw.ring_arc(radius=R2, width=array_width,
                                    theta_start=rad2deg(-pi / 2), theta_stop=rad2deg(0),
                                    x_center=x5, y_center=y5,
                                    angle_resolution=1.0, layer=(1, 0))
            AWG.add_ref(ring2)
            x8 = x9
            y8 = y7
            ring3 = mydraw.ring_arc(radius=R3, width=array_width,
                                    theta_start=rad2deg(pi / 2), theta_stop=rad2deg(pi),
                                    x_center=x8, y_center=y8,
                                    angle_resolution=1.0, layer=(1, 0))
            AWG.add_ref(ring3)

# 绘制右侧星形耦合器
theta_buffer = deg2rad(10)
sector1 = mydraw.sector(radius=Ra,
                        angle_start=rad2deg(-da * (Narray/2 - 1/2) / Ra - theta_buffer + pi),
                        angle_stop=rad2deg(da * (Narray/2 - 1/2) / Ra + theta_buffer + pi),
                        x_center=2 * x_center, y_center=0,
                        angle_resolution=1.0, layer=(1, 0))
AWG.add_ref(sector1)
theta_span = dr * (N_channels/2 - 1/2) * 2 / Ra
sector2 = mydraw.sector(radius=Ra/2,
                        angle_start=0 + rad2deg(-theta_span - theta_buffer),
                        angle_stop=0 + rad2deg(theta_span + theta_buffer),
                        x_center=2 * x_center - Ra/2, y_center=0,
                        angle_resolution=1.0, layer=(1, 0))
AWG.add_ref(sector2)
v1 = [2 * x_center + Ra * cos(-da * (Narray/2 - 1/2) / Ra - theta_buffer + pi),
      Ra * sin(-da * (Narray/2 - 1/2) / Ra - theta_buffer + pi)]
v2 = [2 * x_center + Ra * cos(da * (Narray/2 - 1/2) / Ra + theta_buffer + pi),
      Ra * sin(da * (Narray/2 - 1/2) / Ra + theta_buffer + pi)]
v3 = [2 * x_center - Ra/2 + Ra/2 * cos(-theta_span - theta_buffer),
      Ra/2 * sin(-theta_span - theta_buffer)]
v4 = [2 * x_center - Ra/2 + Ra/2 * cos(theta_span + theta_buffer),
      Ra/2 * sin(theta_span + theta_buffer)]
vtx = [v1,
       v2,
       v3,
       v4]
AWG.add_polygon(vtx, layer=(1, 0))

for i in range(Narray, 0, -1):
    theta = - da * (i - (Narray + 1) / 2) / Ra  # 阵列波导倾斜角度
    x1 = 2 * x_center - Ra * cos(theta)  # 阵列波导端口坐标，原点为罗兰圆圆心
    y1 = Ra * sin(theta)

    # 阵列波导右侧部分第一段直波导
    x_span = array_width
    y_span_buffer = array_width
    x_span_taper = da - gap + (da - gap - x_span) / L1 * y_span_buffer  # taper长边宽度，需要延伸到星形耦合器内，延伸距离为阵列波导宽度
    y_span = L1
    v1 = [x1 + y_span_buffer * cos(theta) - x_span_taper / 2 * sin(theta),
          y1 - y_span_buffer * sin(theta) - x_span_taper / 2 * cos(theta)]
    v2 = [x1 + y_span_buffer * cos(theta) + x_span_taper / 2 * sin(theta),
          y1 - y_span_buffer * sin(theta) + x_span_taper / 2 * cos(theta)]
    v3 = [x1 - y_span * cos(theta) + x_span / 2 * sin(theta),
          y1 + y_span * sin(theta) + x_span / 2 * cos(theta)]
    v4 = [x1 - y_span * cos(theta) - x_span / 2 * sin(theta),
          y1 + y_span * sin(theta) - x_span / 2 * cos(theta)]
    vtx = [v1,
           v2,
           v3,
           v4]
    AWG.add_polygon(vtx, layer=(1, 0))

    # 阵列波导右侧部分第一段弯曲波导
    x2 = 2 * x_center - (Ra + L1) * cos(theta)  # 阵列波导第一段直波导端口坐标
    y2 = (Ra + L1) * sin(theta)

    if theta < 0:
        x0 = x2 + R1 * sin(theta)  # 第一段弯曲波导圆心坐标(x0,y0)
        y0 = y2 + R1 * cos(theta)
        ring1 = mydraw.ring_arc(radius=R1, width=array_width,
                                theta_start=rad2deg(-pi/2), theta_stop=rad2deg(-pi/2 - theta),
                                x_center=x0, y_center=y0,
                                angle_resolution=0.5, layer=(1, 0))
    else:
        x0 = x2 - R1 * sin(theta)  # 第一段弯曲波导圆心坐标(x0,y0)
        y0 = y2 - R1 * cos(theta)
        ring1 = mydraw.ring_arc(radius=R1, width=array_width,
                                theta_start=rad2deg(pi / 2 - theta), theta_stop=rad2deg(pi / 2),
                                x_center=x0, y_center=y0,
                                angle_resolution=0.5, layer=(1, 0))
    AWG.add_ref(ring1)

    if i == Narray:
        L = 2 * (R1 * (da * (Narray / 2 - 1 / 2) / Ra) + L2_0 + L3_0 + L4_0)  # 只记录不同的部分
        # 绘制第二段直波导
        x3 = x0
        y3 = y0 - R1
        y_temp = y3  # 临时值，用于计算第三段直波导位置坐标
        x4 = x3 - L2_0
        y4 = y3
        wg2 = mydraw.waveguide(start=(x3, y3), end=(x4, y4), width=array_width, layer=(1, 0))
        AWG.add_ref(wg2)

        # 绘制第二段弯曲波导
        x5 = x4  # 弯曲波导圆心坐标
        y5 = y4 + R2
        ring2 = mydraw.ring_arc(radius=R2, width=array_width,
                                theta_start=rad2deg(-pi), theta_stop=rad2deg(-pi/2),
                                x_center=x5, y_center=y5,
                                angle_resolution=1.0, layer=(1, 0))
        AWG.add_ref(ring2)

        # 绘制第三段直波导
        x6 = x5 - R2
        y6 = y5
        x_temp = x6  # 临时值，用于计算第三段直波导位置坐标
        x7 = x6
        y7 = y6 + L3_0
        wg3 = mydraw.waveguide(start=(x6, y6), end=(x7, y7), width=array_width, layer=(1, 0))
        AWG.add_ref(wg3)

        # 绘制第三段弯曲波导
        x8 = x7 - R3  # 弯曲波导圆心坐标
        y8 = y7
        ring3 = mydraw.ring_arc(radius=R3, width=array_width,
                                theta_start=rad2deg(0), theta_stop=rad2deg(pi/2),
                                x_center=x8, y_center=y8,
                                angle_resolution=1.0, layer=(1, 0))
        AWG.add_ref(ring3)

        # 绘制第四段直波导
        x9 = x8
        y9 = y8 + R3
        x10 = x9 - L4_0
        y10 = y9
        wg4 = mydraw.waveguide(start=(x9, y9), end=(x10, y10), width=array_width, layer=(1, 0))
        AWG.add_ref(wg4)
    else:
        L = L + delta_L  # 阵列波导总长度
        const = x0 - x_center - R2 - R3  # L2 + L4

        # 绘制第三段直波导
        if theta < 0:
            L3 = L / 2 + R1 * theta - const
            x3 = x0
            y3 = y0 - R1
            delta_y = y3 - y_temp
            x6 = x_temp + delta_y  # 第三段直波导起始坐标
            y6 = y3 + R2
            y_temp = y3  # 临时值，用于计算第三段直波导位置坐标
            x_temp = x6
            x7 = x6  # 第三段直波导终止坐标
            y7 = y6 + L3
            wg3 = mydraw.waveguide(start=(x6, y6), end=(x7, y7), width=array_width, layer=(1, 0))
            AWG.add_ref(wg3)
            x4 = x6 + R2
            y4 = y6 - R2
            L2 = x3 - x4
            wg2 = mydraw.waveguide(start=(x4, y4), end=(x3, y3), width=array_width, layer=(1, 0))
            AWG.add_ref(wg2)
            L4 = const - L2
            x9 = x7 - R3
            y9 = y7 + R3
            x10 = x9 - L4
            y10 = y9
            wg4 = mydraw.waveguide(start=(x10, y10), end=(x9, y9), width=array_width, layer=(1, 0))
            AWG.add_ref(wg4)
            x5 = x4
            y5 = y6
            ring2 = mydraw.ring_arc(radius=R2, width=array_width,
                                    theta_start=rad2deg(-pi), theta_stop=rad2deg(-pi/2),
                                    x_center=x5, y_center=y5,
                                    angle_resolution=1.0, layer=(1, 0))
            AWG.add_ref(ring2)
            x8 = x9
            y8 = y7
            ring3 = mydraw.ring_arc(radius=R3, width=array_width,
                                    theta_start=rad2deg(0), theta_stop=rad2deg(pi/2),
                                    x_center=x8, y_center=y8,
                                    angle_resolution=1.0, layer=(1, 0))
            AWG.add_ref(ring3)
        else:
            L3 = L / 2 - R1 * theta - const
            x3 = x0
            y3 = y0 + R1
            delta_y = y3 - y_temp
            x6 = x_temp + delta_y  # 第三段直波导起始坐标
            y6 = y3 + R2
            y_temp = y3  # 临时值，用于计算第三段直波导位置坐标
            x_temp = x6
            x7 = x6  # 第三段直波导终止坐标
            y7 = y6 + L3
            wg3 = mydraw.waveguide(start=(x6, y6), end=(x7, y7), width=array_width, layer=(1, 0))
            AWG.add_ref(wg3)
            x4 = x6 + R2
            y4 = y6 - R2
            L2 = x3 - x4
            wg2 = mydraw.waveguide(start=(x4, y4), end=(x3, y3), width=array_width, layer=(1, 0))
            AWG.add_ref(wg2)
            L4 = const - L2
            x9 = x7 - R3
            y9 = y7 + R3
            x10 = x9 - L4
            y10 = y9
            wg4 = mydraw.waveguide(start=(x10, y10), end=(x9, y9), width=array_width, layer=(1, 0))
            AWG.add_ref(wg4)
            x5 = x4
            y5 = y6
            ring2 = mydraw.ring_arc(radius=R2, width=array_width,
                                    theta_start=rad2deg(-pi), theta_stop=rad2deg(-pi / 2),
                                    x_center=x5, y_center=y5,
                                    angle_resolution=1.0, layer=(1, 0))
            AWG.add_ref(ring2)
            x8 = x9
            y8 = y7
            ring3 = mydraw.ring_arc(radius=R3, width=array_width,
                                    theta_start=rad2deg(0), theta_stop=rad2deg(pi / 2),
                                    x_center=x8, y_center=y8,
                                    angle_resolution=1.0, layer=(1, 0))
            AWG.add_ref(ring3)

# 绘制输入波导
input_width = output_width = waveguide_width
v1 = [Ra/2, 0-input_width/2]
v2 = [Ra/2, 0+input_width/2]
v3 = [0-L0, 0+input_width/2]
v4 = [0-L0, 0-input_width/2]
vtx = [v1,
       v2,
       v3,
       v4]
AWG.add_polygon(vtx, layer=(1, 0))
# 绘制输出波导
for i in range(1, N_channels+1):
    theta = - dr * (i - (N_channels + 1) / 2) * 2 / Ra
    xc = x_center * 2 - Ra/2 + (Ra/2+L0) * cos(theta)
    yc = - (Ra/2+L0) * sin(theta)
    # 绘制输出波导
    v1 = [x_center * 2 - Ra/2 + output_width/2 * sin(theta),
          output_width/2 * cos(theta)]
    v2 = [x_center * 2 - Ra/2 - output_width/2 * sin(theta),
          - output_width/2 * cos(theta)]
    v3 = [xc - output_width/2 * sin(theta),
          yc - output_width/2 * cos(theta)]
    v4 = [xc + output_width/2 * sin(theta),
          yc + output_width/2 * cos(theta)]
    vtx = [v1,
           v2,
           v3,
           v4]
    AWG.add_polygon(vtx, layer=(1, 0))

AWG.show()
# c = gf.boolean(A=AWG, B=AWG, operation="or", layer=(1, 0))
# c.show()