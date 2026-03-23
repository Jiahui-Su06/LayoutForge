import gdsfactory as gf
# import numpy as np
from numpy import cos, sin, pi, rad2deg
import mydraw


# 【声明】 i->input o->output c->circle/center a->array t-transition
# ================================
# AWG参数
# ================================
m = 60  # 衍射级
lambda_c = 1.55012  # 工作中心波长，单位um
ng = 1.6648  # 阵列（多模）波导有效折射率
N = 60  # 阵列波导数
Ra = 640.36  # 罗兰圆半径，FPR长度，单位um
da = 6  # 阵列波导输入端口间隔
gap = 0.1  # 阵列波导孔径处中心间隔
w = 4  # 阵列波导宽度，多模波导
w0 = 1.2  # 单模波导宽度
Ni = 1  # 输入波导数
No = 16  # 输出波导数
wi = 2.8  # 输入波导开口宽度
wo = 2.8  # 输出波导开口宽度
di = 3  # 输入波导中心间距
do = 3  # 输出波导中心间距
# ================================
# 阵列波导布线参数
# ================================
# 锥形波导参数
L0 = 5  # 单模过渡波导长度
Lm = 10  # 多模波导长度
Li = 20  # 输入端口锥形波导长度
Lo = 20  # 输出端口锥形波导长度
Li_2 = 30
Lo_2 = 30
La = 30  # 阵列波导端口锥形波导长度
Lt = 20  # 单模过渡多模锥形波导长度
# 弯曲波导参数
alpha = 2  # 外扩角度倍数
R1 = 100  # 阵列波导孔径处矫正弯曲半径，普通多模弯曲
R2 = 60  # 90度直角欧拉弯曲
Ri = 100  # 输入端弯曲波导
Ro = 100  # 输出端弯曲波导
# 多模阵列波导参数
L1_0 = 0  # 第一段初始长度
L2_0 = 0  # 第二段初始长度
# 单模波导参数
Li0 = 20  # 输入直波导长度
Lo0 = 10  # 输出直波导长度
# 套刻版图
overlay = True  # 是否增加套

# ================================
# 计算参数
# ================================
dL = m * lambda_c / ng  # 阵列波导长度差
print(dL)

