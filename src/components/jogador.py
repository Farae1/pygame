import pygame
from pygame.sprite import Sprite

from src.core.constants import LARGURA, ALTURA, VERDE


class Jogador(Sprite):
    def __init__(self):
        super().__init__()
        self.image_original = pygame.Surface((40, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.image_original, VERDE, [(20, 0), (0, 30), (40, 30)])
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(center=(LARGURA / 2, ALTURA - 50))
        self.vel = 9
        self.invencivel = False
        self.tempo_invencivel = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.rect.left > 0:
            self.rect.x -= self.vel
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.rect.right < LARGURA:
            self.rect.x += self.vel

        if self.invencivel:
            agora = pygame.time.get_ticks()
            if agora > self.tempo_invencivel:
                self.invencivel = False
                self.image.set_alpha(255)
            else:
                alpha = 0 if (agora // 150) % 2 == 0 else 255
                self.image.set_alpha(alpha)
