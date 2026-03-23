import gdsfactory as gf
import numpy as np
from numpy import cos, sin, pi, deg2rad, rad2deg
from gdsfactory.component import Component
from gdsfactory.typings import LayerSpec

def archimedean_spiral(
    a: float = 10.0,  # 起始半径
    pitch: float = 10.0,  # 螺距
    turns: float = 4,  # 圈数
    width: float = 0.8,  # 波导宽度
    x_center: float = 0.0,
    y_center: float = 0.0,
    angle_resolution: float = 2.5,
    layer: LayerSpec = (1, 0)
) -> Component:
    """Returns a archimedean spiral.

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
    if a <= 0:
        raise ValueError(f"radius={a} must be > 0")
    if width <= 0:
        raise ValueError(f"width={width} must be > 0")
    if turns <= 0:
        raise ValueError(f"turns={turns} must be > 0")

    theta_offset = 0
    c = Component()
    b = pitch / (2 * np.pi)  # 计算单位角度增长的曲线半径
    n = int(np.round((360 * turns - theta_offset)/ angle_resolution)) + 1
    t = np.linspace(theta_offset, 360 * turns, n) * pi / 180
    r = a + b * t  # r(theta)
    inner_radius = r - width / 2
    outer_radius = r + width / 2
    inner_points_x = x_center + inner_radius * cos(t)
    inner_points_y = y_center + inner_radius * sin(t)
    outer_points_x = x_center + outer_radius * cos(t)
    outer_points_y = y_center + outer_radius * sin(t)
    xpts = np.concatenate([inner_points_x, outer_points_x[::-1]])
    ypts = np.concatenate([inner_points_y, outer_points_y[::-1]])
    c.add_polygon(points=list(zip(xpts, ypts, strict=False)), layer=layer)
    return c


# ---------- test ----------------
if __name__ == "__main__":
    c = gf.Component()
    Spiral = archimedean_spiral(
        a=0.5,  # 起始半径
        pitch=(3-1)/1.5,  # 螺距
        turns=1.5,  # 圈数
        width=0.89,  # 波导宽度
        x_center=0.0,
        y_center=0.0,
        angle_resolution=1,
        layer=(1, 0)
    )
    c.add_ref(Spiral)
    c.show()
    c.write_gds(r"E:\桌面\Archimedean_Spiral.gds")
