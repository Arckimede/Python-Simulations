import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# Physical Parameters
g = 9.81       # gravity
L1 = 1.0       # length of pendulum: 1
L2 = 1.0       # length of pendulum: 2
m1 = 1.0       # mass: 1
m2 = 1.0       # mass: 2


# Equations of Motion
def derivatives(y):
    theta1, omega1, theta2, omega2 = y

    delta = theta2 - theta1

    denom1 = (m1 + m2)*L1 - m2*L1*np.cos(delta)**2
    denom2 = (L2/L1) * denom1

    dtheta1 = omega1
    dtheta2 = omega2

    domega1 = (
        m2*L1*omega1**2*np.sin(delta)*np.cos(delta)
        + m2*g*np.sin(theta2)*np.cos(delta)
        + m2*L2*omega2**2*np.sin(delta)
        - (m1 + m2)*g*np.sin(theta1)
    ) / denom1

    domega2 = (
        -m2*L2*omega2**2*np.sin(delta)*np.cos(delta)
        + (m1 + m2)*g*np.sin(theta1)*np.cos(delta)
        - (m1 + m2)*L1*omega1**2*np.sin(delta)
        - (m1 + m2)*g*np.sin(theta2)
    ) / denom2

    return np.array([dtheta1, domega1, dtheta2, domega2])


# RK4 Integrator

def rk4_step(y, dt):
    k1 = derivatives(y)
    k2 = derivatives(y + 0.5 * dt * k1)
    k3 = derivatives(y + 0.5 * dt * k2)
    k4 = derivatives(y + dt * k3)
    return y + (dt / 6.0)*(k1 + 2*k2 + 2*k3 + k4)


# Energy Calculation
def total_energy(y):
    theta1, omega1, theta2, omega2 = y

    x1 = L1*np.sin(theta1)
    y1 = -L1*np.cos(theta1)
    x2 = x1 + L2*np.sin(theta2)
    y2 = y1 - L2*np.cos(theta2)

    v1_sq = (L1*omega1)**2
    v2_sq = (
        v1_sq
        + (L2*omega2)**2
        + 2*L1*L2*omega1*omega2*np.cos(theta1-theta2)
    )

    T = 0.5*m1*v1_sq + 0.5*m2*v2_sq
    V = m1*g*y1 + m2*g*y2

    return T + V

# Simulation Setup
dt = 0.01
t_max = 20
steps = int(t_max / dt)

# Initial conditions (slightly unstable setup)
y = np.array([np.pi/2, 0, np.pi/2 + 0.01, 0])

trajectory = np.zeros((steps, 4))
energy = np.zeros(steps)

for i in range(steps):
    trajectory[i] = y
    energy[i] = total_energy(y)
    y = rk4_step(y, dt)


# Convert to Cartesian
theta1 = trajectory[:, 0]
theta2 = trajectory[:, 2]

x1 = L1*np.sin(theta1)
y1 = -L1*np.cos(theta1)

x2 = x1 + L2*np.sin(theta2)
y2 = y1 - L2*np.cos(theta2)


# Animation
fig, ax = plt.subplots()
ax.set_xlim(-2.2, 2.2)
ax.set_ylim(-2.2, 2.2)
ax.set_aspect('equal')

line, = ax.plot([], [], 'o-', lw=2, color='#1E94E3')

def update(frame):
    line.set_data(
        [0, x1[frame], x2[frame]],
        [0, y1[frame], y2[frame]]
    )
    return line,

ani = FuncAnimation(fig, update, frames=steps, interval=dt*1000)
plt.title("Double Pendulum Simulation (RK4)")
plt.show()


# Energy Drift Plot
plt.figure()
plt.plot(np.arange(steps)*dt, energy, color='#E3B81E')
plt.title("Total Energy Over Time")
plt.xlabel("Time (s)")
plt.ylabel("Energy")
plt.show()