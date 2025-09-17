import pygame
import numpy as np
import random
import math
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from pygame_widgets import update

class Agent():
    def __init__(self, state, color):
        self.state = state # healthy, infected, immune or dead
        self.color = color
        self.hasBeenInfected = True if self.state == "infected" else False
        self.infectionTime = 0
        self.radius = 15
        
        # random x and y    
        WIDTH, HEIGHT = 1280, 720
        self.x = random.randint(0, WIDTH - self.radius)
        self.y = random.randint(0, HEIGHT - self.radius)
        
    def move(self):
        randX = random.randint(-6, 6) 
        randY = random.randint(-6, 6)
        self.x += randX
        self.y += randY
        
        # not going outside screen
        WIDTH, HEIGHT = 1280, 720
        if (self.x < self.radius): self.x = self.radius
        if (self.y < self.radius): self.y = self.radius
        if (self.x > WIDTH): self.x = WIDTH - self.radius
        if (self.y > HEIGHT): self.y = HEIGHT - self.radius 
        
class Simulation():
    def __init__(self):
        self.healthyAgents = 50
        self.infectedAgents = 3
        self.immuneAgents = 3
        self.deadAgents = 0
        self.healthyAgentsList = []
        self.infectedAgentsList = []
        self.immuneAgentsList = []
        self.deathMarkers = []
        self.inRangeMarkers = []
        self.colors = ["#F54927", "#93F06C", "#FFFFFF", "#808080"]
        self.textFont = None
        self.healthyAgentsText = None
        self.deadAgentsText = None
        self.immuneAgentsText = None
        self.infectedAgentsText = None
        self.timePassedText = None
        self.infectionProbability = 0.5
        self.immuneProbability = 0.3 # 30% prob. to become immune
        self.deathProbability = 0.2
        self.stayInfectedProbability = 0.3
        self.minRecoveryTime = 20 
        self.timer = 0
        
    def spawnAgents(self, agentsCount, agentsList: list, state: str, color: str):
        for _ in range(0, agentsCount):
            agent = Agent(state=state, color=color)
            agentsList.append(agent)
    
    def updateState(self, dt, screen):
        for agent in self.infectedAgentsList:
            agent.infectionTime += dt
            if agent.infectionTime >= self.minRecoveryTime:
                p = self.getRandomProbability()
                
                if p < self.immuneProbability:
                    # become immune
                    agent.hasBeenInfected = False
                    agent.state = "immune"
                    agent.color = self.colors[2]
                    self.infectedAgentsList.remove(agent)
                    self.immuneAgentsList.append(agent)
                    self.infectedAgents -= 1
                    self.immuneAgents += 1
                elif p < self.immuneProbability + self.deathProbability:
                    # become dead
                    agent.hasBeenInfected = False
                    agent.state = "dead"
                    agent.color = self.colors[3]
                    self.deadAgents += 1
                    self.deathMarkers.append((agent.x, agent.y))
                    self.infectedAgentsList.remove(agent)
                    self.infectedAgents -= 1
                elif p < self.immuneProbability + self.deathProbability + self.stayInfectedProbability:
                    agent.infectionTime = 0
                else:
                    # return to healthy
                    agent.hasBeenInfected = False
                    agent.state = "healthy"
                    agent.color = self.colors[1]
                    self.infectedAgentsList.remove(agent)
                    self.healthyAgentsList.append(agent)
                    self.infectedAgents -= 1
                    self.healthyAgents += 1

                agent.infectionTime = 0
                
    def moveAgents(self, agents):
        for agent in agents:
            agent.move()
    
    def createInRangeRadius(self, x, y):
        timer = 0
        rangeRadiusDict = {"x": x, "y": y, "radius": 3, "life": 2}
        self.inRangeMarkers.append(rangeRadiusDict)
            
    def createTexts(self, screen, text, font, textColor, x, y):
        img = font.render(text, True, textColor)
        screen.blit(img, (x, y))
    
    def getRandomProbability(self):
        return np.random.rand()
        
    def checkCollisions(self):
        newlyInfected = []
        for infected in self.infectedAgentsList:
            infectedPos = pygame.Vector2(infected.x, infected.y)
            
            for healthy in self.healthyAgentsList:
                healthyPos = pygame.Vector2(healthy.x, healthy.y)

                if (infectedPos.distance_to(healthyPos) <= infected.radius + healthy.radius) and (self.getRandomProbability() < self.infectionProbability):
                    healthy.color = self.colors[0]
                    self.createInRangeRadius(infectedPos.x, infectedPos.y)
                    newlyInfected.append(healthy)
        
        for agent in newlyInfected:
            if agent in self.healthyAgentsList:
                self.healthyAgentsList.remove(agent)
                self.healthyAgents -= 1
            if agent not in self.infectedAgentsList:
                self.infectedAgentsList.append(agent)
                self.infectedAgents += 1
                agent.state = "infected"
        
    def update(self):
        pygame.init()
        pygame.font.init()
        screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Virus Simulation")
        clock = pygame.time.Clock()
        running = True
        dt = 0
        
        self.textFont = pygame.font.SysFont("Anonymous", 30)
        infectionProbSlider = Slider(screen, 950, 620, 300, 20, min=0, max=1, step=0.1, start=self.infectionProbability, 
                                     colour=(85, 85, 85), inactiveColour=(51, 51, 51), handleColour=(245, 73, 39), handleBorderColour=(255, 255, 255))
        sliderTextBox = TextBox(screen, 1000, 650, 200, 40, fontSize=18, textColour=(255, 255, 255), borderThickness=0, colour=(0, 0, 0))
        sliderTextBox.disable()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
            screen.fill("black")
            self.timer += dt
            
            # create agents
            for healthyAgent in self.healthyAgentsList:
                pygame.draw.circle(screen, healthyAgent.color, (healthyAgent.x, healthyAgent.y), healthyAgent.radius)
            
            # draw agents            
            for immune in self.immuneAgentsList:
                pygame.draw.circle(screen, immune.color, (immune.x, immune.y), immune.radius)

            for infected in self.infectedAgentsList:
                pygame.draw.circle(screen, infected.color, (infected.x, infected.y), infected.radius)

            for (x, y) in self.deathMarkers:
                deathMarker = pygame.image.load("C:/Users/chris/Desktop/Informatica/Simulations/Images/red cross.png").convert_alpha()
                deathMarker = pygame.transform.scale(deathMarker, (30, 30))
                screen.blit(deathMarker, (x, y))
                #pygame.draw.circle(screen, "#E027F5", (x, y), 20, width=2)
            
            # move agents
            self.moveAgents(self.healthyAgentsList)
            self.moveAgents(self.immuneAgentsList)
            self.moveAgents(self.infectedAgentsList)
            
            # texts to display
            self.healthyAgentsText = self.createTexts(screen, f"Healthy agents: {self.healthyAgents}", self.textFont, "#FFFFFF", x=50, y=20)
            self.immuneAgentsText = self.createTexts(screen, f"Immune agents: {self.immuneAgents}", self.textFont, "#FFFFFF", x=50, y=50)
            self.infectedAgentsText = self.createTexts(screen, f"Infected agents: {self.infectedAgents}", self.textFont, "#FFFFFF", x=50, y=80)
            self.deadAgentsText = self.createTexts(screen, f"Dead agents: {self.deadAgents}", self.textFont, "#FFFFFF", x=50, y=110)
            self.timePassedText = self.createTexts(screen, f"Time Passed: {self.timer:.02f}", self.textFont, "#FFFFFF", x=1000, y=20)
            
            # collisions and draw in-range markers
            self.checkCollisions()
            
            for marker in self.inRangeMarkers:
                marker["radius"] += 30 * dt
                marker["life"] -= dt
                pygame.draw.circle(screen, "#F59887", (marker["x"], marker["y"]), int(marker["radius"]), width=2)
                if marker["life"] <= 0:
                    self.inRangeMarkers.remove(marker)
            
            self.updateState(dt, screen)
            
            update([infectionProbSlider, sliderTextBox])
            sliderTextBox.setText(f"Infection Prob: {infectionProbSlider.getValue():.2f}")
            self.infectionProbability = infectionProbSlider.getValue()
            pygame.display.update()
            pygame.display.flip()
            dt = clock.tick(60) / 1000

        
        pygame.quit()
        

if __name__ == "__main__":
    simulation = Simulation()
    simulation.spawnAgents(simulation.healthyAgents, simulation.healthyAgentsList, "healthy", simulation.colors[1])
    simulation.spawnAgents(simulation.immuneAgents, simulation.immuneAgentsList, "immune", simulation.colors[2])
    simulation.spawnAgents(simulation.infectedAgents, simulation.infectedAgentsList, "infected", simulation.colors[0])
    simulation.update()