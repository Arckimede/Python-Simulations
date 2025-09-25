import pygame

class Popup():
    def __init__(self, text):
        self.popupWidth = 130
        self.popupHeight = 40
        self.surface = pygame.Surface((self.popupWidth, self.popupHeight))
        self.text = text
    
    def createPopup(self, font: pygame.font.SysFont, planetColor: tuple, screen: pygame.Surface, planetPos: pygame.Vector2, planetYOffset: pygame.Vector2) -> None:
        pygame.draw.rect(self.surface, planetColor, self.surface.get_rect(), 2)
        textSurface = font.render(self.text, True, planetColor)
        textSurfaceRect = textSurface.get_rect(center=(self.popupWidth // 2, self.popupHeight // 2))
        self.surface.blit(textSurface, textSurfaceRect)
        screen.blit(self.surface, (planetPos.x + planetYOffset.x, planetPos.y + planetYOffset.y))
        
