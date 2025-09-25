import pygame

class Utils:
    @staticmethod
    def createRect(x: int, y: int, radius: int) -> pygame.Rect:
        return pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
    
    @staticmethod
    def getMousePos() -> tuple:
        mouseX, mouseY = pygame.mouse.get_pos()
        return (int(mouseX), int(mouseY))
    
    @staticmethod
    def createMouseRect(mouseX: int, mouseY: int, size: int = 30):
        mouseRect = pygame.rect.Rect(int(mouseX), int(mouseY), size, size)
        return mouseRect
    
    @staticmethod
    def calcDistance(posOne: pygame.Vector2, posTwo: pygame.Vector2):
        return posOne.distance_to(posTwo)