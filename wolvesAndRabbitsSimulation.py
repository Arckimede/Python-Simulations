import numpy as np
import pygame
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random

class Wolf:
    def __init__(self, energy = 120, energyLossPerMove: int = 1, energyGain = 60, reproductionThreshold: int = 170, radius: int = 10, maxEnergy: int = 200) -> None:
        self.maxEnergy = maxEnergy
        self.energy = energy
        self.energy = pygame.math.clamp(self.energy, 0, self.maxEnergy)
        self.energyLossPerMove = energyLossPerMove
        self.energyGain = energyGain
        self.reproductionThreshold = reproductionThreshold
        self.radius = radius
        self.state = "rest"
        self.timer = random.randint(40, 100)
        self.dx = 0
        self.dy = 0
        self.isDead = False
        
        WIDTH, HEIGHT = 1280, 720
        self.x = random.randint(0, WIDTH - 20)
        self.y = random.randint(0, HEIGHT - 20)
    
    def move(self):
        WIDTH, HEIGHT = 1280, 720

        if(self.state == "move"):
            self.x = max(0, min(WIDTH, self.x + self.dx))
            self.y = max(0, min(HEIGHT, self.y + self.dy))

        self.timer -= 1
        if (self.timer <= 0):
            if self.state == "move":
                self.decreaseEnergy(self.energyLossPerMove)
                self.state = "rest"
                self.timer = random.randint(40, 100)
            else:
                self.state = "move"
                self.timer = random.randint(20, 60)
                self.dx = random.randint(-3, 3)
                self.dy = random.randint(-3, 3)
                
        if (self.x < self.radius): self.x = self.radius 
        if (self.x > WIDTH): self.x = WIDTH - self.radius
        if (self.y < self.radius): self.y = self.radius
        if (self.y > HEIGHT): self.y = HEIGHT - self.radius
    
    def decreaseEnergy(self, amount):
        if not self.energy: return
        if self.energy > 0:
            self.energy -= amount
    
    def increaseEnergyOnRabbitEaten(self):
        if not self.energy: return
        if self.energy != self.maxEnergy:
            self.energy = min(self.maxEnergy, self.energy + self.energyGain)
            
    def getMinDistanceToRabbit(self, rabbits: list):
        if not rabbits:
            return None, None
        
        grassPosVec = pygame.Vector2(self.x, self.y)
        closestRabbit = min(rabbits, key=lambda r: grassPosVec.distance_to((r.x, r.y)))
        minDist = grassPosVec.distance_to((closestRabbit.x, closestRabbit.y))        
        
        return minDist, closestRabbit
    
    def die(self, wolves: list):
        if self.energy is not None and self.energy <= 0:
            self.isDead = True
            wolves.remove(self)
    
    def createNewWolf(self, wolves: list, xOffset: int, yOffset: int):
        newWolf = Wolf(energy=70)
        newWolf.x += xOffset
        newWolf.y += yOffset
        wolves.append(newWolf)
        return newWolf
    
    def reproduce(self, wolves: list, energyLossOnReproduction: int):
        xVecOffset = random.randint(-5, 5)
        yVecOffset = random.randint(-5, 5)
        
        if self.energy >= self.reproductionThreshold:
            self.energy -= energyLossOnReproduction
            self.createNewWolf(wolves, xVecOffset, yVecOffset)
            return True
        return False
    
