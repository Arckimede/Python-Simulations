import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Constants

mu = 3.986e14           # Earth's gravitational parameter 
R_earth = 6.371e6       # Earth radius (m)

# Orbit radii
r1 = R_earth + 300e3    # Initial orbit (300 km altitude)
r2 = R_earth + 1000e3   # Target orbit (1000 km altitude)

dt = 1                  # Time step (seconds)
t_max = 20000           # Total simulation time
steps = int(t_max / dt)


# Initial Conditions 

pos = np.array([r1, 0.0])
v_circular = np.sqrt(mu / r1)
vel = np.array([0.0, v_circular])

trajectory = []
burn1_done = False
burn2_done = False


# Physics: Two-body gravity

def acceleration(r):
    r_norm = np.linalg.norm(r)
    return -mu * r / r_norm**3

def rk4_step(r, v, dt):
    a1 = acceleration(r)
    k1_r = v
    k1_v = a1

    a2 = acceleration(r + 0.5*dt*k1_r)
    k2_r = v + 0.5*dt*k1_v
    k2_v = a2

    a3 = acceleration(r + 0.5*dt*k2_r)
    k3_r = v + 0.5*dt*k2_v
    k3_v = a3

    a4 = acceleration(r + dt*k3_r)
    k4_r = v + dt*k3_v
    k4_v = a4

    r_next = r + (dt/6)*(k1_r + 2*k2_r + 2*k3_r + k4_r)
    v_next = v + (dt/6)*(k1_v + 2*k2_v + 2*k3_v + k4_v)

    return r_next, v_next


# Hohmann Delta-V Calculations 

dv1 = np.sqrt(mu/r1)*(np.sqrt(2*r2/(r1+r2)) - 1)
dv2 = np.sqrt(mu/r2)*(1 - np.sqrt(2*r1/(r1+r2)))

print("Delta-v1:", dv1, "m/s")
print("Delta-v2:", dv2, "m/s")
print("Total Delta-v:", dv1 + dv2, "m/s")

# Simulation Loop

previous_r = np.linalg.norm(pos)

for i in range(steps):

    r_norm = np.linalg.norm(pos)

    # First burn at start
    if not burn1_done:
        vel += dv1 * vel / np.linalg.norm(vel)
        burn1_done = True

    # Detect apoapsis (radius starts decreasing)
    if burn1_done and not burn2_done:
        if r_norm < previous_r:
            vel += dv2 * vel / np.linalg.norm(vel)
            burn2_done = True
            print("Second burn applied at t =", i*dt, "seconds")

    previous_r = r_norm

    trajectory.append(pos.copy())
    pos, vel = rk4_step(pos, vel, dt)

trajectory = np.array(trajectory)


# Visualization
fig, ax = plt.subplots()
ax.set_aspect('equal')
ax.set_xlim(-1.5*r2, 1.5*r2)
ax.set_ylim(-1.5*r2, 1.5*r2)

earth = plt.Circle((0, 0), R_earth, color='blue')
ax.add_patch(earth)

line, = ax.plot([], [], 'r-', lw=1)
point, = ax.plot([], [], 'ro')

def update(frame):
    line.set_data(trajectory[:frame, 0], trajectory[:frame, 1])
    point.set_data(
        [trajectory[frame, 0]],
        [trajectory[frame, 1]]
    )
    return line, point

ani = FuncAnimation(fig, update, frames=range(0, len(trajectory), 5), interval=10)
plt.title("Hohmann Transfer Simulation (Impulse-Based)")
plt.show()