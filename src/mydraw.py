import numpy as np
from numpy import cos, sin, pi, deg2rad, rad2deg, acos, atan
import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import LayerSpec
from gdsfactory.typings import ComponentSpec, CrossSectionSpec
from gdsfactory.components.tapers.taper import taper as taper_function
from gdsfactory.components.waveguides.straight import straight as straight_function


def ring_arc(
    radius: float = 10.0,
    width: float = 0.5,
    theta_start: float = 0.0,
    theta_stop: float = 90.0,
    x_center: float = 0.0,
    y_center: float = 0.0,
    angle_resolution: float = 2.5,
    layer: LayerSpec = (1, 0)
) -> Component:
    """Returns a ring arc.

    Args:
        radius: radius of the ring.
        width: width of the ring.
        theta_start: starting angle of the ring.
        theta_stop: stopping angle of the ring.
        x_center: 圆环弧的中心坐标x
        y_center: 圆环弧的中心坐标y
        angle_resolution: resolution of the ring.
        layer: gdsfactory layer
    """
    if radius <= 0:
        raise ValueError(f"radius={radius} must be > 0")
    if width <= 0:
        raise ValueError(f"width={width} must be > 0")
    if theta_stop < theta_start:
        raise ValueError(f"theta_stop={theta_stop} must be >= theta_start={theta_start}")

    c = Component()
    inner_radius = radius - width / 2
    outer_radius = radius + width / 2
    n = int(np.round((theta_stop - theta_start) / angle_resolution)) + 1
    t = np.linspace(theta_start, theta_stop, n) * pi / 180
    inner_points_x = x_center + inner_radius * cos(t)
    inner_points_y = y_center + inner_radius * sin(t)
    outer_points_x = x_center + outer_radius * cos(t)
    outer_points_y = y_center + outer_radius * sin(t)
    xpts = np.concatenate([inner_points_x, outer_points_x[::-1]])
    ypts = np.concatenate([inner_points_y, outer_points_y[::-1]])
    c.add_polygon(points=list(zip(xpts, ypts, strict=False)), layer=layer)
    return c


def sector(
    radius: float = 10.0,
    angle_start: float = 0.0,
    angle_stop: float = 90.0,
    x_center: float = 0.0,
    y_center: float = 0.0,
    angle_resolution: float = 2.5,
    layer: LayerSpec = (1, 0)
) -> Component:
    """Generate a circle geometry.

    Args:
        radius: of the circle.
        angle_start: starting angle of the sector.
        angle_stop: stopping angle of the sector.
        x_center: 扇形的中心坐标x
        y_center: 扇形的中心坐标y
        angle_resolution: number of degrees per point.
        layer: layer.
    """
    if radius <= 0:
        raise ValueError(f"radius={radius} must be > 0")
    if angle_stop <= angle_start:
        raise ValueError(f"theta_stop={angle_stop} must be > theta_start={angle_start}")
    c = Component()
    num_points = int(np.round((angle_stop - angle_start) / angle_resolution)) + 1
    theta = np.deg2rad(np.linspace(angle_start, angle_stop, num_points, endpoint=True))
    points = np.stack((x_center + radius * cos(theta), y_center + radius * sin(theta)), axis=-1)
    points = np.append(points, np.array([[x_center, y_center]]), axis=0)
    c.add_polygon(points=points, layer=layer)
    return c


def ellipse_arc_points(
    a: float = 10.0,
    b: float = 5.0,
    theta_start: float = 0.0,
    theta_stop: float = 360.0,
    rotate_angle: float = 0.0,
    angle_resolution: float = 1.0,
    center: tuple[float, float] = (0.0, 0.0),
) -> np.ndarray:
    """生成椭圆弧坐标点

    Parameters
    ----------
    a (float): 椭圆长半轴
    b (float): 椭圆短半轴
    theta_start (float): 椭圆弧线起始角度（单位：度）
    theta_stop (float): 终止角度
    rotate_angle (float): 椭圆旋转角度（相对于椭圆中心）
    angle_resolution (float): 绘图角分辨率（度）
    center (tuple[float, float]): 椭圆中心点坐标

    Returns
    -------
    np.ndarray: 椭圆弧离散点坐标

    """
    # 输入检测：a长半轴  和短半轴 b 大于 0
    if a <= 0:
        raise ValueError(f"a={a} must be > 0")
    elif b <= 0:
        raise ValueError(f"b={b} must be > 0")

    # 根据角分辨率计算绘图所用坐标点总数
    num_points = int(np.round(np.abs(theta_stop-theta_start) / angle_resolution)) + 1
    # 防止超出 theta_stop 的范围
    theta = np.linspace(np.deg2rad(theta_start), np.deg2rad(theta_stop), num_points)

    # 计算椭圆坐标，计算大量数据采用 numpy 库
    x = a * np.cos(theta)
    y = b * np.sin(theta)

    # 旋转椭圆，利用旋转矩阵实现
    rotate_angle_rad = np.deg2rad(rotate_angle)
    xr = x * np.cos(rotate_angle_rad) - y * np.sin(rotate_angle_rad)
    yr = x * np.sin(rotate_angle_rad) + y * np.cos(rotate_angle_rad)

    # 平移椭圆
    x_final = xr + center[0]
    y_final = yr + center[1]

    return np.column_stack((x_final, y_final))


