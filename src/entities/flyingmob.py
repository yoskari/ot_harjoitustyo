import pygame
from settings import TILE_SIZE, GREEN, RED
from resources import crow_images
from entities.particle import Particle
from entities.drop import DroppedItem
from functions import move, draw_health_bar

class FlyingMob():
    """
    An enemy mob which flies towards the player
    """
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.image = crow_images[0]
        self.imageindex = 0
        self.invert = 0
        self.anim_repeat = 20
        self.dx = 0
        self.dy = 0
        self.speed = 2
        self.max_speed = self.speed * 2
        self.dead = False
        self.max_health = 25
        self.health = self.max_health
        self.mobtype = "bird"
        self.collisions = {}

    def update(self, player, world):
        """
        Updates the health, animation and movement of the object
        """
        # despawning
        if self.rect.x < player.rect.x - 1000 or self.rect.x > player.rect.x + 1000:
            print("Bird despawned")
            world.entities.remove(self)
            world.mobs.remove(self)

        # death
        if self.health <= 0:
            for i in range(50):
                world.particles.append(Particle(self.rect.centerx, self.rect.centery, RED))
            world.drops.append(DroppedItem(self.rect.centerx, self.rect.centery,
                                           self.dx//2, self.dy, "meat"))
            world.mobs.remove(self)
            world.entities.remove(self)

        # animation
        self.anim_repeat -= 1
        if self.anim_repeat <= 0:
            self.anim_repeat = 20
            self.imageindex += 1
            if self.imageindex >= len(crow_images):
                self.imageindex = 0
            self.image = crow_images[self.imageindex]

        # movement
        move(self, world, True)

        if self.rect.x < player.rect.x and self.dx < self.speed:
            self.dx += 0.07
            self.invert = 1
        if self.rect.x > player.rect.x and self.dx > -self.speed:
            self.dx -= 0.07
            self.invert = 0

        if abs(player.rect.x - self.rect.x) > 100:
            if self.rect.y < player.rect.y - 100 and self.dy < self.speed:
                self.dy += 0.07
            if self.rect.y > player.rect.y - 100 and self.dy > -self.speed:
                self.dy -= 0.07
        else:
            if self.rect.y < player.rect.y and self.dy < self.speed:
                self.dy += 0.2
            if self.rect.y > player.rect.y and self.dy > -self.speed:
                self.dy -= 0.2

        if self.collisions["left"] or self.collisions["right"] and self.dx > -self.speed:
            self.dy -= 0.4

        if self.dx > self.max_speed:
            self.dx = self.max_speed
        if self.dx < -self.max_speed:
            self.dx = -self.max_speed
        if self.dy > self.max_speed:
            self.dy = self.max_speed
        if self.dy < -self.max_speed:
            self.dy = -self.max_speed

    def draw(self, display, world): # pragma: no cover
        """
        Draws the Flying Mob object
        """
        display.blit(pygame.transform.flip(self.image, self.invert, 0), (self.rect.x - world.scrollx, self.rect.y - world.scrolly))

        draw_health_bar(self.rect.centerx-world.scrollx, self.rect.y-TILE_SIZE-world.scrolly,
                        display, self.health, self.max_health)
