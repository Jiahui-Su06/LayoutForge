import gdsfactory as gf
import numpy as np
from numpy import cos, sin, pi, sqrt, deg2rad, rad2deg
import mydraw

c = gf.Component()
# c1 = gf.components.bend_euler(radius=100, angle=90, p=1, with_arc_floorplan=True, width=4,
#                               cross_section='strip', allow_min_radius_violation=False).copy()
# c2 = gf.components.bend_euler(radius=50, angle=-90, p=0.5, with_arc_floorplan=True, width=3,
#                               cross_section='strip', allow_min_radius_violation=False).copy()
# c1.rotate(180)
# c1.move([20,20])
# c2.rotate(90)
# c2.move([20,20])
# c.add_ref(c1)
# c.add_ref(c2)
# c.draw_ports()
# ring = mydraw.ring_arc(radius=125, width=1,
#                        theta_start=0, theta_stop=90,
#                        x_center=0, y_center=0,
#                        angle_resolution=0.1,
#                        layer=(1, 0))
# c.add_ref(ring)
sector = mydraw.sector(radius=100,
                       angle_start=45,
                       angle_stop=135,
                       x_center=0, y_center=0,
                       angle_resolution=0.5, layer=(4, 1))
# wg = mydraw.waveguide(start=(0, 0), end=(200, 0),  # 增加补偿长度，填缝隙
#                       width=11.2, layer=(4, 2))
# c.add_ref(taper)
# c.add_ref(wg)
c.add_ref(sector)
c.show()
# c.write_gds(r"E:\桌面\Euler_Bend_100um.gds")