def elliptical_arc_ring(
    a_inner: float = 0.0,
    b_inner: float = 0.0,
    a_outer: float = 0.0,
    b_outer: float = 0.0,
    theta_start: float = 0.0,
    theta_stop: float = 0.0,
    rotate_angle: float = 0.0,
    angle_resolution: float = 1.0,
    center: tuple[float, float] = (0.0, 0.0),
    layer: tuple[int, int] = (1, 0)
) -> gf.Component:
    """绘制椭圆弧环
    参数：
        a_inner, b_inner (float): 内椭圆 a 和 b 长度
        a_outer, b_outer (float): 外椭圆 a 和 b 长度
        theta_start, theta_stop: 椭圆坐标系中的起止角度 (度)
        rotate_angle: 椭圆环整体旋转角度 (度)
        angle_resolution (float): 绘图角分辨率
        center (float): 椭圆环中心
        layer (float): 绘制层
    """
    c = gf.Component()

    # 外弧 (正向)
    outer_arc = ellipse_arc_points(a_outer, b_outer, theta_start, theta_stop, rotate_angle=rotate_angle,
                                   angle_resolution=angle_resolution, center=center)
    # 内弧 (反向)
    inner_arc = ellipse_arc_points(a_inner, b_inner, theta_stop, theta_start, rotate_angle=rotate_angle,
                                   angle_resolution=angle_resolution, center=center)

    # 拼接椭圆环
    ring_points = np.vstack([outer_arc, inner_arc])
    c.add_polygon(ring_points, layer=layer)

    return c


def taper(
    w1: float = 1.0,
    w2: float = 2.0,
    length: float = 10.0,
    rotate_angle: float = 0.0,
    center: tuple[float, float] = (0.0, 0.0),
    layer: tuple[int, int] = (1, 0)
) -> gf.Component:
    """绘制锥形波导
        参数：
            w1, w2 (float): taper短边、长边宽度
            length (float): taper长度
            rotate_angle (float): 锥形波导倾斜角度（度）
            center (float): 锥形波导短边中心
            layer (float): gdsfactory绘制层
        """

    c = gf.Component()
    x = center[0]
    y = center[1]
    theta = deg2rad(rotate_angle)
    v1 = [x + w1 / 2 * sin(theta), y - w1 / 2 * cos(theta)]
    v2 = [x - w1 / 2 * sin(theta), y + w1 / 2 * cos(theta)]
    v3 = [x + length * cos(theta) - w2 / 2 * sin(theta),
          y + length * sin(theta) + w2 / 2 * cos(theta)]
    v4 = [x + length * cos(theta) + w2 / 2 * sin(theta),
          y + length * sin(theta) - w2 / 2 * cos(theta)]
    vtx = [v1,
           v2,
           v3,
           v4]
    c.add_polygon(vtx, layer=layer)
    return c