class Rabbit:
    def __init__(self, energy = 70, energyLossPerMove: int = 0.3, energyGain: int = 25, reproductionThreshold: int = 90, radius: int = 5, maxEnergy: int = 100) -> None:
        self.maxEnergy = maxEnergy
        self.energy = energy
        self.energy = pygame.math.clamp(self.energy, 0, self.maxEnergy)
        self.energyLossPerMove = energyLossPerMove
        self.energyGain = energyGain
        self.reproductionThreshold = reproductionThreshold
        self.radius = radius
        self.state = "rest"
        self.timer = random.randint(10, 50)
        self.dx = 0
        self.dy = 0
        self.isDead = False
        
        WIDTH, HEIGHT = 1280, 720
        self.x = random.randint(0, WIDTH - 20)
        self.y = random.randint(0, HEIGHT - 20)
        
    def move(self):
        WIDTH, HEIGHT = 1280, 720

        if self.state == "move":
            self.x = max(0, min(WIDTH, self.x + self.dx))
            self.y = max(0, min(HEIGHT, self.y + self.dy))
            
        self.timer -= 1
        if self.timer <= 0:
            if self.state == "move":
                self.state = "rest"
                self.timer = random.randint(10, 50) # rest duration
            else:
                self.state = "move"
                self.timer = random.randint(10, 30) # hop duration
                self.decreaseEnergy(self.energyLossPerMove)
                # choose new direction
                self.dx = random.randint(-2, 2)
                self.dy = random.randint(-2, 2)

        if (self.x < self.radius): self.x = self.radius 
        if (self.x > WIDTH): self.x = WIDTH - self.radius
        if (self.y < self.radius): self.y = self.radius
        if (self.y > HEIGHT): self.y = HEIGHT - self.radius

    def decreaseEnergy(self, amount):
        if not self.energy: return
        if self.energy > 0:
            self.energy -= amount
    
    def increaseEnergyOnGrass(self):
        if not self.energy: return
        if self.energy != self.maxEnergy:
            self.energy = min(self.maxEnergy, self.energy + self.energyGain)
    
    def die(self, rabbits: list):
        if self.energy is not None and self.energy <= 0:
            self.isDead = True
            rabbits.remove(self)
    
    def createNewRabbit(self, rabbits: list, xOffset: int, yOffset: int):
        newRabbit = Rabbit(energy=30)
        newRabbit.x += xOffset
        newRabbit.y += yOffset
        rabbits.append(newRabbit)
        return newRabbit
    
    def reproduce(self, rabbits: list, energyLossOnReproduction: int):
        xVecOffset = random.randint(-7, 7)
        yVecOffset = random.randint(-7, 7)
        
        if self.energy >= self.reproductionThreshold:
            self.energy -= energyLossOnReproduction
            self.createNewRabbit(rabbits, xVecOffset, yVecOffset)
            return True
        return False
    
class Grass:
    def __init__(self, time: int, minTimeToSpawn: int):
        self.time = time
        self.minTimeToSpawn = minTimeToSpawn
        self.x = random.randint(0, 1280)
        self.y = random.randint(0, 720)
        
    def getMinDistanceToRabbit(self, rabbits: list):
        if not rabbits:
            return None, None
        
        grassPosVec = pygame.Vector2(self.x, self.y)
        closestRabbit = min(rabbits, key=lambda r: grassPosVec.distance_to((r.x, r.y)))
        minDist = grassPosVec.distance_to((closestRabbit.x, closestRabbit.y))        
        
        return minDist, closestRabbit

class HealthBar:
    def __init__(self, x, y, w, h, maxHp, hp, vecOffset = pygame.Vector2(-15, -15)):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.maxHp = maxHp
        self.hp = hp
        self.vecOffset = vecOffset
        
    def draw(self, screen):
        ratio = self.hp / self.maxHp
        pygame.draw.rect(screen, "red", (self.x + self.vecOffset.x, self.y + self.vecOffset.y, self.w, self.h))
        pygame.draw.rect(screen, "#6e3dbd", (self.x + self.vecOffset.x, self.y + self.vecOffset.y, self.w * ratio, self.h))
    
