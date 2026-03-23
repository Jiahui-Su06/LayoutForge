import gdsfactory as gf
import mydraw as md  # import自定义库mydraw

# 纵向直波导长度
w1 = 20
w2 = 20
w3 = 20
w4 = 20
w5 = 20
w6 = 20
w7 = 20
w8 = 20
w9 = 20

w = 1.1  # 单模波导宽度
R = 60   # 单模弯曲波导半径
packaging = 127  # 封装光纤阵列中心间隔

# MMI参数
w_taper = 2.7
l_taper_i = 50
l_taper_o = 50
l_mmi = 55.5
w_mmi = 7
length_mmi = l_taper_i + l_taper_o + l_mmi  # MMI总长度
separation = 3.63  # MMI的输出taper中心偏移距离
gap_mmi = separation - w_taper
x_start = 0 # 第一个MMI的起始坐标(x, y)
y_start = 0
# S bend参数
w_sbend = 110  # S bend的横向距离（宽度）
bend = True  # 是否使用普通弯曲拼接成的Bend：若为True，为普通弯曲拼接成的S bend；若为False，为Bezier-S Bend
# h是计算值，不能自定义，根据光纤阵列间隔得出
# 这部分是纵向的直波导距离，都是计算参数，不需要修改
h1 = 8*packaging-separation/2-R*2
h2 = 4*packaging-separation/2-R*2
h3 = 2*packaging-separation/2-R*2
h4 = 1*packaging-separation/2-R*2
h5 = packaging/2-separation/2

# 后面都是封装写好的代码，不需要改，只需要修改前面的结构参数即可
c = gf.Component()
mmi_1 = md.my_mmi1x2(width=w, width_taper=w_taper,
                     length_taper_in=l_taper_i, length_taper_out=l_taper_o,
                     length_mmi=l_mmi, width_mmi=w_mmi,
                     gap_mmi=gap_mmi, cross_section='strip',
                     layer=(4, 1)).copy()