def curved_taper(
    m: float = 2.0,
    w1: float = 1.0,
    w2: float = 2.0,
    length: float = 10.0,
    n: int = 100,
    rotate_angle: float = 0.0,
    center: tuple[float, float] = (0.0, 0.0),
    layer: tuple[int, int] = (1, 0)
) -> gf.Component:
    """绘制锥形波导
        参数：
            m (float): m参数
            w1, w2 (float): taper短边、长边宽度
            length (float): taper长度
            n (int): 描点数目
            rotate_angle (float): 锥形波导倾斜角度（度）
            center (float): 锥形波导短边中心
            layer (float): gdsfactory绘制层
        """

    c = gf.Component()
    alpha = (w1 - w2) / (length ** m)
    x = np.linspace(0, length, n)
    w = alpha * (length - x) ** m + w2
    y1 = w / 2
    y2 = - w / 2
    P1 = np.column_stack((x, y1))  # 锥形上段点
    P2 = np.column_stack((x, y2))  # 下段
    vtx = []
    vtx.extend(P1)
    vtx.extend(P2[::-1])
    theta = np.deg2rad(180)  # 旋转角度（°→弧度）
    R = np.array([[np.cos(theta), -np.sin(theta)],
                  [np.sin(theta), np.cos(theta)]])  # 旋转矩阵
    # 旋转
    vtx_rot = vtx @ R.T
    # 平移
    offset = np.array([length, 0])  # 平移目标点 (x0, y0)
    vtx_new = vtx_rot + offset
    theta = np.deg2rad(rotate_angle)  # 旋转角度（°→弧度）
    R = np.array([[np.cos(theta), -np.sin(theta)],
                  [np.sin(theta), np.cos(theta)]])  # 旋转矩阵
    # 旋转
    vtx_rot = vtx_new @ R.T
    # 平移
    offset = np.array(center)  # 平移目标点 (x0, y0)
    vtx_new = vtx_rot + offset
    c.add_polygon(vtx_new, layer=layer)
    return c

def circle(
    radius: float = 10.0,
    theta_start: float = 0.0,
    theta_stop: float = 90.0,
    x_center: float = 0.0,
    y_center: float = 0.0,
    angle_resolution: float = 2.5,
):
    if radius <= 0:
        raise ValueError(f"radius={radius} must be > 0")
    if theta_stop <= theta_start:
        raise ValueError(f"theta_stop={theta_stop} must be > theta_start={theta_start}")
    num_points = int(np.round((theta_stop - theta_start) / angle_resolution)) + 1
    theta = np.deg2rad(np.linspace(theta_start, theta_stop, num_points, endpoint=True))
    points = np.stack((x_center + radius * cos(theta), y_center + radius * sin(theta)), axis=-1)
    return points


def waveguide(
    start: tuple[float, float] = (0.0, 0.0),
    end: tuple[float, float] = (10.0, 0.0),
    width: float = 0.5,
    layer: tuple[int, int] = (1, 0)
) -> gf.Component:
    """已知起点、终点，绘制直波导

    参数：
        start (tuple[float, float]): 波导起始点
        end (tuple[float, float]): 直波导终止点
        width (float): 波导宽度
        layer (tuple[int, int]): 绘制层
    """
    dx, dy = end[0]-start[0], end[1]-start[1]
    length = np.sqrt(dx**2 + dy**2)
    angle = np.degrees(np.arctan2(dy, dx))

    xs = gf.cross_section.strip(width=width, layer=layer)
    wg = gf.components.straight(length=length, cross_section=xs)

    c = gf.Component()
    ref = c.add_ref(wg)
    ref.move(start)
    ref.rotate(angle, center=start)
    return c


def my_mmi1x2(
    width: float = 1.0,
    width_taper: float = 2.0,
    length_taper_in: float = 10.0,
    length_taper_out: float = 20.0,
    length_mmi: float = 30.0,
    width_mmi: float = 10.0,
    gap_mmi: float = 2.0,
    cross_section="strip",
    layer: LayerSpec | None = None,
):

    c = gf.Component()
    xs = gf.get_cross_section(cross_section)

    # ======================
    # 输入 taper
    # ======================
    taper_in = gf.components.taper(
        length=length_taper_in,
        width1=width,
        width2=width_taper,
        cross_section=cross_section,
        layer=layer
    )
    t_in = c.add_ref(taper_in)
    t_in.move((0, 0))  # y=0 保证对齐

    # ======================
    # MMI 区（矩形）
    # ======================
    mmi = gf.components.rectangle(
        size=(length_mmi, width_mmi),
        layer=layer,
    )
    m = c.add_ref(mmi)
    # 对齐左边界到输入 taper 的右边
    m.xmin = t_in.xmax
    # 保证 y 中心对齐
    m.y = 0

    # ======================
    # 输出 tapers
    # ======================
    taper_out = gf.components.taper(
        length=length_taper_out,
        width1=width_taper,
        width2=width,
        cross_section=cross_section,
        layer=layer
    )

    y_offset = gap_mmi / 2 + width_taper / 2

    t_out1 = c.add_ref(taper_out)
    t_out2 = c.add_ref(taper_out)

    # 对齐输入端到 MMI 右边
    t_out1.xmin = m.xmax
    t_out2.xmin = m.xmax
    # 对齐 y
    t_out1.y = +y_offset
    t_out2.y = -y_offset

    # ======================
    # 端口定义
    # ======================
    c.add_port("o1", port=t_in.ports["o1"], cross_section=cross_section, layer=layer)
    c.add_port("o2", port=t_out1.ports["o2"], cross_section=cross_section, layer=layer)
    c.add_port("o3", port=t_out2.ports["o2"], cross_section=cross_section, layer=layer)

    return c