class Simulation:
    def __init__(self, numRabbitsCount: int = 25, numWolvesCount: int = 3):
        self.numRabbitsList = []
        self.numWolvesList = []
        self.grass = []
        self.grassTimer = 0
        self.minTimeToSpawnGrass = 2
        self.numRabbitsCount = numRabbitsCount
        self.numWolvesCount = numWolvesCount
        self.textFont = None
        self.wolvesCountText = None
        self.rabbitsCountText = None
        self.avgRabbitEnergyText = None
        self.avgWolfEnergyText = None
        self.fpsText = None
        self.minDistanceForRabbitToEatGrass = 10
        self.minDistanceToEatRabbit = 15
        self.energyLossOnRabbitReproduction = 50
        self.energyLossOnWolfReproduction = 60
    
    def createRabbits(self):
        for _ in range(0, self.numRabbitsCount):
            rabbit = Rabbit()
            self.numRabbitsList.append(rabbit)
    
    def createWolves(self):
        for _ in range(0, self.numWolvesCount):
            wolf = Wolf()
            self.numWolvesList.append(wolf)
    
    def createGrass(self, dt):
        self.grassTimer += dt
        if (self.grassTimer >= self.minTimeToSpawnGrass):
            grass = Grass(self.grassTimer, self.minTimeToSpawnGrass)
            
            overlap = False
            for g in self.grass:
                if g.x == grass.x and g.y == grass.y:
                    overlap = True
                    break
            
            if not overlap:
                self.grass.append(grass)
            self.grassTimer = 0
    
    def createText(self, screen, text, font, textColor, x, y):
        img = font.render(text, True, textColor)
        screen.blit(img, (x, y))
    
    def getAvgAnimalEnergy(self, animals: list):
        return np.mean([animal.energy for animal in animals])     
     
    def update(self):
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        pygame.mouse.set_visible(False)
        screen = pygame.display.set_mode((1280, 720))   
        pygame.display.set_caption("Wolves and Rabbits")
        clock = pygame.time.Clock()
        running = True
        dt = 0
        
        textFont = pygame.font.SysFont("Anonymous", 30)
        wolfEatingSound = pygame.mixer.Sound("C:/Users/chris/Desktop/Informatica/Simulations/Sound/wolf eating rabbit.mp3")
        rabbitEatingSound = pygame.mixer.Sound("C:/Users/chris/Desktop/Informatica/Simulations/Sound/rabbit eating.wav")
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            screen.fill("#A6E34F")
                
            # updating animals
            for rabbit in self.numRabbitsList:
                pygame.draw.circle(screen, "#8b949b", (rabbit.x, rabbit.y), radius=rabbit.radius)
                rabbit.move()
                
                # health bar
                healthBar = HealthBar(rabbit.x, rabbit.y, 30, 6, rabbit.maxEnergy, rabbit.energy)
                healthBar.draw(screen)
                
                # reproduce
                if (rabbit.reproduce(self.numRabbitsList, self.energyLossOnRabbitReproduction)):
                    self.numRabbitsCount += 1
                
                # die
                rabbit.die(self.numRabbitsList)
                if rabbit.isDead:
                    self.numRabbitsCount -= 1
                
            for wolf in self.numWolvesList:
                pygame.draw.circle(screen, "#8b0000", (wolf.x, wolf.y), radius=12)
                wolf.move()
                
                # reproduce
                if (wolf.reproduce(self.numWolvesList, self.energyLossOnWolfReproduction)):
                    self.numWolvesCount += 1
                
                distToClosestRabbit, closestRabbit = wolf.getMinDistanceToRabbit(self.numRabbitsList)
                if distToClosestRabbit is not None and distToClosestRabbit <= self.minDistanceToEatRabbit:
                    wolf.increaseEnergyOnRabbitEaten()
                    self.numRabbitsList.remove(closestRabbit)
                    wolfEatingSound.play()
                    self.numRabbitsCount -= 1
                wolf.die(self.numWolvesList)
                if wolf.isDead:
                    self.numWolvesCount -= 1
            
            self.createGrass(dt)
            for g in self.grass[:]:
                pygame.draw.rect(screen, "#17A321", pygame.Rect(g.x, g.y, 5, 5))
                distToClosestRabbit, closestRabbit = g.getMinDistanceToRabbit(self.numRabbitsList)
                if distToClosestRabbit is not None and distToClosestRabbit <= self.minDistanceForRabbitToEatGrass:
                    closestRabbit.increaseEnergyOnGrass()
                    rabbitEatingSound.play()
                    self.grass.remove(g)
            
            # texts
            self.rabbitsCountText = self.createText(screen, f"Total Rabbits: {int(self.numRabbitsCount)}", textFont, "#FFFFFF", 20, 20)
            self.wolvesCountText = self.createText(screen, f"Total Wolves: {int(self.numWolvesCount)}", textFont, "#FFFFFF", 20, 50)
            self.fpsText = self.createText(screen, f"FPS: {int(clock.get_fps())}", textFont, "#FFFFFF", 1200, 20)
            self.avgRabbitEnergyText = self.createText(screen, f"Avg. Rabbit Energy: {np.round(self.getAvgAnimalEnergy(self.numRabbitsList), 2)}", textFont, "#FFFFFF", 20, 80)
            self.avgWolfEnergyText = self.createText(screen, f"Avg. Wolf Energy: {np.round(self.getAvgAnimalEnergy(self.numWolvesList), 2)}", textFont, "#FFFFFF", 20, 110)
            
            pygame.display.flip()
            dt = clock.tick(60) / 1000
        
        pygame.quit()


if __name__ == "__main__":
    simulation = Simulation()
    simulation.createRabbits()
    simulation.createWolves()
    simulation.update()



