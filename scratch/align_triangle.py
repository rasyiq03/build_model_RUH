import math

# King Fahd minarets
m0 = (-198.9, -151.6)
m1 = (-229.0, -128.0)

# Midpoint of the gate
cx = (m0[0] + m1[0]) / 2.0
cy = (m0[1] + m1[1]) / 2.0
print(f"Gate Midpoint: {cx:.1f}, {cy:.1f}")

# Vector from m0 to m1 (edge vector)
dx = m1[0] - m0[0]
dy = m1[1] - m0[1]
length = math.sqrt(dx*dx + dy*dy)
ux = dx / length
uy = dy / length

# Inward normal (towards Kaaba)
nx1, ny1 = uy, -ux
nx2, ny2 = -uy, ux
if (0 - cx) * nx1 + (0 - cy) * ny1 > (0 - cx) * nx2 + (0 - cy) * ny2:
    nx, ny = nx1, ny1
else:
    nx, ny = nx2, ny2

# Two front domes are at distance D_front from the gate
D_front = 50.0
front_center_x = cx + D_front * nx
front_center_y = cy + D_front * ny

# Spaced by S_front left and right of the center line
S_front = 14.0
dome1_x = front_center_x - S_front * ux
dome1_y = front_center_y - S_front * uy
dome2_x = front_center_x + S_front * ux
dome2_y = front_center_y + S_front * uy

# The back dome is further inward along the center line by D_back
D_back = 28.0
dome3_x = front_center_x + D_back * nx
dome3_y = front_center_y + D_back * ny

print("\nPOSITIONS = [")
print(f"    ({dome1_x:.1f}, {dome1_y:.1f}),  # Depan Kiri")
print(f"    ({dome2_x:.1f}, {dome2_y:.1f}),  # Depan Kanan")
print(f"    ({dome3_x:.1f}, {dome3_y:.1f}),  # Belakang Tengah")
print("]")
