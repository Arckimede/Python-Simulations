import numpy as np
import time as t
from vpython import *

#variables
projectile = sphere(pos=vector(0, 20, 0), radius=1.5, color=color.yellow, make_trail=True, retain=50, trail_radius=0.2, trail_type="points", 
                    trail_color=color.white)
projectile.v0 = 50
projectile.theta = 45
projectile.phi = 45
projectile.G = 9.81

projectileLabel = label(pos=projectile.pos, text="", xoffset=20, yoffset=20, align="center", 
                        color=color.white, font="monospace")

groundPlane = box(pos=vector(150, 0, 150), color=color.magenta, size=vector(100, 2, 100))

projectileVisible = True
kDragCoefficient = 0.05 # linear drag
dt = 0.01
thetaRad = np.radians(projectile.theta)
phiRad = np.radians(projectile.phi)

v = vector(projectile.v0 * np.cos(thetaRad) * np.cos(phiRad), 
           projectile.v0 * np.sin(thetaRad),
           projectile.v0 * np.cos(thetaRad) * np.sin(phiRad)
           )

def handleMovement():
    global kDragCoefficient, dt, v
    
    # apply gravity
    v.y = v.y - projectile.G*dt
        
    # apply linear drag to velocity vector        
    v = v * (1 - kDragCoefficient * dt)
    
    # update position
    projectile.pos = projectile.pos + v * dt

def changeDragCoefficient(evt):
    global kDragCoefficient 
    kDragCoefficient = evt.value
    
def onGroundPlaneCollision():
    global projectileVisible
    
    if projectile.pos.y - (projectile.radius * 0.5) <= groundPlane.pos.y:
        projectileVisible = False
        projectile.make_trail = False
        projectile.visible = False
        projectile.delete()
        projectileLabel.visible = False
        projectileLabel.delete()

dragCoeffSlider = slider(bind=changeDragCoefficient, min=0.01, max=0.1, step=0.01, value=0.05)

while True:
    rate(30)
    projectileLabel.pos = projectile.pos
    projectileLabel.text = f"Moving at x:{np.round(projectile.pos.x, decimals=2)}, y:{np.round(projectile.pos.y, decimals=2)}, z:{np.round(projectile.pos.z, decimals=2)}"

    handleMovement()
    onGroundPlaneCollision()
    
    if projectileVisible:
        scene.camera.follow(projectile)
    else:
        scene.camera.follow(None)
    
