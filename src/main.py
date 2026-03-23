import gdsfactory as gf
import numpy as np
import mydraw as md


# 注意，GDSFactory函数的定义以微米为单位
lambda_center = 0.78  # 工作中心波长
# 布拉格反射镜参数
duty_cycle = 0.5      # 布拉格光栅的占空比
period_bragg = 0.236  # 布拉格光栅的周期长度
# 闪耀光栅参数
num_blazed = 200      # 闪耀光栅的周期总数，总数为 2*num_blaze+1
num_bragg = 1         # 每个闪耀光栅周期内所含的布拉格光栅周期数
num_bragg_all = 20    # 布拉格反射镜周期总数
radius_rowland = 100  # 罗兰圆半径
theta_blazed = np.deg2rad(45)  # 光栅闪耀角
phi = np.deg2rad(2)   # 入射角度，相对布拉格光栅法线
period_blazed = period_bragg * num_bragg / np.sin(theta_blazed)  # 闪耀光栅周期长度
thickness_bragg_SiO2 = period_bragg * duty_cycle  # 布拉格光栅中刻蚀层厚度
# 入射、出射波导参数
width_input_wg = 2    # 入射波导宽度
width_single_mode_wg = 0.4  # 单模波导宽度
radius_bend_wg = 150  # 弯曲波导半径
theta_input = theta_blazed+phi   # 入射角，相对闪耀光栅法线
theta_output = theta_blazed-phi  # 出射角，对应中心输出波导
width_bragg = num_bragg_all * period_bragg / np.tan(theta_blazed)  # 布拉格光栅的宽度

# 求入射、出射波导坐标
# 建模以罗兰圆极点为原点
distance_input_to_pole = 2*radius_rowland * np.cos(theta_input)    # 入射波导与光栅极点之间的距离
distance_output_to_pole = 2*radius_rowland * np.cos(theta_output)  # 中心出射波导与光栅极点之间的距离
x_input_wg = distance_input_to_pole * np.sin(theta_input)          # 入射波导入射点坐标
y_input_wg = distance_input_to_pole * np.cos(theta_input)
x_output_wg = distance_output_to_pole * np.sin(theta_output)       # 中心出射波导出射点坐标
y_output_wg = distance_output_to_pole * np.cos(theta_output)

# 中心椭圆（过光栅极点的椭圆）参数计算
# a = (distance_input_to_pole + distance_output_to_pole) / 2  # 椭圆长轴长度 a 
c = np.sqrt((x_input_wg-x_output_wg)**2 + (y_input_wg-y_output_wg)**2) / 2  # 椭圆半焦距长度 c
c_square = ((x_input_wg-x_output_wg)**2 + (y_input_wg-y_output_wg)**2) / 4
# b = math.sqrt(a ** 2 - c ** 2)  # 椭圆短轴长度 b
x_ellipse_center = (x_input_wg + x_output_wg) / 2  # 同心椭圆中心点坐标
y_ellipse_center = (y_input_wg + y_output_wg) / 2
theta_ellipse_rotate = np.atan(-(x_input_wg-x_output_wg) / (y_input_wg-y_output_wg)) - np.pi/2  # 同心椭圆旋转角度

grating = gf.Component("ellipse_grating")  # 光栅器件容器

