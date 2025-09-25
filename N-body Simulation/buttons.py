import pygame
from pygame_widgets.button import Button

class Buttons:
    def __init__(self):
        self.pauseAnimationButton = None
        self.isPaused = False
    
    def onButtonClicked(self, button: Button):
        self.isPaused = not self.isPaused
        button.setText("RESTART" if self.isPaused else "PAUSE")
        
    def createButtons(self, screen: pygame.Surface, font):
        self.pauseAnimationButton = Button(screen, 50, 650, width=100, height=30, font=font, textColour=(255, 255, 255), text="PAUSE", fontSize=20, inactiveColour=(11, 12, 42), 
                                           hoverColour=(100, 149, 237), radius=2, borderColour=(100, 149, 237), borderThickness=2, onClick=lambda: self.onButtonClicked(self.pauseAnimationButton))

    def isMouseOnButton(self) -> bool:
        buttonX, buttonY = self.pauseAnimationButton.getX(), self.pauseAnimationButton.getY()
        buttonWidth, buttonHeight = self.pauseAnimationButton.getWidth(), self.pauseAnimationButton.getHeight()
        buttonRect = pygame.Rect(buttonX, buttonY, buttonWidth, buttonHeight)
        mousePosX, mousePosY = pygame.mouse.get_pos()
        mouseWidth, mouseHeight = 23, 23
        mouseRect = pygame.rect.Rect(int(mousePosX), int(mousePosY), mouseWidth, mouseHeight)

        return pygame.Rect.colliderect(mouseRect, buttonRect)
        