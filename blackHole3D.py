from vpython import *
import numpy as np
import random
import pygame 

pygame.mixer.init()
flashSound = pygame.mixer.Sound("Sound/flash sound.mp3")

canvas(width=1200, height=800)

# constants
G = 10
dt = 0.01

# general variables
eventHorizon = 1
particles = []
speedReduction = 0.5

# colors
ringColor = vector(1, 0.5, 0)
blackHoleColor = vector(0.1, 0.0, 0.2)
particlesColor = [color.red, color.cyan, color.yellow, color.purple]
plasmaJetColor = vector(1, 0.5, 0)

blackHole = sphere(pos=vector(0, 0, 0), radius=eventHorizon, color=blackHoleColor)
blackHole.mass = 1000
disk = ring(pos=blackHole.pos, radius=1.1, thickness=0.2, color=ringColor, opacity=0.5)

def createStars(numStars):   
    
    while numStars >= 0:
        
        x = random.randint(-30, 30)
        y = random.randint(-30, 30)
        z = random.randint(-30, 30)
        point = sphere(pos=vector(x, y, z), radius=0.2, color=color.white, emissive=True, 
                    shininess=0.5)
        numStars -= 1


def createParticles(numParticles=20):
    global G, particlesColor, dt, particles, speedReduction

    #for _ in range(0, numParticles):
    while numParticles >= 0:
        # initial position
        particleDistanceFromBlackHole = random.randint(a=3, b=8)
        
        randColor = random.choice(particlesColor)
        angle = random.randrange(0, 628) / 100
        x = particleDistanceFromBlackHole * np.cos(angle)
        y = particleDistanceFromBlackHole * np.sin(angle)
        z = random.uniform(-10, 10)

        pos = vector(x, y, z)
        rVec = pos
        axis = vector(0, 0, 1)
        
        speed = np.sqrt(G * blackHole.mass / particleDistanceFromBlackHole)
        tangentialVeL = cross(axis, rVec).norm() * (speedReduction * speed)
        
        particle = sphere(pos=pos, radius=0.1, color=randColor, make_trail=True, retain=18)
        particle.velocity = tangentialVeL
        particles.append(particle)
        
        numParticles -= 1
        
def handleParticles():
    global particles, G, dt
    
    for particle in particles:
        rVec = particle.pos - blackHole.pos
        rMag = mag(rVec)
        gravAcc = - (G * blackHole.mass / rMag**3) * rVec
        
        particle.velocity += gravAcc * dt
        particle.pos = particle.pos + particle.velocity * dt    

def destroyParticles():
    global particles, eventHorizon, blackHoleSizeIncrement, diskSizeIncrement, eventHorizon
        
    for particle in particles:
        vecToBlackHole = blackHole.pos - particle.pos
        vecMag = mag(vecToBlackHole)
        
        if vecMag <= eventHorizon:
            particle.visible = False
            flashSound.play()
            particles.remove(particle)
            particle.make_trail = False
            del particle
    

createParticles(20)
createStars(50)

while True:
    rate(60)
    disk.rotate(axis=vec(0, 1, 0), angle=0.01)
    handleParticles()
    destroyParticles()
    
    