AWG = gf.Component("AWG")  # 创建AWG容器
theta_sign = [1, -1]  # 指示AWG区域
x_offset_sign = [1, -1]
offset = 0.002  # 长度偏移量
correct1 = []
correct2 = []
correct3 = []
correct4 = []
for i in range(0, 2):  # 分别绘制AWG左右部分
    for j in range(1, N+3):  # 绘制阵列波导，N+2多出的两个是为了绘制套
        # ==============================================================================================================
        # 阵列孔径处弯曲锥形波导、单模过渡波导、单模->多模锥形波导
        # ==============================================================================================================
        theta = - da * (j - (N + 3) / 2) / Ra * theta_sign[i]  # 锥形波导倾斜角度
        if i == 1:
            x1 = Ra * sin(theta) + x_center * 2  # 阵列波导端口坐标(x1, y1)
            x2 = (Ra + La) * sin(theta) + x_center * 2  # 阵列波导第一段锥形波导端口坐标
            x3 = (Ra + La + L0) * sin(theta) + x_center * 2
            x3_offset = (Ra + La + L0 + offset) * sin(theta) + x_center * 2
            x4 = (Ra + La + L0 + Lt) * sin(theta) + x_center * 2
        else:
            x1 = Ra * sin(theta)  # 阵列波导端口坐标(x1, y1)
            x2 = (Ra + La) * sin(theta)
            x3 = (Ra + La + L0) * sin(theta)
            x3_offset = (Ra + La + L0 + offset) * sin(theta)
            x4 = (Ra + La + L0 + Lt) * sin(theta)
        y1 = Ra * cos(theta)
        y2 = (Ra + La) * cos(theta)
        y3 = (Ra + La + L0) * cos(theta)
        y3_offset = (Ra + La + L0 + offset) * cos(theta)
        y4 = (Ra + La + L0 + Lt) * cos(theta)
        if j != 1 and j != N+2:
            if i == 0:
                x_r = x1 + (da - gap) / 2 * cos(theta)
                y_r = y1 - (da - gap) / 2 * sin(theta)
                x_l = x1 - (da - gap) / 2 * cos(theta)
                y_l = y1 + (da - gap) / 2 * sin(theta)
                correct1.append((x_r, y_r))
                correct1.append((x_l, y_l))  # 逆时针方向记录
            else:
                x_l = x1 - (da - gap) / 2 * cos(theta)
                y_l = y1 + (da - gap) / 2 * sin(theta)
                x_r = x1 + (da - gap) / 2 * cos(theta)
                y_r = y1 - (da - gap) / 2 * sin(theta)
                correct2.append((x_l, y_l))
                correct2.append((x_r, y_r))  # 顺时针方向记录
            taper1 = mydraw.curved_taper(w1=w0, w2=da-gap,
                                         length=La + offset,
                                         rotate_angle=rad2deg(pi / 2 - theta),
                                         center=(x1, y1),
                                         layer=(4, 1))
            wg1 = mydraw.waveguide(start=(x2, y2), end=(x3_offset, y3_offset),  # 单模过渡波导
                                   width=w0, layer=(4, 1))
            taper2 = mydraw.taper(w1=w0, w2=w,
                                  length=Lt,
                                  rotate_angle=rad2deg(pi / 2 - theta),
                                  center=(x3, y3),
                                  layer=(4, 1))
            AWG.add_ref(taper1)
            AWG.add_ref(wg1)
            AWG.add_ref(taper2)
        else:
            if i == 0 and j == 1:
                x_left_1 = x1
                y_left_1 = y1
            elif i == 0 and j == N+2:
                x_left_2 = x1
                y_left_2 = y1
            elif i == 1 and j == 1:
                x_right_1 = x1
                y_right_1 = y1
            elif i == 1 and j == N+2:
                x_right_2 = x1
                y_right_2 = y1
        # ==============================================================================================================
        # 竖直矫正单模弯曲波导
        # ==============================================================================================================
        if theta > 0:
            xc1 = x4 + R1 * cos(theta)  # 第一段弯曲波导圆心坐标(xc1,yc1)
            yc1 = y4 - R1 * sin(theta)
            x5 = xc1 - R1 * cos(alpha * theta)
            y5 = yc1 + R1 * sin(alpha * theta)
            x6 = x5 + Lm * sin(alpha * theta)
            y6 = y5 + Lm * cos(alpha * theta)
            xc2 = x6 - R1 * cos(alpha * theta)
            yc2 = y6 + R1 * sin(alpha * theta)
            x7 = xc2 + R1
            y7 = yc2
            L_offset = (2 * alpha - 1) * (-da*(1-(N+3)/2)/Ra - theta) * R1
            x8 = x7
            y8 = y7 + L_offset
            if j != 1 and j != N + 2:
                ring1 = mydraw.ring_arc(radius=R1, width=w,
                                        theta_start=rad2deg(pi-alpha*theta), theta_stop=rad2deg(pi-theta),
                                        x_center=xc1, y_center=yc1,
                                        angle_resolution=0.1,
                                        layer=(4, 1))
                wg2 = mydraw.waveguide(start=(x5, y5), end=(x6, y6),
                                       width=w, layer=(4, 1))
                ring2 = mydraw.ring_arc(radius=R1, width=w,
                                        theta_start=rad2deg(-alpha*theta), theta_stop=rad2deg(0),
                                        x_center=xc2, y_center=yc2,
                                        angle_resolution=0.1,
                                        layer=(4, 1))
                wg_offset = mydraw.waveguide(start=(x7, y7), end=(x8, y8+offset), width=w, layer=(4, 1))
                AWG.add_ref(ring1)
                AWG.add_ref(wg2)
                AWG.add_ref(ring2)
                AWG.add_ref(wg_offset)
        else:
            xc1 = x4 - R1 * cos(-theta)  # 第一段弯曲波导圆心坐标(xc1,yc1)
            yc1 = y4 - R1 * sin(-theta)
            x5 = xc1 + R1 * cos(-alpha * theta)
            y5 = yc1 + R1 * sin(-alpha * theta)
            x6 = x5 - Lm * sin(-alpha * theta)
            y6 = y5 + Lm * cos(-alpha * theta)
            xc2 = x6 + R1 * cos(-alpha * theta)
            yc2 = y6 + R1 * sin(-alpha * theta)
            x7 = xc2 - R1
            y7 = yc2
            L_offset = (2 * alpha - 1) * (-da * (1 - (N + 3) / 2) / Ra + theta) * R1
            x8 = x7
            y8 = y7 + L_offset
            if j != 1 and j != N + 2:
                ring1 = mydraw.ring_arc(radius=R1, width=w,
                                        theta_start=rad2deg(-theta), theta_stop=rad2deg(-alpha * theta),
                                        x_center=xc1, y_center=yc1,
                                        angle_resolution=0.1,
                                        layer=(4, 1))
                wg2 = mydraw.waveguide(start=(x5, y5), end=(x6, y6),
                                       width=w, layer=(4, 1))
                ring2 = mydraw.ring_arc(radius=R1, width=w,
                                        theta_start=rad2deg(pi), theta_stop=rad2deg(pi-alpha*theta),
                                        x_center=xc2, y_center=yc2,
                                        angle_resolution=0.1,
                                        layer=(4, 1))
                wg_offset = mydraw.waveguide(start=(x7, y7), end=(x8, y8 + offset), width=w, layer=(4, 1))
                AWG.add_ref(ring1)
                AWG.add_ref(wg2)
                AWG.add_ref(ring2)
                AWG.add_ref(wg_offset)
        # ================================
        # 多模波导，其长度是计算值
        # ================================
        if j == 1:  # 第一根阵列波导
            x9 = x8
            y9 = y8 + L1_0
            xc3 = x9 + R2 * x_offset_sign[i]
            yc3 = y9
            x10 = xc3
            y10 = yc3 + R2
            x11 = x10 + L2_0 * x_offset_sign[i]
            y11 = y10
            x_center = x11
        else:
            if i == 1:
                L2 = x5 - x_center - R2
            else:
                L2 = x_center - x5 - R2
            # L1 = (L1_0 + L2_0) + dL * (j-1) / 2 - L2  # 每个部分的L1只增长dL/2，要检查好！！！
            L1 = (L1_0 + L2_0) + dL * (j-1) / 2 - L2
            x7 = x6
            y7 = y6 + L1
            xc2 = x7 + R2 * x_offset_sign[i]
            yc2 = y7
            x8 = xc2
            y8 = yc2 + R2
            x9 = x8 + L2 * x_offset_sign[i]
            y9 = y8
        if j != 1 and j != N + 2:
            wg2 = mydraw.waveguide(start=(x6, y6), end=(x7, y7+offset),
                                   width=w,
                                   layer=(4, 1))
            ring2 = gf.components.bend_euler(radius=R2,
                                             angle=90,
                                             p=1,
                                             with_arc_floorplan=True,
                                             # width=w,
                                             cross_section=gf.cross_section.strip(width=w, layer=(4, 1)),
                                             allow_min_radius_violation=False).copy()
            if i == 0:
                ring2.rotate(180)
                ring2.move([x8, y8])
                wg3 = mydraw.waveguide(start=(x8, y8), end=(x9 + offset, y9),  # 增加补偿长度，填缝隙
                                       width=w, layer=(4, 1))
            else:
                ring2.rotate(90)
                ring2.move([x7, y7])
                wg3 = mydraw.waveguide(start=(x8, y8), end=(x9, y9),
                                       width=w, layer=(4, 1))
            AWG.add_ref(wg2)
            AWG.add_ref(ring2)
            AWG.add_ref(wg3)
        if i == 0 and j == 1:
            vtx1 = [[x1, y1],
                    [x2, y2],
                    [x3, y3],
                    [x4, y4],
                    [x5, y5],
                    [x6, y6],
                    [x7, y7],
                    [x8, y8],
                    [x9, y9],
                    [xc1, yc1],
                    [xc2, yc2],
                    [-theta, 0],
                    [45+theta_sign[i]*45, 135+theta_sign[i]*45]]
        elif i == 0 and j == N+2:
            vtx2 = [[x1, y1],
                    [x2, y2],
                    [x3, y3],
                    [x4, y4],
                    [x5, y5],
                    [x6, y6],
                    [x7, y7],
                    [x8, y8],
                    [x9, y9],
                    [xc1, yc1],
                    [xc2, yc2],
                    [pi, pi - theta],
                    [45+theta_sign[i]*45, 135+theta_sign[i]*45]]
        elif i == 1 and j == 1:
            vtx3 = [[x1, y1],
                    [x2, y2],
                    [x3, y3],
                    [x4, y4],
                    [x5, y5],
                    [x6, y6],
                    [x7, y7],
                    [x8, y8],
                    [x9, y9],
                    [xc1, yc1],
                    [xc2, yc2],
                    [pi, pi - theta],
                    [45+theta_sign[i]*45, 135+theta_sign[i]*45]]
        elif i == 1 and j == N+2:
            vtx4 = [[x1, y1],
                    [x2, y2],
                    [x3, y3],
                    [x4, y4],
                    [x5, y5],
                    [x6, y6],
                    [x7, y7],
                    [x8, y8],
                    [x9, y9],
                    [xc1, yc1],
                    [xc2, yc2],
                    [-theta, 0],
                    [45+theta_sign[i]*45, 135+theta_sign[i]*45]]

    # ================================
    # 输入输出波导
    # ================================
    if i == 1:
        for k in range(1, Ni+3):
            theta_i = - di * (k - (Ni + 3) / 2) * 2 / Ra
            xi1 = 2 * x_center + (Ra/2) * sin(theta_i)
            yi1 = Ra/2 - (Ra/2) * cos(theta_i)
            if k != 1 and k != Ni+2:
                taper_i = mydraw.curved_taper(w1=w0, w2=wi,
                                              length=Li,
                                              rotate_angle=rad2deg(theta_i-pi/2),
                                              center=(xi1, yi1),
                                              layer=(4, 1))
                AWG.add_ref(taper_i)
                x_r = xi1 + wi / 2 * cos(theta_i)
                y_r = yi1 + wi / 2 * sin(theta_i)
                x_l = xi1 - wi / 2 * cos(theta_i)
                y_l = yi1 - wi / 2 * sin(theta_i)
                correct3.append((x_r, y_r))
                correct3.append((x_l, y_l))  # 顺时针方向记录
            else:
                if k == 1:
                    x_i_r = xi1
                    y_i_r = yi1
                elif k == Ni+2:
                    x_i_l = xi1
                    y_i_l = yi1
            # ================================
            # 竖直输入波导矫正单模弯曲波导
            # ================================
            xi1_ = x_center*2 + (Ra / 2 + Li) * sin(-theta_i)
            yi1_ = Ra / 2 - (Ra / 2 + Li) * cos(theta_i)
            xi2 = x_center*2 + (Ra / 2 + Li + Li_2) * sin(-theta_i)
            yi2 = Ra / 2 - (Ra / 2 + Li + Li_2) * cos(theta_i)
            if theta_i > 0:
                xic1 = xi2 + Ri * cos(theta_i)  # 第一段弯曲波导圆心坐标(xic1,yic1)
                yic1 = yi2 - Ri * sin(theta_i)
                # ================================
                # 补偿单模竖直波导
                # ================================
                L_offset = (-di * (1 - (Ni + 3) / 2) * 2 / Ra - theta_i) * Ri
                xi3 = xic1 - Ri
                yi3 = yic1
                xi4 = xi3
                yi4 = yi3 - L_offset
                if k != 1 and k != Ni + 2:
                    wg_i = mydraw.waveguide(start=(xi1_, yi1_), end=(xi2, yi2),
                                            width=w0, layer=(4, 1))
                    ring_i = mydraw.ring_arc(radius=Ri, width=w0,
                                             theta_start=rad2deg(pi - theta_i), theta_stop=rad2deg(pi),
                                             x_center=xic1, y_center=yic1,
                                             angle_resolution=0.1,
                                             layer=(4, 1))
                    wg_i_offset = mydraw.waveguide(start=(xi3, yi3), end=(xi4, yi4), width=w0, layer=(4, 1))
                    AWG.add_ref(wg_i)
                    AWG.add_ref(ring_i)
                    AWG.add_ref(wg_i_offset)
            else:
                xic1 = xi2 - Ri * cos(-theta_i)  # 第一段弯曲波导圆心坐标(xic1,yic1)
                yic1 = yi2 - Ri * sin(-theta_i)
                L_offset = (-di * (1 - (Ni + 3) / 2) * 2 / Ra + theta_i) * Ri
                xi3 = xic1 + Ri
                yi3 = yic1
                xi4 = xi3
                yi4 = yi3 - L_offset
                if k != 1 and k != Ni + 2:
                    wg_i = mydraw.waveguide(start=(xi1_, yi1_), end=(xi2, yi2),
                                            width=w0, layer=(4, 1))
                    ring_i = mydraw.ring_arc(radius=Ri, width=w0,
                                             theta_start=rad2deg(0), theta_stop=rad2deg(-theta_i),
                                             x_center=xic1, y_center=yic1,
                                             angle_resolution=0.1,
                                             layer=(4, 1))
                    wg_i_offset = mydraw.waveguide(start=(xi3, yi3), end=(xi4, yi4), width=w0, layer=(4, 1))
                    AWG.add_ref(wg_i)
                    AWG.add_ref(ring_i)
                    AWG.add_ref(wg_i_offset)
            if Ni % 2 == 0 and k == (Ni + 2) / 2:  # k为偶数
                yi_port = yi4
            elif Ni % 2 == 1 and k == (Ni + 3) / 2:
                yi_port = yi4
        wg_i_port = [None] * Ni
        for k in range(1, Ni + 3):
            theta_i = - di * (k - (Ni + 3) / 2) * 2 / Ra
            xi1 = 2 * x_center + (Ra / 2) * sin(theta_i)
            yi1 = Ra / 2 - (Ra / 2) * cos(theta_i)
            xi2 = x_center * 2 + (Ra / 2 + Li) * sin(-theta_i)
            yi2 = Ra / 2 - (Ra / 2 + Li) * cos(theta_i)
            if theta_i > 0:
                xic1 = xi2 + Ri * cos(theta_i)  # 第一段弯曲波导圆心坐标(xic1,yic1)
                yic1 = yi2 - Ri * sin(theta_i)
                L_offset = (-di * (1 - (Ni + 3) / 2) * 2 / Ra - theta_i) * Ri
                xi3 = xic1 - Ri
                yi3 = yic1
            else:
                xic1 = xi2 - Ri * cos(-theta_i)  # 第一段弯曲波导圆心坐标(xic1,yic1)
                yic1 = yi2 - Ri * sin(-theta_i)
                L_offset = (-di * (1 - (Ni + 3) / 2) * 2 / Ra + theta_i) * Ri
                xi3 = xic1 + Ri
                yi3 = yic1
            xi4 = xi3
            yi4 = yi3 - L_offset
            xi5 = xi4
            yi5 = yi_port
            if k != 1 and k != Ni + 2:  # 绘制输出端口Port波导
                wg_i_port[k-2] = mydraw.waveguide(start=(xi4, yi4), end=(xi5, yi5-offset), width=w0, layer=(4, 1))
                wg_i_port[k-2].add_port(name="i1", center=(xi5, yi5), width=w0, orientation=-90, layer=(4, 1))
                wg_i_port[k-2].add_port(name="i2", center=(xi5, yi5), width=w0, orientation=-90, layer=(4, 1))
                AWG.add_ref(wg_i_port[k-2])
            if k == 1:
                vtx_i_1 = [[xi1, yi1],
                           [xi2, yi2],
                           [xi3, yi3],
                           [xi4, yi4],
                           [xi5, yi5],
                           [xic1, yic1],
                           [pi - theta_i, pi]]
            elif k == Ni + 2:
                vtx_i_2 = [[xi1, yi1],
                           [xi2, yi2],
                           [xi3, yi3],
                           [xi4, yi4],
                           [xi5, yi5],
                           [xic1, yic1],
                           [0, -theta_i]]
    else:
        for k in range(1, No+3):
            theta_o = - do * (k - (No + 3) / 2) * 2 / Ra
            xo1 = 0 + (Ra/2) * sin(theta_o)
            yo1 = Ra/2 - (Ra/2) * cos(theta_o)
            if k != 1 and k != No+2:
                taper_o = mydraw.curved_taper(w1=w0, w2=wo,
                                              length=Lo,
                                              rotate_angle=rad2deg(theta_o-pi/2),
                                              center=(xo1, yo1),
                                              layer=(4, 1))

                AWG.add_ref(taper_o)
                x_r = xo1 + wo / 2 * cos(theta_o)
                y_r = yo1 + wo / 2 * sin(theta_o)
                x_l = xo1 - wo / 2 * cos(theta_o)
                y_l = yo1 - wo / 2 * sin(theta_o)
                correct4.append((x_r, y_r))
                correct4.append((x_l, y_l))  # 顺时针方向记录
            else:
                if k == 1:
                    x_o_r = xo1
                    y_o_r = yo1
                elif k == No + 2:
                    x_o_l = xo1
                    y_o_l = yo1
            # ================================
            # 竖直输出波导矫正单模弯曲波导
            # ================================
            xo1_ = 0 + (Ra / 2 + Lo) * sin(theta_o)
            yo1_ = Ra / 2 - (Ra / 2 + Lo) * cos(theta_o)
            xo2 = (Ra/2 + Lo + Lo_2) * sin(-theta_o)
            yo2 = Ra/2 - (Ra/2 + Lo + Lo_2) * cos(theta_o)
            if theta_o > 0:
                xoc1 = xo2 + Ro * cos(theta_o)  # 第一段弯曲波导圆心坐标(xoc1,yoc1)
                yoc1 = yo2 - Ro * sin(theta_o)
                # ================================
                # 补偿单模竖直波导
                # ================================
                L_offset = (-do*(1-(No+3)/2)*2/Ra - theta_o) * Ro
                xo3 = xoc1 - Ro
                yo3 = yoc1
                xo4 = xo3
                yo4 = yo3 - L_offset
                if k != 1 and k != No+2:
                    wg_o = mydraw.waveguide(start=(xo1_, yo1_), end=(xo2, yo2),
                                            width=w0, layer=(4, 1))
                    ring_o = mydraw.ring_arc(radius=Ro, width=w0,
                                             theta_start=rad2deg(pi-theta_o), theta_stop=rad2deg(pi),
                                             x_center=xoc1, y_center=yoc1,
                                             angle_resolution=0.1,
                                             layer=(4, 1))
                    wg_o_offset = mydraw.waveguide(start=(xo3, yo3), end=(xo4, yo4), width=w0, layer=(4, 1))
                    AWG.add_ref(wg_o)
                    AWG.add_ref(ring_o)
                    AWG.add_ref(wg_o_offset)
            else:
                xoc1 = xo2 - Ro * cos(-theta_o)  # 第一段弯曲波导圆心坐标(xoc1,yoc1)
                yoc1 = yo2 - Ro * sin(-theta_o)
                L_offset = (-do*(1-(No+3)/2)*2/Ra + theta_o) * Ro
                xo3 = xoc1 + Ro
                yo3 = yoc1
                xo4 = xo3
                yo4 = yo3 - L_offset
                if k != 1 and k != No + 2:
                    wg_o = mydraw.waveguide(start=(xo1_, yo1_), end=(xo2, yo2),
                                            width=w0, layer=(4, 1))
                    ring_o = mydraw.ring_arc(radius=Ro, width=w0,
                                             theta_start=rad2deg(0), theta_stop=rad2deg(-theta_o),
                                             x_center=xoc1, y_center=yoc1,
                                             angle_resolution=0.1, layer=(4, 1))
                    wg_o_offset = mydraw.waveguide(start=(xo3, yo3), end=(xo4, yo4), width=w0, layer=(4, 1))
                    AWG.add_ref(wg_o)
                    AWG.add_ref(ring_o)
                    AWG.add_ref(wg_o_offset)
            if No % 2 == 0 and k == (No+2)/2:  # k为偶数
                yo_port = yo4
            elif No % 2 == 1 and k == (No+3)/2:
                yo_port = yo4
        wg_o_port = [None] * No
        for k in range(1, No+3):  # 为输出波导添加输出端口Ports
            theta_o = - do * (k - (No + 3) / 2) * 2 / Ra
            xo1 = 0 + (Ra/2) * sin(theta_o)
            yo1 = Ra/2 - (Ra/2) * cos(theta_o)
            xo2 = (Ra/2 + Lo) * sin(-theta_o)
            yo2 = Ra/2 - (Ra/2 + Lo) * cos(theta_o)
            if theta_o > 0:
                xoc1 = xo2 + Ro * cos(theta_o)  # 第一段弯曲波导圆心坐标(xoc1,yoc1)
                yoc1 = yo2 - Ro * sin(theta_o)
                L_offset = (-do*(1-(No+3)/2)*2/Ra - theta_o) * Ro
                xo3 = xoc1 - Ro
                yo3 = yoc1
            else:
                xoc1 = xo2 - Ro * cos(-theta_o)  # 第一段弯曲波导圆心坐标(xoc1,yoc1)
                yoc1 = yo2 - Ro * sin(-theta_o)
                L_offset = (-do*(1-(No+3)/2)*2/Ra + theta_o) * Ro
                xo3 = xoc1 + Ro
                yo3 = yoc1
            xo4 = xo3
            yo4 = yo3 - L_offset
            xo5 = xo4
            yo5 = yo_port
            if k != 1 and k != No + 2:  # 做补偿长度，填缝隙
                wg_o_port[k-2] = mydraw.waveguide(start=(xo4, yo4), end=(xo5, yo5-offset), width=w0, layer=(4, 1))
                wg_o_port[k-2].add_port(name="o1", center=(xo5, yo5), width=w0, orientation=-90,
                                        layer=(4, 1))
                wg_o_port[k-2].add_port(name="o2", center=(xo5, yo5), width=w0, orientation=-90,
                                        layer=(4, 1))
                AWG.add_ref(wg_o_port[k-2])
            if k == 1:
                vtx_o_1 = [[xo1, yo1],
                           [xo2, yo2],
                           [xo3, yo3],
                           [xo4, yo4],
                           [xo5, yo5],
                           [xoc1, yoc1],
                           [pi-theta_o, pi]]
            elif k == No+2:
                vtx_o_2 = [[xo1, yo1],
                           [xo2, yo2],
                           [xo3, yo3],
                           [xo4, yo4],
                           [xo5, yo5],
                           [xoc1, yoc1],
                           [0, -theta_o]]