def bend_s_ring(
    w: float = 0.5,
    height: float = 10.0,
    width: float = 0.5,
    x_center: float = 0.0,
    y_center: float = 0.0,
    angle_resolution: float = 2.5,
    radius_min: float = 10,
    layer: LayerSpec = (1, 0)
) -> Component:
    """绘制Sbend

    Args:
        w: width of the ring.
        height: S bend的高度，可以是负数，符号代表方向
        x_center: S bend的起始点坐标x
        y_center: S bend的起始点坐标y
        angle_resolution: resolution of the ring.
        layer: gdsfactory layer
    """
    if height >= 0:
        dir = 1
    else:
        height = -height
        dir = 0

    # if radius <= 0:
    #     raise ValueError(f"radius={radius} must be > 0")
    if w <= 0:
        raise ValueError(f"width={w} must be > 0")
    # if height > radius*2:
    #     raise ValueError(f"height={height} must be <= radius*2")
    # if width > radius*2:
    #     raise ValueError(f"width={width} must be <= radius*2")

    c = Component()
    theta = 2 * atan(height / width)
    radius = width / sin(theta) / 2
    if radius < radius_min:
        raise ValueError(f"radius={height} must be >= {radius_min}")
    inner_radius = radius - w / 2
    outer_radius = radius + w / 2
    angle = rad2deg(theta)
    n = int(np.round(angle / angle_resolution)) + 1
    if dir == 1:
        x_ring1 = x_center
        y_ring1 = y_center + radius
        x_ring2 = x_ring1 + radius * 2 * sin(theta)
        y_ring2 = y_ring1 - radius * 2 * cos(theta)
        t1 = np.linspace(-90, -90 + angle, n) * pi / 180
        t2 = np.linspace(90, 90 + angle, n) * pi / 180

    else:
        x_ring1 = x_center
        y_ring1 = y_center - radius
        x_ring2 = x_ring1 + radius * 2 * sin(theta)
        y_ring2 = y_ring1 + radius * 2 * cos(theta)
        t1 = np.linspace(90-angle, 90, n) * pi / 180
        t2 = np.linspace(-90-angle, -90, n) * pi / 180

    inner_points_x_1 = x_ring1 + inner_radius * cos(t1)
    inner_points_y_1 = y_ring1 + inner_radius * sin(t1)
    outer_points_x_1 = x_ring1 + outer_radius * cos(t1)
    outer_points_y_1 = y_ring1 + outer_radius * sin(t1)
    inner_points_x_2 = x_ring2 + inner_radius * cos(t2)
    inner_points_y_2 = y_ring2 + inner_radius * sin(t2)
    outer_points_x_2 = x_ring2 + outer_radius * cos(t2)
    outer_points_y_2 = y_ring2 + outer_radius * sin(t2)
    if dir == 1:
        xpts = np.concatenate([inner_points_x_1, outer_points_x_2[::-1], inner_points_x_2, outer_points_x_1[::-1]])
        ypts = np.concatenate([inner_points_y_1, outer_points_y_2[::-1], inner_points_y_2, outer_points_y_1[::-1]])
    else:
        xpts = np.concatenate([inner_points_x_1[::-1], outer_points_x_2, inner_points_x_2[::-1], outer_points_x_1])
        ypts = np.concatenate([inner_points_y_1[::-1], outer_points_y_2, inner_points_y_2[::-1], outer_points_y_1])
    c.add_polygon(points=list(zip(xpts, ypts, strict=False)), layer=layer)
    return c
