from vpython import *
import numpy as np
import time as t
import math


canvas(width=1200, height=800)

saturnColor = vector(0.9, 0.8, 0.5)
particlesColor = vector(0.9, 0.9, 0.7)
saturn = sphere(pos=vec(0, 0, 0), radius=6.03*np.power(10, 7), color=saturnColor)
saturn.mass = 5.68e26
saturnLabel = label(pos=saturn.pos, text="Saturn", font="monospace", color=saturnColor, box=False)

# moon ex.
moon = sphere(pos=vec(2 * 10**8, 0, 0), radius=1 * 10**6, color=color.white, make_trail=True, retain=5, trail_color=color.white, trail_size=1)
moon.mass = 1 * 10**22
moon.orbitalRadius = 2 * 10**8
moon.velocity = vector(0, 0, 0)
moonLabel = label(pos=moon.pos, text="Moon", font="monospace", color=color.white, box=False)

# vectors pointing from moon
moonDirVecScaleFactor = 10**3
saturnDirArrowScaleFactor = 1 / 10
moonDirArrow = arrow(pos=vector(0, 0, 0), color=color.purple, emissive=True)
saturnDirArrow = arrow(pos=vector(0, 0, 0), color=color.purple, emissive=True)

# variables
G = 6.674 * 10**-11
dt = 3600 # 1 hour time step
particles = []

# toggles
showMoonForceOnParticles = True
showDirVectors = True

def calcAcceleration(particle):
    global G, dt
    
    rVec = saturn.pos - particle.pos
    r = mag(rVec)
    acc = (G * saturn.mass / r**2) * hat(rVec)

    return acc    

# particles' position based on Saturn and their velocities
def spawnRandomParticles(numParticles = 20):
    global dt
    
    for _ in range(0, numParticles):
        
        randX = np.random.uniform(1.7 * saturn.radius, 2 * saturn.radius)
        randY = np.random.uniform(1.7 * saturn.radius, 2 * saturn.radius)
               
        particle = sphere(pos=vector(randX, randY, 0), radius=1 * np.power(10, 5), make_trail=True, retain=15, color=particlesColor)
        particle.mass = 1
        
        rVec = particle.pos - saturn.pos
        tangentialDir = vector(-rVec.y, rVec.x, 0)
        tangentialDir = hat(tangentialDir)
        
        v = np.sqrt(G * saturn.mass / mag(rVec))
                    
        particle.velocity = tangentialDir * v
        particles.append(particle)

def moonVelocity():
    global G, dt
    
    rVecMoon = moon.pos - saturn.pos
    tangentialDirMoon = vector(-rVecMoon.y, rVecMoon.x, 0)
    tangentialDirMoon = hat(tangentialDirMoon)
    vMoon = np.sqrt(G * saturn.mass / mag(rVecMoon))
    moon.velocity = tangentialDirMoon * vMoon

def gravitationalAccFromMoon(particle):
    global G
    
    partToMoonVec = moon.pos - particle.pos
    partToMoonVecMag = mag(partToMoonVec)
    accMoon = (G * moon.mass) * (partToMoonVec / partToMoonVecMag**3)
    return accMoon

# gravitational acceleration from both Saturn and the moon on particles
def totalAcceleration(particle):
    return calcAcceleration(particle) + gravitationalAccFromMoon(particle)

def showMoonForceOnParticles(evt):
    global showMoonForceOnParticles
    
    if evt.checked:
        showMoonForceOnParticles = True
    else:
        showMoonForceOnParticles = False


showMoonForceOnParticlesCheckBox = checkbox(bind=showMoonForceOnParticles, text="Show Moon Force on Particles", checked=True)

def updateVectorArrows():
    moonDirArrow.pos = moon.pos
    moonDirArrow.axis = moonDirVecScaleFactor * moon.velocity
    moonDirArrow.shaftwidth = 0.1 * mag(moonDirArrow.axis)
    
    saturnDirArrow.pos = moon.pos
    saturnDirArrow.axis = saturnDirArrowScaleFactor * (saturn.pos - moon.pos)
    saturnDirArrow.shaftwidth = 0.1 * mag(saturnDirArrow.axis)

def showDirectionalVectors(evt):
    global showDirVectors
    
    if evt.checked:
        showDirVectors = True
    else:
        showDirVectors = False

showDirVectorsCheckbox = checkbox(bind=showDirectionalVectors, text="Show Directional Vectors", checked=True)

spawnRandomParticles(100)
moonVelocity()

while True:
    rate(10)
    
    # move particles    
    for particle in particles:
        if showMoonForceOnParticles:
            particle.velocity = particle.velocity + totalAcceleration(particle) * dt 
            particle.pos = particle.pos + particle.velocity * dt
            particle.trail_color = particlesColor
            particle.color = particlesColor
            moon.color = color.white
            moon.trail_color = color.white
        else:
            particle.velocity = particle.velocity + calcAcceleration(particle) * dt
            particle.pos = particle.pos + particle.velocity * dt
            particle.trail_color = color.orange
            particle.color = color.orange
            moon.color = color.red
            moon.trail_color = color.red
            
    # move moon
    moon.velocity = moon.velocity + calcAcceleration(moon) * dt
    moon.pos = moon.pos + moon.velocity * dt
    moonLabel.pos = moon.pos
    
    updateVectorArrows()
    
    if showDirVectors:
        moonDirArrow.visible = True
        saturnDirArrow.visible = True
    else:
        moonDirArrow.visible = False
        saturnDirArrow.visible = False
    