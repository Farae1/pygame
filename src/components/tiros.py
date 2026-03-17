import pygame
from pygame.sprite import Sprite

from src.core.constants import ALTURA, AMARELO


class Tiro(Sprite):
    def __init__(self, x, y, dano, escala):
        super().__init__()
        self.dano = dano
        largura = int(4 * escala)
        altura = int(15 * escala)
        self.image = pygame.Surface((largura, altura))
        self.image.fill(AMARELO if dano == 1 else (255, 100, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = 15

    def update(self):
        self.rect.y -= self.vel
        if self.rect.bottom < 0:
            self.kill()


class TiroInimigo(Sprite):
    def __init__(self, x, y, largura, altura, cor, vida, vel):
        super().__init__()
        self.vida = vida
        self.image = pygame.Surface((largura, altura))
        self.image.fill(cor)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = vel

    def update(self):
        self.rect.y += self.vel
        if self.rect.top > ALTURA:
            self.kill()


class LaserBoss(Sprite):
    def __init__(self, x, largura):
        super().__init__()
        self.image = pygame.Surface((largura, ALTURA), pygame.SRCALPHA)
        self.image.fill((255, 0, 0, 180))
        self.rect = self.image.get_rect(topleft=(x, 0))
        self.tempo_morte = pygame.time.get_ticks() + 1000

    def update(self):
        if pygame.time.get_ticks() > self.tempo_morte:
            self.kill()