# ================================
# 绘制AWG外面的套
# ================================
radius_offset = 15  # 套的外圈半径偏移量
if overlay:
    c1_1 = mydraw.circle(R1,
                         theta_start=rad2deg(vtx1[11][0]),
                         theta_stop=rad2deg(vtx1[11][1]),
                         x_center=vtx1[9][0],
                         y_center=vtx1[9][1],
                         angle_resolution=0.1)
    c1_2 = mydraw.circle(R2-radius_offset,
                         theta_start=vtx1[12][0],
                         theta_stop=vtx1[12][1],
                         x_center=vtx1[10][0]-radius_offset,
                         y_center=vtx1[10][1]+radius_offset,
                         angle_resolution=0.1)
    c2_1 = mydraw.circle(R1,
                         theta_start=rad2deg(vtx2[11][0]),
                         theta_stop=rad2deg(vtx2[11][1]),
                         x_center=vtx2[9][0],
                         y_center=vtx2[9][1],
                         angle_resolution=0.1)
    c2_2 = mydraw.circle(R2-radius_offset,
                         theta_start=vtx2[12][0],
                         theta_stop=vtx2[12][1],
                         x_center=vtx2[10][0]-radius_offset,
                         y_center=vtx2[10][1]+radius_offset,
                         angle_resolution=0.1)
    c3_1 = mydraw.circle(R1,
                         theta_start=rad2deg(vtx3[11][0]),
                         theta_stop=rad2deg(vtx3[11][1]),
                         x_center=vtx3[9][0],
                         y_center=vtx3[9][1],
                         angle_resolution=0.1)
    c3_2 = mydraw.circle(R2-radius_offset,
                         theta_start=vtx3[12][0],
                         theta_stop=vtx3[12][1],
                         x_center=vtx3[10][0]+radius_offset,
                         y_center=vtx3[10][1]+radius_offset,
                         angle_resolution=0.1)
    c4_1 = mydraw.circle(R1,
                         theta_start=rad2deg(vtx4[11][0]),
                         theta_stop=rad2deg(vtx4[11][1]),
                         x_center=vtx4[9][0],
                         y_center=vtx4[9][1],
                         angle_resolution=0.1)
    c4_2 = mydraw.circle(R2-radius_offset,
                         theta_start=vtx4[12][0],
                         theta_stop=vtx4[12][1],
                         x_center=vtx4[10][0]+radius_offset,
                         y_center=vtx4[10][1]+radius_offset,
                         angle_resolution=0.1)
    c_left = mydraw.circle(Ra,
                           theta_start=rad2deg(pi/2 + da * (1 - (N + 3) / 2) / Ra),
                           theta_stop=rad2deg(pi/2 + da * (N+2 - (N + 3) / 2) / Ra),
                           x_center=0,
                           y_center=0,
                           angle_resolution=0.1)
    c_right = mydraw.circle(Ra,
                            theta_start=rad2deg(pi/2 - da * (N+2 - (N + 3) / 2) / Ra),
                            theta_stop=rad2deg(pi/2 - da * (1 - (N + 3) / 2) / Ra),
                            x_center=2*x_center,
                            y_center=0,
                            angle_resolution=0.1)
    vtx = []
    vtx.extend(c1_1)
    vtx.extend(c1_2[::-1])
    vtx.extend(c3_2[::-1])
    vtx.extend(c3_1)
    vtx.append((x_right_1, y_right_1))
    vtx.extend(correct2)
    vtx.append((x_right_2, y_right_2))
    vtx.extend(c4_1)
    vtx.extend(c4_2)
    vtx.extend(c2_2)
    vtx.extend(c2_1)
    vtx.append((x_left_2, y_left_2))
    vtx.extend(correct1[::-1])
    vtx.append((x_left_1, y_left_1))
    AWG.add_polygon(vtx, layer=(4, 2))

    # 绘制输出端的套
    co1 = mydraw.circle(Ro,
                        theta_start=rad2deg(vtx_o_1[6][0]),
                        theta_stop=rad2deg(vtx_o_1[6][1]),
                        x_center=vtx_o_1[5][0],
                        y_center=vtx_o_1[5][1],
                        angle_resolution=0.1)
    co2 = mydraw.circle(Ro,
                        theta_start=rad2deg(vtx_o_2[6][0]),
                        theta_stop=rad2deg(vtx_o_2[6][1]),
                        x_center=vtx_o_2[5][0],
                        y_center=vtx_o_2[5][1],
                        angle_resolution=0.1)
    co = mydraw.circle(Ra/2,
                       theta_start=rad2deg(-pi/2 + do * (1 - (No + 3) / 2) * 2 / Ra),
                       theta_stop=rad2deg(-pi/2 - do * (1 - (No + 3) / 2) * 2 / Ra),
                       x_center=0,
                       y_center=Ra/2,
                       angle_resolution=0.1)
    vtx_o = []
    vtx_o.extend(co1)
    vtx_o.extend([[vtx_o_1[4][0], vtx_o_1[4][1]]])
    vtx_o.extend([[vtx_o_2[4][0], vtx_o_2[4][1]]])
    vtx_o.extend(co2)
    vtx_o.append((x_o_r, y_o_r))
    vtx_o.extend(correct4)
    vtx_o.append((x_o_l, y_o_l))
    AWG.add_polygon(vtx_o, layer=(4, 2))

    # 绘制输入端的套
    ci1 = mydraw.circle(Ri,
                        theta_start=rad2deg(vtx_i_1[6][0]),
                        theta_stop=rad2deg(vtx_i_1[6][1]),
                        x_center=vtx_i_1[5][0],
                        y_center=vtx_i_1[5][1],
                        angle_resolution=0.1)
    ci2 = mydraw.circle(Ri,
                        theta_start=rad2deg(vtx_i_2[6][0]),
                        theta_stop=rad2deg(vtx_i_2[6][1]),
                        x_center=vtx_i_2[5][0],
                        y_center=vtx_i_2[5][1],
                        angle_resolution=0.1)
    ci = mydraw.circle(Ra / 2,
                       theta_start=rad2deg(-pi / 2 + di * (1 - (Ni + 3) / 2) * 2 / Ra),
                       theta_stop=rad2deg(-pi / 2 - di * (1 - (Ni + 3) / 2) * 2 / Ra),
                       x_center=0+2*x_center,
                       y_center=Ra / 2,
                       angle_resolution=0.1)
    vtx_i = []
    vtx_i.extend(ci1)
    vtx_i.extend([[vtx_i_1[4][0], vtx_i_1[4][1]]])
    vtx_i.extend([[vtx_i_2[4][0], vtx_i_2[4][1]]])
    vtx_i.extend(ci2)
    vtx_i.append((x_i_r, y_i_r))
    vtx_i.extend(correct3)
    vtx_i.append((x_i_l, y_i_l))
    AWG.add_polygon(vtx_i, layer=(4, 2))

