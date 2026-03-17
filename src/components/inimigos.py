import random
import math

import pygame
from pygame.sprite import Sprite

from src.core.constants import LARGURA, ALTURA, VERMELHO, CINZA, BRANCO, ROXO, AMARELO, VERDE
from src.components.tiros import TiroInimigo, LaserBoss


class InimigoVermelho(Sprite):
    def __init__(self, hp, get_pontos):
        super().__init__()
        self.vida = hp
        self._get_pontos = get_pontos
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.rect(self.image, VERMELHO, (0, 0, 30, 30), border_radius=5)
        self.reset_pos()

    def reset_pos(self):
        self.rect = self.image.get_rect(center=(random.randint(15, LARGURA - 15), -50))
        bonus_vel = (self._get_pontos() // 200) * 2
        self.vel_y = random.randint(3, 5) + (bonus_vel / 5)

    def update(self):
        self.rect.y += self.vel_y
        if self.rect.top > ALTURA:
            self.reset_pos()


class InimigoEspecial(Sprite):
    def __init__(self, lado, cor, hp, get_pontos):
        super().__init__()
        self.cor_base = cor
        self.lado = lado
        self.vida = hp
        self.vida_max = hp
        self._get_pontos = get_pontos
        self.image = pygame.Surface((35, 35), pygame.SRCALPHA)
        self.atualizar_visual()
        self.tempo_offset = random.randint(0, 1000)
        self.reset_pos()

    def atualizar_visual(self):
        pct = self.vida / self.vida_max
        cor = self.cor_base if pct > 0.7 else CINZA if pct > 0.3 else BRANCO
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, cor, (0, 0, 35, 35), border_radius=8)

    def reset_pos(self):
        pontos = self._get_pontos()
        x_ini = -50 if self.lado == "esq" else LARGURA + 50
        x_curva = 180 if self.lado == "esq" else LARGURA - 180
        self.caminho = [(x_ini, 560), (x_curva, 240), (LARGURA / 2, 80), (random.randint(20, LARGURA - 20), 900)]
        self.ponto_atual, self.pos = 0, pygame.math.Vector2(self.caminho[0])
        self.rect = self.image.get_rect(center=self.pos)
        self.vel = 5 + (pontos // 200) * 0.5
        self.amplitude = 60 + (pontos // 350) * 15
        self.frequencia = 0.005 + (pontos // 350) * 0.001

    def update(self):
        alvo = pygame.math.Vector2(self.caminho[self.ponto_atual])
        direcao = alvo - self.pos
        if direcao.length() < self.vel:
            self.ponto_atual += 1
            if self.ponto_atual >= len(self.caminho):
                self.reset_pos()
        elif direcao.length() > 0:
            self.pos += direcao.normalize() * self.vel
        balanco = math.sin(pygame.time.get_ticks() * self.frequencia + self.tempo_offset) * self.amplitude
        self.rect.center = (self.pos.x + balanco, self.pos.y)


class Boss(Sprite):
    def __init__(self, todos, grupo_tiros_inimigos):
        super().__init__()
        self.vida = 600
        self.image_base = pygame.Surface((150, 80), pygame.SRCALPHA)
        pygame.draw.rect(self.image_base, ROXO, (0, 0, 150, 80), border_radius=15)
        pygame.draw.rect(self.image_base, AMARELO, (40, 20, 70, 40), border_radius=5)
        self.image = self.image_base.copy()
        self.rect = self.image.get_rect(center=(LARGURA / 2, -100))
        self.pos_y_alvo = 150
        self.vel = 4
        self.todos, self.grupo_tiros_inimigos = todos, grupo_tiros_inimigos
        self.ultimo_bloco, self.ultimo_especial = pygame.time.get_ticks(), pygame.time.get_ticks()
        self.estado = "NORMAL"
        self.timer_estado = 0

    def update(self):
        agora = pygame.time.get_ticks()
        if self.rect.centery < self.pos_y_alvo:
            self.rect.y += 2
            return

        if self.estado == "NORMAL":
            self.rect.x += self.vel
            if self.rect.right > LARGURA or self.rect.left < 0:
                self.vel *= -1
            if agora - self.ultimo_bloco > 2000:
                bloco = TiroInimigo(self.rect.centerx, self.rect.bottom, 25, 25, VERDE, 12, 4)
                self.todos.add(bloco)
                self.grupo_tiros_inimigos.add(bloco)
                self.ultimo_bloco = agora
            if agora - self.ultimo_especial > 15000:
                largura_g = LARGURA // 2
                x_ale = random.randint(largura_g // 2, LARGURA - largura_g // 2)
                vel_golpe = 3.5 if self.vida <= 300 else 1.5
                esp = TiroInimigo(x_ale, self.rect.bottom, largura_g, 40, AMARELO, 120, vel_golpe)
                self.todos.add(esp)
                self.grupo_tiros_inimigos.add(esp)
                self.ultimo_especial = agora
            if random.random() < 0.005:
                self.estado = "PREPARANDO"
                self.timer_estado = agora + 1500
        elif self.estado == "PREPARANDO":
            alpha = 100 if (agora // 100) % 2 == 0 else 255
            self.image.set_alpha(alpha)
            if agora > self.timer_estado:
                self.estado = "LASER"
                self.timer_estado = agora + 1000
                laser = LaserBoss(self.rect.x, self.rect.width)
                self.todos.add(laser)
                self.grupo_tiros_inimigos.add(laser)
        elif self.estado == "LASER":
            self.image.set_alpha(255)
            if agora > self.timer_estado:
                self.estado = "NORMAL"
