import pygame
from pygame.sprite import Sprite

from src.core.constants import ALTURA, AMARELO, TIRO_VEL, LASER_DURACAO


class Tiro(Sprite):
    def __init__(self, x, y, dano, escala, furia=False):
        super().__init__()
        self.dano = dano
        largura = int(4 * escala)
        altura = int(15 * escala)
        self.image = pygame.Surface((largura, altura))
        if furia:
            self.image.fill((255, 30, 30))
        else:
            self.image.fill(AMARELO if dano == 1 else (255, 100, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = TIRO_VEL

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


class ProjetilBoss(Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.vida = 12
        r = 12
        tam = r * 2 + 6
        self.image = pygame.Surface((tam, tam), pygame.SRCALPHA)
        c = tam // 2
        pygame.draw.circle(self.image, (210, 60, 10, 90),  (c, c), r + 2)
        pygame.draw.circle(self.image, (220, 70, 10, 255), (c, c), r)
        pygame.draw.circle(self.image, (255, 160, 30, 255), (c, c), r - 4)
        pygame.draw.circle(self.image, (255, 230, 180, 255), (c, c), r - 8)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = 4

    def update(self):
        self.rect.y += self.vel
        if self.rect.top > ALTURA:
            self.kill()


class FeixeBoss(Sprite):
    def __init__(self, x, y, largura, vel=2):
        super().__init__()
        self.vida = 120
        h = 44
        self.image = pygame.Surface((largura, h), pygame.SRCALPHA)

        mh = h / 2
        for gy in range(h):
            t = max(0.0, 1 - abs(gy - mh) / mh)
            a = int(140 * (t ** 0.6))
            pygame.draw.line(self.image, (255, 90, 0, a), (0, gy), (largura - 1, gy))

        core_h = 12
        cy = h // 2
        for gy in range(cy - core_h // 2, cy + core_h // 2):
            t = 1 - abs(gy - cy) / (core_h / 2)
            pygame.draw.line(self.image, (255, int(190 + t * 65), int(40 * t), 255),
                             (0, gy), (largura - 1, gy))

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
        cx = largura / 2

        for gx in range(largura):
            t = max(0.0, 1 - abs(gx - cx) / cx)
            pygame.draw.line(self.image, (160, 0, 255, int(90 * t)), (gx, 0), (gx, ALTURA - 1))

        core_w = largura // 3
        for gx in range(int(cx - core_w // 2), int(cx + core_w // 2)):
            t = 1 - abs(gx - cx) / (core_w / 2)
            pygame.draw.line(self.image, (255, 20, 20, int(210 * t)), (gx, 0), (gx, ALTURA - 1))

        for gx in range(int(cx) - 2, int(cx) + 2):
            pygame.draw.line(self.image, (255, 200, 220, 230), (gx, 0), (gx, ALTURA - 1))

        self.rect = self.image.get_rect(topleft=(x, 0))
        self.tempo_morte = pygame.time.get_ticks() + LASER_DURACAO

    def update(self):
        if pygame.time.get_ticks() > self.tempo_morte:
            self.kill()