# 绘制layer(1, 0)层布线
wg_i = AWG << gf.components.straight(length=10.0, width=1.2,
                                     cross_section=gf.cross_section.strip(width=1.2, layer=(4, 1))).copy()
wg_i.move((400, -120))
route_input = gf.routing.route_single(
    AWG,
    port1=wg_i.ports["o1"],
    port2=wg_i_port[0].ports["i1"],
    cross_section=gf.cross_section.strip(width=1.2, layer=(4, 1)),
    bend=gf.components.bend_circular,
    radius=50,  # 单位 μm
    layer=(4, 1)
)
# 绘制套刻层布线
wg_i_overlay = AWG << gf.components.straight(length=10.0, width=1.2,
                                             cross_section=gf.cross_section.strip(width=1.2, layer=(4, 2))).copy()
wg_i_overlay.move((400, -120))
route_input_overlay = gf.routing.route_single(
    AWG,
    port1=wg_i_overlay.ports["o1"],
    port2=wg_i_port[0].ports["i2"],
    cross_section=gf.cross_section.strip(width=11.2, layer=(4, 2)),
    bend=gf.components.bend_circular,
    radius=50,  # 单位 μm
    auto_taper=False
)

wg_o = [None] * No
wg_o_overlay = [None] * No
for ii in range(1, No+1):
    wg_o[ii-1] = AWG << gf.components.straight(length=10.0, width=1.2,
                                               cross_section=gf.cross_section.strip(width=1.2, layer=(4, 1))).copy()
    wg_o_overlay[ii-1] = AWG << gf.components.straight(length=10.0, width=1.2,
                                                       cross_section=gf.cross_section.strip(width=1.2, layer=(4, 2))).copy()
    wg_o[ii-1].move((-300, -660+ii*33))
    wg_o_overlay[ii-1].move((-300, -660+ii*33))
    # wg_o[ii-1].rotate(90)
    # wg_o_overlay[ii-1].rotate(90)
    route = gf.routing.route_single(
        AWG,
        port1=wg_o[ii-1].ports["o2"],
        port2=wg_o_port[No-ii].ports["o1"],
        cross_section=gf.cross_section.strip(width=1.2, layer=(4, 1)),
        bend=gf.components.bend_circular,

        radius=60,  # 单位 μm
    )
    route_output_overlay = gf.routing.route_single(
        AWG,
        port1=wg_o_overlay[ii-1].ports["o2"],
        port2=wg_o_port[No-ii].ports["o2"],
        cross_section=gf.cross_section.strip(width=11.2, layer=(4, 2)),
        bend=gf.components.bend_circular,
        radius=60,  # 单位 μm
        auto_taper=False
    )

AWG.show()
AWG.write_gds(r"E:\桌面\AWG.gds")
# c = gf.boolean(A=AWG, B=AWG, operation="or", layer=(4, 1))  # 不同层做Merge运算
# c.show()

gf.components.bend_s(size=(11.0, 1.8), npoints=99, cross_section='strip', allow_min_radius_violation=False, width=None)
