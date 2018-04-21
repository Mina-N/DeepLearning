import numpy as np
import nvector as nv

frame = nv.FrameE(name='WGS84')

xyz = str(input("Input XYZ ECEF Coordinate: "))

try:
    x, y, z = xyz.split()

    posECEF = np.vstack((float(x.strip(',; ')), float(y.strip(',; ')), float(z.strip(',; '))))
    p_eb_e = frame.ECEFvector(posECEF)
    point = p_eb_e.to_geo_point()
    print()
    lat, lon, alt = point.latitude_deg[0], point.longitude_deg[0], -point.z[0]
    print("Converted LLA: ", lat, lon, alt)

except ValueError as e:
    print("Error: ", str(e))
except Exception as e:
    print("Exception: ", str(e))

