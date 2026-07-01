import math

# King Fahd minarets
m0 = (-198.9, -151.6)
m1 = (-229.0, -128.0)

# Midpoint of the gate
cx = (m0[0] + m1[0]) / 2.0
cy = (m0[1] + m1[1]) / 2.0
print(f"Midpoint: {cx}, {cy}")

# Vector from m0 to m1
dx = m1[0] - m0[0]
dy = m1[1] - m0[1]
length = math.sqrt(dx*dx + dy*dy)
ux = dx / length
uy = dy / length
print(f"Edge unit vector: {ux}, {uy}")

# Inward normal (perpendicular to edge, pointing towards Kaaba (0,0))
# Perpendicular to (ux, uy) is (uy, -ux) or (-uy, ux)
# Let's check which one points to (0,0)
nx1, ny1 = uy, -ux
nx2, ny2 = -uy, ux

dot1 = (0 - cx) * nx1 + (0 - cy) * ny1
dot2 = (0 - cx) * nx2 + (0 - cy) * ny2

if dot1 > dot2:
    nx, ny = nx1, ny1
else:
    nx, ny = nx2, ny2
    
print(f"Inward normal: {nx}, {ny}")

# Place center dome at distance D inward
D = 65.0
c_dome_x = cx + D * nx
c_dome_y = cy + D * ny

print(f"Center Dome: {c_dome_x:.1f}, {c_dome_y:.1f}")

# Place side domes at distance S along the edge
S = 26.0
left_dome_x = c_dome_x - S * ux
left_dome_y = c_dome_y - S * uy
right_dome_x = c_dome_x + S * ux
right_dome_y = c_dome_y + S * uy

print(f"Left Dome: {left_dome_x:.1f}, {left_dome_y:.1f}")
print(f"Right Dome: {right_dome_x:.1f}, {right_dome_y:.1f}")

print("\nPOSITIONS = [")
print(f"    ({left_dome_x:.1f}, {left_dome_y:.1f}),")
print(f"    ({c_dome_x:.1f}, {c_dome_y:.1f}),")
print(f"    ({right_dome_x:.1f}, {right_dome_y:.1f}),")
print("]")