mmi_1.move([x_start, y_start])
c.add_ref(mmi_1)
for i in [-1, 1]:
    x1 = x_start + length_mmi
    y1 = y_start + i*separation/2
    x2 = x1 + w1
    y2 = y1
    wg_1 = md.waveguide(start=(x1, y1), end=(x2, y2), width=w, layer=(4, 1))
    c.add_ref(wg_1)
    ring_1 = md.ring_arc(radius=R, width=w, theta_start=-45-i*45, theta_stop=45-i*45,
                        x_center=x2, y_center=y2+i*R,
                        angle_resolution=0.1,
                        layer=(4, 1))
    c.add_ref(ring_1)
    x3 = x2 + R
    y3 = y2 + i*R
    x4 = x3
    y4 = y3 + i*h1
    hg_1 = md.waveguide(start=(x3, y3), end=(x4, y4), width=w, layer=(4, 1))
    c.add_ref(hg_1)
    ring_2 = md.ring_arc(radius=R, width=w, theta_start=135 - i * 45, theta_stop=225 - i * 45,
                         x_center=x4+R, y_center=y4,
                         angle_resolution=0.1,
                         layer=(4, 1))
    c.add_ref(ring_2)
    x5 = x4 + R
    y5 = y4 + i * R
    x6 = x5 + w2
    y6 = y5
    wg_2 = md.waveguide(start=(x5, y5), end=(x6, y6), width=w, layer=(4, 1))
    c.add_ref(wg_2)
    mmi_2 = md.my_mmi1x2(width=w, width_taper=w_taper,
                         length_taper_in=l_taper_i, length_taper_out=l_taper_o,
                         length_mmi=l_mmi, width_mmi=w_mmi,
                         gap_mmi=gap_mmi, cross_section='strip',
                         layer=(4, 1)).copy()
    mmi_2.move([x6, y6])
    c.add_ref(mmi_2)
    for j in [-1, 1]:
        x7 = x6 + length_mmi
        y7 = y6 + j * separation / 2
        x8 = x7 + w3
        y8 = y7
        wg_3 = md.waveguide(start=(x7, y7), end=(x8, y8), width=w, layer=(4, 1))
        c.add_ref(wg_3)
        ring_3 = md.ring_arc(radius=R, width=w, theta_start=-45 - j * 45, theta_stop=45 - j * 45,
                             x_center=x8, y_center=y8 + j * R,
                             angle_resolution=0.1,
                             layer=(4, 1))
        c.add_ref(ring_3)
        x9 = x8 + R
        y9 = y8 + j * R
        x10 = x9
        y10 = y9 + j * h2
        hg_2 = md.waveguide(start=(x9, y9), end=(x10, y10), width=w, layer=(4, 1))
        c.add_ref(hg_2)
        ring_4 = md.ring_arc(radius=R, width=w, theta_start=135 - j * 45, theta_stop=225 - j * 45,
                             x_center=x10 + R, y_center=y10,
                             angle_resolution=0.1,
                             layer=(4, 1))
        c.add_ref(ring_4)
        x11 = x10 + R
        y11 = y10 + j * R
        x12 = x11 + w4
        y12 = y11
        wg_4 = md.waveguide(start=(x11, y11), end=(x12, y12), width=w, layer=(4, 1))
        c.add_ref(wg_4)
        mmi_3 = md.my_mmi1x2(width=w, width_taper=w_taper,
                             length_taper_in=l_taper_i, length_taper_out=l_taper_o,
                             length_mmi=l_mmi, width_mmi=w_mmi,
                             gap_mmi=gap_mmi, cross_section='strip',
                             layer=(4, 1)).copy()
        mmi_3.move([x12, y12])
        c.add_ref(mmi_3)
        for k in [-1, 1]:
            x13 = x12 + length_mmi
            y13 = y12 + k * separation / 2
            x14 = x13 + w5
            y14 = y13
            wg_5 = md.waveguide(start=(x13, y13), end=(x14, y14), width=w, layer=(4, 1))
            c.add_ref(wg_5)
            ring_5 = md.ring_arc(radius=R, width=w, theta_start=-45 - k * 45, theta_stop=45 - k * 45,
                                 x_center=x14, y_center=y14 + k * R,
                                 angle_resolution=0.1,
                                 layer=(4, 1))
            c.add_ref(ring_5)
            x15 = x14 + R
            y15 = y14 + k * R
            x16 = x15
            y16 = y15 + k * h3
            hg_3 = md.waveguide(start=(x15, y15), end=(x16, y16), width=w, layer=(4, 1))
            c.add_ref(hg_3)
            ring_6 = md.ring_arc(radius=R, width=w, theta_start=135 - k * 45, theta_stop=225 - k * 45,
                                 x_center=x16 + R, y_center=y16,
                                 angle_resolution=0.1,
                                 layer=(4, 1))
            c.add_ref(ring_6)
            x17 = x16 + R
            y17 = y16 + k * R
            x18 = x17 + w6
            y18 = y17
            wg_6 = md.waveguide(start=(x17, y17), end=(x18, y18), width=w, layer=(4, 1))
            c.add_ref(wg_6)
            mmi_4 = md.my_mmi1x2(width=w, width_taper=w_taper,
                                 length_taper_in=l_taper_i, length_taper_out=l_taper_o,
                                 length_mmi=l_mmi, width_mmi=w_mmi,
                                 gap_mmi=gap_mmi, cross_section='strip',
                                 layer=(4, 1)).copy()
            mmi_4.move([x18, y18])
            c.add_ref(mmi_4)
            for m in [-1, 1]:
                x19 = x18 + length_mmi
                y19 = y18 + m * separation / 2
                x20 = x19 + w7
                y20 = y19
                wg_7 = md.waveguide(start=(x19, y19), end=(x20, y20), width=w, layer=(4, 1))
                c.add_ref(wg_7)
                ring_7 = md.ring_arc(radius=R, width=w, theta_start=-45 - m * 45, theta_stop=45 - m * 45,
                                     x_center=x20, y_center=y20 + m * R,
                                     angle_resolution=0.1,
                                     layer=(4, 1))
                c.add_ref(ring_7)
                x21 = x20 + R
                y21 = y20 + m * R
                x22 = x21
                y22 = y21 + m * h4
                hg_4 = md.waveguide(start=(x21, y21), end=(x22, y22), width=w, layer=(4, 1))
                c.add_ref(hg_4)
                ring_8 = md.ring_arc(radius=R, width=w, theta_start=135 - m * 45, theta_stop=225 - m * 45,
                                     x_center=x22 + R, y_center=y22,
                                     angle_resolution=0.1,
                                     layer=(4, 1))
                c.add_ref(ring_8)
                x23 = x22 + R
                y23 = y22 + m * R
                x24 = x23 + w8
                y24 = y23
                wg_8 = md.waveguide(start=(x23, y23), end=(x24, y24), width=w, layer=(4, 1))
                c.add_ref(wg_8)
                mmi_5 = md.my_mmi1x2(width=w, width_taper=w_taper,
                                     length_taper_in=l_taper_i, length_taper_out=l_taper_o,
                                     length_mmi=l_mmi, width_mmi=w_mmi,
                                     gap_mmi=gap_mmi, cross_section='strip',
                                     layer=(4, 1)).copy()
                mmi_5.move([x24, y24])
                c.add_ref(mmi_5)
                for n in [-1, 1]:
                    x25 = x24 + length_mmi
                    y25 = y24 + n * separation / 2
                    x26 = x25 + w9
                    y26 = y25
                    wg_9 = md.waveguide(start=(x25, y25), end=(x26, y26), width=w, layer=(4, 1))
                    c.add_ref(wg_9)
                    if bend == True:
                        sbend = md.bend_s_ring(w=w, height=n*h5, width=w_sbend,
                                               x_center=x26, y_center=y26,
                                               angle_resolution=0.1, radius_min=60, layer=(4,1))
                        c.add_ref(sbend)
                    else:
                        bend_bezier = gf.components.bend_s(size=(w_sbend, n*h5), npoints=200,
                                                           cross_section=gf.cross_section.strip(width=w, layer=(4, 1)),
                                                           allow_min_radius_violation=False).copy()
                        bend_bezier.move([x26, y26])
                        c.add_ref(bend_bezier)

c.show()
