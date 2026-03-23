import numpy as np


def ellipse_intersection_finder(
    x1: float = 0.0,
    y1: float = 0.0,
    x2: float = 0.0,
    y2: float = 0.0,
    x3: float = 0.0,
    y3: float = 0.0,
    a1: float = 0.0,
    a2: float = 0.0,
    center_angle_deg: float = 45,
    opening_angle_deg: float = 90,
) -> tuple[float, float, float, float] | None:
    """寻找两个共一个焦点的椭圆交点

    参数:
        (x1, y1) (float, float): 两个椭圆的公共焦点
        (x2, y2) (float, float): 第一个椭圆的第二个焦点
        (x3, y3) (float, float): 第二个椭圆的第二个焦点
        a1, a2 (float, float): 两个椭圆的长半轴 (semi-major axis)
        center_angle_deg, opening_angle_deg (float, float): 搜索扇区中心角度和张角 (单位: 度)

    返回:
        [IntersectionX, IntersectionY, IntersectionR, IntersectionPhi]
    """

    discretization = 120
    intersection_angle_accuracy = 1e-15
    k = np.linspace(0, 2 * np.pi, discretization + 1)  # 角度采样点

    focus_vec1 = np.array([x2 - x1, y2 - y1])
    focus_vec2 = np.array([x3 - x1, y3 - y1])

    # 检查椭圆合法性
    if np.linalg.norm(focus_vec1) >= 2 * a1:
        print("Warning: Degenerate ellipse 1, major axis too small")
    if np.linalg.norm(focus_vec2) >= 2 * a2:
        print("Warning: Degenerate ellipse 2, major axis too small")

    # 椭圆参数
    b1 = np.sqrt(a1 ** 2 - (np.linalg.norm(focus_vec1) / 2) ** 2)
    eps1 = np.sqrt(1 - (b1 / a1) ** 2)

    b2 = np.sqrt(a2 ** 2 - (np.linalg.norm(focus_vec2) / 2) ** 2)
    eps2 = np.sqrt(1 - (b2 / a2) ** 2)

    theta1 = np.arctan2(focus_vec1[1], focus_vec1[0])
    theta2 = np.arctan2(focus_vec2[1], focus_vec2[0])

    # 开始扫描
    low_phi = 0.0
    low_r1 = (a1 * (1 - eps1 ** 2)) / (1 - eps1 * np.cos(theta1 - low_phi))
    low_r2 = (a2 * (1 - eps2 ** 2)) / (1 - eps2 * np.cos(theta2 - low_phi))
    rdiff_low = low_r2 - low_r1

    intersection_list = []
    if np.sign(rdiff_low) == 0:
        intersection_list.append(low_phi)

    for i in range(discretization):
        high_phi = (i + 1) * 2 * np.pi / discretization
        high_r1 = (a1 * (1 - eps1 ** 2)) / (1 - eps1 * np.cos(theta1 - high_phi))
        high_r2 = (a2 * (1 - eps2 ** 2)) / (1 - eps2 * np.cos(theta2 - high_phi))
        rdiff_high = high_r2 - high_r1

        if np.sign(rdiff_high) == 0:
            intersection_list.append(high_phi)
        elif np.sign(rdiff_high) != np.sign(rdiff_low):
            # 二分法
            lphi, hphi = low_phi, high_phi
            rdiff_l, rdiff_h = rdiff_low, rdiff_high
            while (hphi - lphi) > intersection_angle_accuracy:
                iphi = 0.5 * (hphi + lphi)
                ir1 = (a1 * (1 - eps1 ** 2)) / (1 - eps1 * np.cos(theta1 - iphi))
                ir2 = (a2 * (1 - eps2 ** 2)) / (1 - eps2 * np.cos(theta2 - iphi))
                rdiff_i = ir2 - ir1
                if np.sign(rdiff_i) == 0:
                    break
                elif np.sign(rdiff_i) != np.sign(rdiff_l):
                    hphi, rdiff_h = iphi, rdiff_i
                else:
                    lphi, rdiff_l = iphi, rdiff_i
            intersection_list.append(0.5 * (lphi + hphi))

        low_phi, rdiff_low = high_phi, rdiff_high

    # 转换角度范围限制
    center_angle = np.deg2rad(center_angle_deg)
    opening_angle = np.deg2rad(opening_angle_deg)

    found_angle = None
    for phi in intersection_list:
        if (phi >= center_angle - opening_angle / 2) and (phi <= center_angle + opening_angle / 2):
            found_angle = phi

    if found_angle is None:
        return None

    # 计算交点坐标
    intersection_r = (a1 * (1 - eps1 ** 2)) / (1 - eps1 * np.cos(theta1 - found_angle))
    intersection_x = intersection_r * np.cos(found_angle) + x1
    intersection_y = intersection_r * np.sin(found_angle) + y1
    intersection_phi = np.rad2deg(found_angle)

    return intersection_x, intersection_y, intersection_r, intersection_phi
