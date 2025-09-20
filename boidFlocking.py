import numpy as np
import pygame
import random
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
import pygame_widgets
from pygame_widgets import update
from pygame_widgets.button import Button

GAME_WIDTH, GAME_HEIGHT = 1280, 720

class Boid:
    def __init__(self) -> None:
        self.pos = pygame.Vector2(random.randint(0, GAME_WIDTH), random.randint(0, GAME_HEIGHT))
        self.vel =  pygame.Vector2(random.uniform(-100, 100), random.uniform(-100, 100))
        self.normalColor = pygame.Color("#558cf4")
        self.color = self.normalColor
        self.maxSpeed = 200
        self.vertexOffset = 4
        self.minDistanceToNeighbor = 50
        self.separationWeight = 0.5
        self.alignmentWeight = 0.5
        self.cohesionWeight = 0.5
        self.hasBounced = False
        self.colorTimer = 0
        self.bouncedColor = pygame.Color("#F23B1B")
        self.transitionDuration = 1.0
        self.inBounceTransition = False

    def changeColourOnBoundariesHit(self, dt):
        if self.inBounceTransition:
            self.colorTimer += dt
            t = min(self.colorTimer / self.transitionDuration, 1.0)
            
            # normal to bounced
            if t < 0.5:
                lerpT = t / 0.5
                self.color = pygame.Color.lerp(self.normalColor, self.bouncedColor, lerpT)
            # bounced to normal
            else:
                lerpT = (t - 0.5) / 0.5
                self.color = pygame.Color.lerp(self.bouncedColor, self.normalColor, lerpT)
            
            # reset when finished
            if t >= 1.0:
                self.inBounceTransition = False
                self.color = self.normalColor
    
    def getNeighbors(self, boids: list) -> list:
        neighbors = []
        
        for other in boids:
            if (other != self) and (pygame.Vector2.distance_to(self.pos, other.pos) <= self.minDistanceToNeighbor):
                neighbors.append(other)
        
        return neighbors
    
    def separation(self, boids: list) -> pygame.Vector2:
        sepVec = pygame.Vector2(0, 0)
        neighbors = self.getNeighbors(boids)
        for neighbor in neighbors:
            sepVec = sepVec + (self.pos - neighbor.pos)
        
        if neighbors and sepVec.length() > 0:
            return sepVec.normalize() * self.separationWeight
        return pygame.Vector2(0, 0)
        
    def alignment(self, boids) -> pygame.Vector2:
        neighbors = self.getNeighbors(boids)

        if not neighbors:
            return pygame.Vector2(0, 0)
        
        avgVelNearbyNeighbors = sum((neighbor.vel for neighbor in neighbors), pygame.Vector2(0, 0)) / len(neighbors)
        steeringVec = (avgVelNearbyNeighbors - self.vel) 
        
        return steeringVec.normalize() * self.alignmentWeight
    
    def cohesion(self, boids) -> pygame.Vector2:
        neighbors = self.getNeighbors(boids)
        
        if not neighbors:
            return pygame.Vector2(0, 0)
        
        avgPosNeighbors = sum((neighbor.pos for neighbor in neighbors), pygame.Vector2(0, 0)) / len(neighbors)
        vecToAvgCenter = avgPosNeighbors - self.pos
        return vecToAvgCenter.normalize() * self.cohesionWeight
    
    def updateBoidPos(self, dt, boids) -> None:
        self.vel += self.separation(boids) + self.alignment(boids) + self.cohesion(boids)
        
        if(self.vel.length() > self.maxSpeed):
            self.vel.scale_to_length(self.maxSpeed)
        
        self.pos = self.pos + self.vel * dt
    
    def handleBoundaries(self) -> None:
        bounced = False
        if(self.pos.x < 0):
            self.pos.x = 0
            self.vel.x *= -1
            bounced = True
        if(self.pos.x > GAME_WIDTH):
            self.pos.x = GAME_WIDTH
            self.vel.x *= -1
            bounced = True
        if(self.pos.y < 0):
            self.pos.y = 0
            self.vel.y *= -1
            bounced = True
        if(self.pos.y > GAME_HEIGHT):
            self.pos.y = GAME_HEIGHT
            self.vel.y *= -1
            bounced = True
        
        if bounced:
            self.colorTimer = 0.0
            self.inBounceTransition = True
    
    def draw(self, screen):
        baseTriangle = [
            pygame.Vector2(0, -2.5),
            pygame.Vector2(-1.5, 1.5),
            pygame.Vector2(1.5, 1.5)
        ]
    
        if self.vel.length() > 0: # avoid division by 0
            angle = self.vel.angle_to(pygame.Vector2(0, -1))
        else:
            angle = 0
        
        # rotate and translate to boid position
        scaledBaseTriangle = [vec * self.vertexOffset for vec in baseTriangle]
        rotated = [p.rotate(-angle) for p in scaledBaseTriangle]
        moved = [self.pos + p for p in rotated]
        
        # draw
        pygame.draw.polygon(screen, self.color, moved)
    
