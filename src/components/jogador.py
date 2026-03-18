import pygame
from pygame.sprite import Sprite

from src.core.constants import LARGURA, ALTURA, JOGADOR_VEL


class Jogador(Sprite):
    def __init__(self):
        super().__init__()
        w, h = 52, 48
        cx = w // 2
        self.image_original = pygame.Surface((w, h), pygame.SRCALPHA)

        pygame.draw.polygon(self.image_original, (0, 80, 140),
                            [(cx - 4, h // 2 + 2), (1, h - 2), (cx - 9, h - 1)])
        pygame.draw.polygon(self.image_original, (0, 80, 140),
                            [(cx + 4, h // 2 + 2), (w - 1, h - 2), (cx + 9, h - 1)])
        pygame.draw.line(self.image_original, (0, 150, 200),
                         (cx - 4, h // 2 + 2), (1, h - 2), 1)
        pygame.draw.line(self.image_original, (0, 150, 200),
                         (cx + 4, h // 2 + 2), (w - 1, h - 2), 1)

        hull = [
            (cx, 0), (cx + 5, 9), (cx + 8, 22),
            (cx + 7, h - 9), (cx - 7, h - 9), (cx - 8, 22), (cx - 5, 9),
        ]
        pygame.draw.polygon(self.image_original, (10, 150, 195), hull)
        pygame.draw.polygon(self.image_original, (80, 210, 255), hull, 1)

        pygame.draw.ellipse(self.image_original, (130, 210, 255), (cx - 5, 7, 10, 14))
        pygame.draw.ellipse(self.image_original, (210, 242, 255), (cx - 3, 9, 6, 8))

        pygame.draw.line(self.image_original, (50, 170, 215), (cx, 21), (cx, h - 11), 1)

        for ex in (cx - 10, cx + 2):
            pygame.draw.ellipse(self.image_original, (20, 60, 210), (ex, h - 11, 10, 10))
            pygame.draw.ellipse(self.image_original, (100, 170, 255), (ex + 2, h - 9, 6, 6))
            pygame.draw.ellipse(self.image_original, (210, 235, 255), (ex + 3, h - 7, 4, 3))

        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(center=(LARGURA / 2, ALTURA - 50))
        self.vel = JOGADOR_VEL
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
                self.image.set_alpha(0 if (agora // 150) % 2 == 0 else 255)
