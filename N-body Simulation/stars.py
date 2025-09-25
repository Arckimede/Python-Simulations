from pygame_particles import Particle, ParticleContainer, Circle
import random
import pygame

class Star():
    def __init__(self):
        super().__init__()
        self.container = ParticleContainer()
        self.spawnDelay = 1
        self.time = 0
        
    def createStars(self, dt, screen: pygame.Surface, screenWidth = 1280, screenHeight = 720):
        self.time += dt
        
        if self.time >= self.spawnDelay:
            self.time = 0
            particle = Particle(
                center_x=random.randint(0, screenWidth),
                center_y=random.randint(0, screenHeight),
                objects_count=1,
                life_seconds=2,
                fade_seconds=3,
                color="white",
                size=(1, 5),
                speed=(1, 5),
                width=0,
                shape_cls=Circle,
            )
        
            self.container.add(particle)
        self.container.draw(screen)

    

        
        
