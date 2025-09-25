import pygame
from utils import Utils

class Sun:
    def __init__(self, x: int, y: int, mass: int, color: tuple, radius: int):
        self.x = x
        self.y = y
        self.mass = mass
        self.pos = pygame.Vector2(self.x, self.y)
        self.color = color
        self.radius = radius
        
    def drawSun(self, screen):
        pygame.draw.circle(screen, self.color, self.pos, self.radius)
    
    def isMouseOnSun(self):
        sunRect = Utils.createRect(self.x, self.y, self.radius)
        mousePosX, mousePosY = Utils.getMousePos()
        mouseRect = Utils.createMouseRect(mousePosX, mousePosY, 25)
        
        return pygame.Rect.colliderect(mouseRect, sunRect)
    
    