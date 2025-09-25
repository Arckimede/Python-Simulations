import numpy as np
import pygame
from utils import Utils

class Planet:
    def __init__(self, x: int, y: int, mass: int, vel: pygame.Vector2, color: tuple, radius: int) -> None:
        self.x = x
        self.y = y
        self.mass = mass
        self.vel = vel
        self.color = color
        self.pos = pygame.Vector2(float(self.x), float(self.y))
        self.radius = radius
        self.path = None
    
    def drawPlanet(self, screen):
        pygame.draw.circle(screen, self.color, self.pos, self.radius)
    
    def setInitialVelocity(self, sunPos: pygame.Vector2, sunMass: int, gravitConstant: int):
        vecSunToPlanet = self.pos - sunPos
        dist = Utils.calcDistance(self.pos, sunPos)
        tangentialSpeed = np.sqrt(gravitConstant * sunMass / dist)      
        # to rotate clockwise
        perpVecToR = pygame.Vector2(vecSunToPlanet.y, -vecSunToPlanet.x).normalize()
        finalVel = tangentialSpeed * perpVecToR
        
        self.vel = self.vel + finalVel
    
    def calcFuturePlanetPos(self, sunPos: pygame.Vector2, sunMass: int, gravitConstant: int, softeningParameter: int, dt, steps=500):
        tempPos = pygame.Vector2(self.pos)
        tempVel = pygame.Vector2(self.vel)
        path = []
        
        for _ in range(steps):
            vecSunToPlanet = tempPos - sunPos
            dist = Utils.calcDistance(sunPos, tempPos)
            acc = - (gravitConstant * sunMass) * (vecSunToPlanet / ((dist**2 + softeningParameter**2)**1.5))

            tempVel += acc * dt
            tempPos += tempVel * dt
            
            path.append((int(tempPos.x), int(tempPos.y)))
        
        return path
    
    def calcAcceleration(self, pos: pygame.Vector2, sunPos: pygame.Vector2, sunMass: int, gravitConstant: int, softeningParameter: int):
        vecSunToPlanet = pos - sunPos
        dist = Utils.calcDistance(sunPos, pos)
        softenedGravAccTowardSun = - (gravitConstant * sunMass) * (vecSunToPlanet / ((dist**2 + softeningParameter**2)**1.5))

        return softenedGravAccTowardSun
    
    def updatePosRungeKutta(self, sunPos: pygame.Vector2, sunMass: int, gravitConstant: int, softeningParameter: int, dt):
        k1Pos = self.vel
        k1Vel = self.calcAcceleration(self.pos, sunPos, sunMass, gravitConstant, softeningParameter)
        
        k2Pos = self.vel + 0.5 * k1Vel * dt
        k2Vel = self.calcAcceleration(self.pos + 0.5 * k1Pos * dt, sunPos, sunMass, gravitConstant, softeningParameter)
        
        k3Pos = self.vel + 0.5 * k2Vel * dt
        k3Vel = self.calcAcceleration(self.pos + 0.5 * k2Pos * dt, sunPos, sunMass, gravitConstant, softeningParameter)
        
        k4Pos = self.vel + k3Vel * dt
        k4Vel = self.calcAcceleration(self.pos + k3Pos * dt, sunPos, sunMass, gravitConstant, softeningParameter)

        # weighted average
        self.pos += (dt / 6) * (k1Pos + 2*k2Pos + 2*k3Pos + k4Pos)     
        self.vel += (dt / 6) * (k1Vel + 2*k2Vel + 2*k3Vel + k4Vel)