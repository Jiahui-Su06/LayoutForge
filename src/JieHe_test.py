import gdsfactory as gf
import mydraw as md

c = gf.Component()
# mmi = md.my_mmi1x2(width=1.1, width_taper=2.6, length_taper_in=14.3, length_taper_out=30.8, length_mmi=55.85, width_mmi=10, gap_mmi=2.6, cross_section='strip').copy()
# mmi.move([10, 10])
# c.add_ref(mmi)
# sbend = md.bend_s_ring(w=1.1, height=60.9, width=110, x_center=0.0, y_center=0.0, angle_resolution=0.1, radius_min=60, layer=(4,1))
# c.add_ref(sbend)
bend_bezier = gf.components.bend_s(width=1.1, size=(110, -60.9), npoints=99, cross_section='strip', allow_min_radius_violation=False).copy()
bend_bezier.move([10, 10])
c.add_ref(bend_bezier)
# c.draw_ports()
c.show()
c.write_gds(r"E:\桌面\Sbend.gds")
