import numpy as np
import matplotlib.pyplot as plt
import math
import matplotlib.patches as patches

g = 9.8 # Earth's gravity
dt = 0.01

class Pendulum:
    
    def __init__(self, pendulumLength: int, theta: int, angularVelocity: int, startingPos: int, endingPos: int) -> None:
        self.pendulumLength = pendulumLength
        self.theta = theta
        self.angularVelocity = angularVelocity
        self.startingPos = startingPos
        self.endingPos = endingPos
    
    def calculateAngularAcc(self):
        return - (g / self.pendulumLength) * np.sin(self.theta)
    
    def updateAngularVelocity(self) -> None:
        self.angularVelocity += self.calculateAngularAcc() * dt
    
    def updateAngle(self):
        self.theta += self.angularVelocity * dt
        
    def plot(self) -> np.array:
        x = self.pendulumLength * np.sin(self.theta)
        y = -self.pendulumLength * np.cos(self.theta)
        return np.array([x, y])
    
# pendulum
pendulum = Pendulum(3, np.radians(45), 0, 3, 1)
pivot = np.array([3, 3])
pendulumCircle = patches.Circle(xy=(pendulum.startingPos, pendulum.endingPos), radius = 0.25, color = '#F59C27')

# line connected to pendulum
lineStartingPos, lineEndingPos = np.array([3, 3]), np.array([3, 1])

# plotting
fig, ax = plt.subplots(1, 1, constrained_layout = True, figsize = (10, 6))
linePlot, = ax.plot(lineStartingPos, lineEndingPos, color = '#27E0F5')
ax.add_patch(pendulumCircle)
ax.set_xlim(0, 6)
ax.set_ylim(0, 6)
plt.title(label="Swinging Pendulum Physics", fontfamily = 'monospace', color = '#000000')

for _ in range(10000):
    pendulum.updateAngularVelocity()
    pendulum.updateAngle()
    
    pos = pendulum.plot() + pivot
    
    pendulumCircle.set_center(pos)
    linePlot.set_data([pivot[0], pos[0]], [pivot[1], pos[1]])
    
    plt.pause(0.01)

plt.show()