import random
import math

import pygame
from pygame.sprite import Sprite

from src.core.constants import LARGURA, ALTURA, VERMELHO, CINZA, BRANCO, ROXO, AMARELO, VERDE
from src.components.tiros import TiroInimigo, LaserBoss


class MeteoroNormal(Sprite):
    def __init__(self, hp, get_pontos):
        super().__init__()
        self.vida = hp
        self._get_pontos = get_pontos
        self._image_normal, self._image_rachado = self._gerar_imagens()
        self._image_base = self._image_normal
        self.image = self._image_base
        self.angulo = random.randint(0, 360)
        self.vel_rotacao = random.uniform(-2.5, 2.5)
        self.reset_pos()

    def _gerar_imagens(self):
        tamanho = 50
        surf = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
        cx, cy = tamanho // 2, tamanho // 2
        num_pts = random.randint(8, 11)
        pts = []
        for i in range(num_pts):
            ang = (2 * math.pi / num_pts) * i + random.uniform(-0.3, 0.3)
            r = random.randint(17, 23)
            pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
        self.tom = random.randint(80, 115)
        pygame.draw.polygon(surf, (self.tom, self.tom, self.tom), pts)
        pygame.draw.polygon(surf, (self.tom - 30, self.tom - 30, self.tom - 30), pts, 2)
        for _ in range(2):
            cx2 = cx + random.randint(-8, 8)
            cy2 = cy + random.randint(-8, 8)
            pygame.draw.circle(surf, (self.tom - 25, self.tom - 25, self.tom - 25), (cx2, cy2), random.randint(2, 5))

        surf_rachado = surf.copy()
        for _ in range(random.randint(4, 6)):
            ang = random.uniform(0, 2 * math.pi)
            x, y = float(cx), float(cy)
            pts_crack = [(int(x), int(y))]
            for _ in range(random.randint(3, 5)):
                ang += random.uniform(-0.5, 0.5)
                x += math.cos(ang) * random.uniform(3, 7)
                y += math.sin(ang) * random.uniform(3, 7)
                pts_crack.append((int(x), int(y)))
            pygame.draw.lines(surf_rachado, (0, 0, 0), False, pts_crack, 1)
            pygame.draw.lines(surf_rachado, (0, 0, 0), False, pts_crack, 2)

        return surf, surf_rachado

    def atualizar_visual(self):
        self._image_base = self._image_rachado

    def reset_pos(self):
        self.rect = self._image_normal.get_rect(center=(random.randint(25, LARGURA - 25), -60))
        bonus_vel = (self._get_pontos() // 200) * 0.8
        self.vel_y = random.uniform(1.5, 2.8) + bonus_vel

    def update(self):
        self.rect.y += self.vel_y
        self.angulo = (self.angulo + self.vel_rotacao) % 360
        self.image = pygame.transform.rotate(self._image_base, self.angulo)
        self.rect = self.image.get_rect(center=self.rect.center)
        if self.rect.top > ALTURA:
            self.reset_pos()


class FragmentoMeteoro(Sprite):
    def __init__(self, x, y, tom):
        super().__init__()
        tamanho = random.randint(8, 15)
        surf = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
        cx, cy = tamanho // 2, tamanho // 2
        num_pts = random.randint(4, 6)
        pts = []
        for i in range(num_pts):
            ang = (2 * math.pi / num_pts) * i + random.uniform(-0.4, 0.4)
            r = random.randint(3, tamanho // 2 - 1)
            pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
        pygame.draw.polygon(surf, (tom, tom, tom), pts)
        self._image_original = surf
        self.image = surf.copy()
        self.rect = self.image.get_rect(center=(x, y))
        ang_saida = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        self.vel_x = math.cos(ang_saida) * speed
        self.vel_y = math.sin(ang_saida) * speed
        self.alpha = 255
        self.angulo = random.randint(0, 360)
        self.vel_rotacao = random.uniform(-6, 6)

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.alpha = max(0, self.alpha - 7)
        self.angulo = (self.angulo + self.vel_rotacao) % 360
        self.image = pygame.transform.rotate(self._image_original, self.angulo)
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect(center=self.rect.center)
        if self.alpha <= 0:
            self.kill()


class ImpactoTiro(Sprite):
    def __init__(self, x, y):
        super().__init__()
        self._cx = x
        self._cy = y
        self.raio = 5
        self.alpha = 220
        self._atualizar_surface()

    def _atualizar_surface(self):
        tamanho = self.raio * 2 + 2
        self.image = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 210, 80), (tamanho // 2, tamanho // 2), self.raio, 2)
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect(center=(self._cx, self._cy))

    def update(self):
        self.raio += 4
        self.alpha = max(0, self.alpha - 55)
        self._atualizar_surface()
        if self.alpha <= 0:
            self.kill()


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