class Simulation:
    def __init__(self) -> None:
        self.numBoids = 50
        self.boids = []
        self.separationSlider = None
        self.alignmentSlider = None
        self.cohesionSlider = None
        self.sizeSlider = None
        self.separationOutput = None
        self.alignmentOutput = None
        self.cohesionOutput = None
        self.sizeOutput = None
        self.resetButton = None
    
    def createBoids(self) -> None:
        for _ in range(0, self.numBoids):
            boid = Boid()
            self.boids.append(boid)
    
    def resetWeights(self):
        originalWeightValue = 0.5
        originalVertexOffsetValue = 4
        
        if len(self.boids) == 0 or self.boids is None:
            return
        
        for boid in self.boids:
            boid.separationWeight = originalWeightValue
            boid.alignmentWeight = originalWeightValue
            boid.cohesionWeight = originalWeightValue
            boid.vertexOffset = originalVertexOffsetValue

        self.separationSlider.setValue(boid.separationWeight)
        self.alignmentSlider.setValue(boid.alignmentWeight)
        self.cohesionSlider.setValue(boid.cohesionWeight)
        self.sizeSlider.setValue(float(boid.vertexOffset))
        self.separationOutput.setText(f"Separation: {self.separationSlider.getValue():.2f}")
        self.alignmentOutput.setText(f"Alignment: {self.alignmentSlider.getValue():.2f}")
        self.cohesionOutput.setText(f"Cohesion: {self.cohesionSlider.getValue():.2f}")
        self.sizeOutput.setText(f"Boid Size: {float(self.sizeSlider.getValue())}")
    
    def createButtonBorder(self, screen, button: Button) -> None:
        borderWidth = 5
        
        pygame.draw.rect(screen, color=(242, 59, 27), rect=[button.getX() - borderWidth // 2, button.getY() - borderWidth // 2, 
                    button.getWidth() + borderWidth, button.getHeight() + borderWidth], width=borderWidth, border_radius=3)
        
    
    def createWidgets(self, screen) -> None:
        self.sizeSlider = Slider(screen, 100, 680, 200, 20, min=1.0, max=10, step=0.5, 
                                    colour=(85, 140, 244), inactiveColour=(85, 140, 244), handleColour=(252,237,187), handleBorderColour=(255, 255, 255), 
                                    handleRadius=14, curved=True)
        self.separationSlider = Slider(screen, 350, 680, 200, 20, min=0, max=2, step=0.1, start=0.5, 
                                    colour=(85, 140, 244), inactiveColour=(85, 140, 244), handleColour=(252,237,187), handleBorderColour=(255, 255, 255), 
                                    handleRadius=14, curved=True)
        self.alignmentSlider = Slider(screen, 600, 680, 200, 20, min=0, max=2, step=0.1, start=0.5, 
                                    colour=(85, 140, 244), inactiveColour=(85, 140, 244), handleColour=(252,237,187), handleBorderColour=(255, 255, 255), 
                                    handleRadius=14, curved=True)
        self.cohesionSlider = Slider(screen, 850, 680, 200, 20, min=0, max=2, step=0.1, start=0.5, 
                                    colour=(85, 140, 244), inactiveColour=(85, 140, 244), handleColour=(252,237,187), handleBorderColour=(255, 255, 255), 
                                    handleRadius=14, curved=True)
        self.separationOutput = TextBox(screen, 400, 650, 110, 20, fontSize=15, textColour=(255, 255, 255), borderThickness=0, colour=(85, 140, 244))
        self.alignmentOutput = TextBox(screen, 650, 650, 110, 20, fontSize=15, textColour=(255, 255, 255), borderThickness=0, colour=(85, 140, 244))
        self.cohesionOutput = TextBox(screen, 900, 650, 110, 20, fontSize=15, textColour=(255, 255, 255), borderThickness=0, colour=(85, 140, 244))
        self.sizeOutput = TextBox(screen, 160, 650, 110, 20, fontSize=15, textColour=(255, 255, 255), borderThickness=0, colour=(85, 140, 244))
        
        self.resetButton = Button(screen, x=1100, y=650, width=80, height=50, fontSize=20, inactiveColour=(40, 44, 52), pressedColor=(242, 59, 27), 
                                  hoverColour=(242, 59, 27), textColour=(255, 255, 255), text="RESET", onClick=self.resetWeights)
        
        self.separationOutput.disable()
        self.alignmentOutput.disable()
        self.cohesionOutput.disable()
        self.sizeOutput.disable()
    
    def setSlidersValue(self) -> None:
        if self.separationSlider is not None and self.alignmentSlider is not None and self.cohesionSlider is not None:
            self.separationSlider.setValue(0.5)
            self.alignmentSlider.setValue(0.5)
            self.cohesionSlider.setValue(0.5)
            self.sizeSlider.setValue(4.0)        

    
    def setLabelsValue(self) -> None:
        if self.separationOutput is not None and self.alignmentOutput is not None and self.cohesionOutput is not None:
            self.separationOutput.setText(f"Separation: {self.separationSlider.getValue():.2f}")
            self.alignmentOutput.setText(f"Alignment: {self.alignmentSlider.getValue():.2f}")
            self.cohesionOutput.setText(f"Cohesion: {self.cohesionSlider.getValue():.2f}")
            self.sizeOutput.setText(f"Boid Size: {float(self.sizeSlider.getValue())}")
    
    def update(self) -> None:
        pygame.init()
        screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
        pygame.display.set_caption("Boids Flocking Simulation")
        clock = pygame.time.Clock()
        isRunning = True
        dt = 0
        
        # creating widgets
        self.createWidgets(screen)
        # force sliders to start at value given
        self.setSlidersValue()
        self.createButtonBorder(screen, self.resetButton)
        
        while(isRunning):
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    isRunning = False
            
            screen.fill("#282c34")
            
            for boid in self.boids:
                boid.separationWeight = self.separationSlider.getValue()  
                boid.alignmentWeight = self.alignmentSlider.getValue()
                boid.cohesionWeight = self.cohesionSlider.getValue()
                boid.vertexOffset = self.sizeSlider.getValue()

                boid.handleBoundaries()
                boid.changeColourOnBoundariesHit(dt)
                boid.updateBoidPos(dt, self.boids)
                boid.draw(screen)
            
            # labels and button border
            self.setLabelsValue()
            self.createButtonBorder(screen, self.resetButton)

            pygame_widgets.update(events)
            update([self.separationSlider, self.alignmentSlider, self.cohesionSlider, self.sizeSlider, self.separationOutput, 
                    self.alignmentOutput, self.cohesionOutput, self.sizeOutput, self.resetButton])
            pygame.display.update()
            pygame.display.flip()
            
            dt = clock.tick(60) / 1000

        pygame.quit()

if __name__ == "__main__":
    simulation = Simulation()
    simulation.createBoids()
    simulation.update()