# # 测试代码
# i = 0
# x_blazed = i * period_blazed  # 光栅刻面中心位置坐标，满足罗兰圆构型
# y_blazed = 2*radius_rowland - np.sqrt((2*radius_rowland)**2 - x_blazed**2)
# distance_input_to_blazed = np.sqrt((x_input_wg-x_blazed)**2 + (y_input_wg-y_blazed)**2)
# distance_output_to_blazed = np.sqrt((x_output_wg-x_blazed)**2 + (y_output_wg-y_blazed)**2)
# a_inner = (distance_input_to_pole + distance_output_to_pole) / 2  # 椭圆环内椭圆 a
# # b_inner = np.sqrt(a_inner**2 - c**2)  # 椭圆环内椭圆 b
# b_inner = np.sqrt(a_inner**2 - c_square)  # 椭圆环内椭圆 b
# a_outer = a_inner + thickness_bragg_SiO2 * a_inner / b_inner  # 椭圆环外椭圆 a
# b_outer = b_inner + thickness_bragg_SiO2  # 椭圆环外椭圆 b
# theta_center_to_blazed = np.atan2(x_ellipse_center-x_blazed, y_ellipse_center-y_blazed)  #
# theta_start = -np.rad2deg(np.pi/2 + theta_ellipse_rotate + theta_center_to_blazed)
# theta_stop = theta_start + 2.0
# # theta_start = 0
# # theta_stop = 360.0
# rotate_angle = np.rad2deg(theta_ellipse_rotate)
# center = (x_ellipse_center, y_ellipse_center)  # 椭圆中心点坐标
# ring = md.elliptical_arc_ring(a_inner, b_inner, a_outer, b_outer, theta_start, theta_stop, rotate_angle,
#                               angle_resolution=0.5, center=center)
# grating.add_ref(ring)

# 绘制椭圆光栅
for i in range(-num_blazed, num_blazed+1):  # 光栅刻面总数为2*num_blazed+1
    x_blazed = i * period_blazed  # 光栅刻面中心位置坐标（满足罗兰圆构型）
    y_blazed = 2*radius_rowland - np.sqrt((2*radius_rowland)**2 - x_blazed**2)
    distance_input_to_blazed = np.sqrt((x_input_wg-x_blazed)**2 + (y_input_wg-y_blazed)**2)
    distance_output_to_blazed = np.sqrt((x_output_wg-x_blazed)**2 + (y_output_wg-y_blazed)**2)
    a_inner = (distance_input_to_blazed + distance_output_to_blazed) / 2  # 椭圆环内椭圆 a
    b_inner = np.sqrt(a_inner**2 - c**2)  # 椭圆环内椭圆 b
    a_outer = a_inner + thickness_bragg_SiO2 * a_inner / b_inner  # 椭圆环外椭圆 a
    b_outer = b_inner + thickness_bragg_SiO2  # 椭圆环外椭圆 b
    theta_center_to_blazed = np.atan2(x_ellipse_center-x_blazed, y_ellipse_center-y_blazed)  #
    theta_start = -np.rad2deg(np.pi/2 + theta_ellipse_rotate + theta_center_to_blazed)
    radius_ellipse = a_inner*b_inner / np.sqrt((b_inner * np.cos(np.deg2rad(theta_start)))**2 +
                                               (a_inner * np.sin(np.deg2rad(theta_start)))**2)
    theta_stop = theta_start + np.rad2deg(width_bragg / radius_ellipse)
    rotate_angle = np.rad2deg(theta_ellipse_rotate)
    center = (x_ellipse_center, y_ellipse_center)  # 椭圆中心点坐标
    ring = md.elliptical_arc_ring(a_inner, b_inner, a_outer, b_outer, theta_start, theta_stop, rotate_angle,
                                  angle_resolution=0.5, center=center, layer=(1, 0))
    grating.add_ref(ring)

helper1 = gf.components.circle(radius=radius_rowland, layer=(2, 0), angle_resolution=1.0)
helper2 = gf.components.circle(radius=2 * radius_rowland, layer=(2, 0), angle_resolution=1.0)
wg1 = md.waveguide(start=(x_input_wg, y_input_wg), end=(0, 0), width=0.1, layer=(2, 0))
wg2 = md.waveguide(start=(x_output_wg, y_output_wg), end=(0, 0), width=0.1, layer=(2, 0))
wg3 = md.waveguide(start=(x_ellipse_center, y_ellipse_center), end=(0, 0), width=0.1, layer=(2, 0))
coupler = gf.components.straight_all_angle
grating.add_ref(wg1)
grating.add_ref(wg2)
grating.add_ref(wg3)
grating.add_ref(helper1).move((0, radius_rowland))
grating.add_ref(helper2).move((0, 2 * radius_rowland))
grating.show()
