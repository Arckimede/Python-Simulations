import numpy as np
import pygame
from pygame_widgets import update
import pygame_widgets
import random

# other scripts
import sun, popup, buttons, stars
from planet import Planet
from utils import Utils

WIDTH, HEIGHT = 1280, 720
GRAVITATIONAL_CONSTANT = 2.0 # 0.5 to 2 is good
SOFTENING_PARAMETER = 1.0 # prevents extreme accelerations at close approach

# planets
sunInstance = sun.Sun(WIDTH / 2, HEIGHT / 2, 10000, (255, 255, 0), 30)
earth = Planet(790, 360, 10, pygame.Vector2(0, 0), (0, 102, 255), 6)
jupiter = Planet(940, 360, 300, pygame.Vector2(0, 0), (255, 165, 0), 14)
saturn = Planet(1090, 360, 200, pygame.Vector2(0, 0), (210, 180, 140), 12)
widgetButton = buttons.Buttons()
particleStars = stars.Star()
planets = [earth, jupiter, saturn]


class Simulation:
    def __init__(self) -> None:
        self.minDistanceToShowPopup = 10
        self.totalKineticEnergy = None
        self.totalPotentialEnergy = None
        self.totalEnergy = None
        self.tileSize = 60
        self.gridColor = "#2E2F4F"
        self.maxPlanets = 4
        self.currentPlanets = 3
        
    def createGrid(self, screen) -> None:
        
        # vertical lines
        for x in range(self.tileSize, WIDTH, self.tileSize):
            pygame.draw.line(screen, self.gridColor, (x, 0), (x, HEIGHT))
        
        # horizontal lines
        for y in range(self.tileSize, HEIGHT, self.tileSize):
            pygame.draw.line(screen, self.gridColor, (0, y), (WIDTH, y))
    
    @staticmethod
    def isMouseOnPlanet(scale: float = 2.0, minSize: int = 25) -> bool:
        mousePosX, mousePosY = Utils.getMousePos()
        
        for planet in planets:
            # mouse rect size grows with planet size but never smaller than minSize
            size = max(minSize, int(planet.radius * scale))
            mouseRect = Utils.createMouseRect(mousePosX, mousePosY, size=size)
            planetRect = Utils.createRect(planet.x, planet.y, planet.radius)
            if pygame.Rect.colliderect(mouseRect, planetRect):
                return True
        return False        
    
    def spawnNewPlanet(self, planetList: list) -> None:
        # to spawn new planets
        randMass = random.randint(50, 200)
        newPlanetColor = "#88F2F2"
        randRadius = random.randint(5, 15)
        mousePosX, mousePosY = pygame.mouse.get_pos()
        
        # check that you can still create planets,  cursor is not on planets and on sun and on button
        if (self.currentPlanets < self.maxPlanets) and (not self.isMouseOnPlanet()) and (not sunInstance.isMouseOnSun()) and (not widgetButton.isMouseOnButton()):
            newPlanet = Planet(mousePosX, mousePosY, randMass, pygame.Vector2(0, 0), newPlanetColor, randRadius)
            newPlanet.setInitialVelocity(sunInstance.pos, sunInstance.mass, GRAVITATIONAL_CONSTANT)
            planetList.append(newPlanet)
            self.currentPlanets += 1
    
    def createPlanetPopup(self, font, screen):
        mousePosX, mousePosY = Utils.getMousePos()
        for planet in planets:
            distToMouse = Utils.calcDistance(pygame.Vector2(mousePosX, mousePosY), planet.pos)
            if distToMouse < self.minDistanceToShowPopup:
                popupText = popup.Popup(text=f"X: {np.round(planet.pos.x, 2)} - Y: {np.round(planet.pos.y, 2)}")
                popupText.createPopup(font, planet.color, screen, planet.pos, pygame.Vector2(-60, -60))

    def updatePlanetPositions(self, dt, screen) -> None:
        if sunInstance is not None and planets[0] is not None and planets[1] is not None and planets[2] is not None:
            sunInstance.drawSun(screen)
            for planet in planets:
                planet.drawPlanet(screen)
                planetPath = planet.calcFuturePlanetPos(sunInstance.pos, sunInstance.mass, GRAVITATIONAL_CONSTANT, SOFTENING_PARAMETER, dt, steps=14000)
                pygame.draw.lines(screen, planet.color, False, planetPath, 1)
                if not widgetButton.isPaused:
                    planet.updatePosRungeKutta(sunInstance.pos, sunInstance.mass, GRAVITATIONAL_CONSTANT, SOFTENING_PARAMETER, dt)        

    def calcTotalPlanetEnergies(self) -> list:
        # energy of motion (KE)
        totalKineticEnergy = sum([0.5 * planet.mass * planet.vel.length_squared() for planet in planets])
        # gravitational energy between bodies (PE)
        totalPotentialEnergy = sum([-(GRAVITATIONAL_CONSTANT * sunInstance.mass * planet.mass) / planet.pos.distance_to(sunInstance.pos) for planet in planets])
        # total energy (TE)
        totalEnergy = totalKineticEnergy + totalPotentialEnergy

        return [totalKineticEnergy, totalPotentialEnergy, totalEnergy]

    def displayEnergiesText(self, screen: pygame.Surface , font: pygame.font.SysFont) -> None:
        kineticEnergySurface = font.render(f"Total Kinetic Energy: {np.round(self.calcTotalPlanetEnergies()[0], 2)}", True, (255, 215, 0))
        potentialEnergySurface = font.render(f"Total Potential Energy: {np.round(self.calcTotalPlanetEnergies()[1], 2)}", True, (255, 215, 0))
        totalEnergySurface = font.render(f"Total Energy: {np.round(self.calcTotalPlanetEnergies()[2], 2)}", True, (255, 215, 0))
        screen.blit(kineticEnergySurface, (40, 30))
        screen.blit(potentialEnergySurface, (40, 70))
        screen.blit(totalEnergySurface, (40, 110))

    def updateSimulation(self) -> None:
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("N-body Simulation")
        clock = pygame.time.Clock()
        running = True
        dt = 0
        
        popupFont = pygame.font.SysFont("Anonymous", 18)
        textFont = pygame.font.SysFont("Anonymous", 20)
        widgetButton.createButtons(screen, textFont)
        
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.spawnNewPlanet(planets)
                    
            screen.fill("#0B0C2A")
            self.createGrid(screen)
            self.updatePlanetPositions(dt, screen)    
            self.displayEnergiesText(screen, textFont)
            self.createPlanetPopup(popupFont, screen)
            particleStars.createStars(dt, screen, WIDTH, HEIGHT)
            pygame_widgets.update(events)            
            update([widgetButton])
            pygame.display.flip()
            dt = clock.tick(60) / 1000
        pygame.quit()


if __name__ == "__main__":
    simulation = Simulation()
    for planet in planets:
        planet.setInitialVelocity(sunInstance.pos, sunInstance.mass, GRAVITATIONAL_CONSTANT)
    
    simulation.updateSimulation()
