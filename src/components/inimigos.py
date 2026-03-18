import random
import math

import pygame
from pygame.sprite import Sprite

from src.core.constants import (
    LARGURA, ALTURA, VERMELHO, CINZA, BRANCO, ROXO, AMARELO, VERDE,
    BOSS_VEL, BOSS_POS_Y_ALVO, BOSS_COOLDOWN_TIRO, BOSS_COOLDOWN_FEIXE, BOSS_PROB_LASER,
)
from src.components.tiros import TiroInimigo, LaserBoss, ProjetilBoss, FeixeBoss


class MeteoroNormal(Sprite):
    def __init__(self, hp, get_horda):
        super().__init__()
        self.vida = hp
        self._get_horda = get_horda
        self._image_normal = self._gerar_imagem()
        self._image_rachado = self._image_normal.copy()
        self._image_base = self._image_normal
        self.image = self._image_base
        self.angulo = random.randint(0, 360)
        self.vel_rotacao = random.uniform(-2.5, 2.5)
        self.reset_pos()

    def _gerar_imagem(self):
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
        return surf

    def atualizar_visual(self):
        cx, cy = 25, 25
        for _ in range(random.randint(2, 3)):
            ang = random.uniform(0, 2 * math.pi)
            x = cx + random.uniform(-13, 13)
            y = cy + random.uniform(-13, 13)
            pts_crack = [(int(x), int(y))]
            for _ in range(random.randint(3, 5)):
                ang += random.uniform(-0.5, 0.5)
                x += math.cos(ang) * random.uniform(3, 7)
                y += math.sin(ang) * random.uniform(3, 7)
                pts_crack.append((int(x), int(y)))
            pygame.draw.lines(self._image_rachado, (0, 0, 0), False, pts_crack, 1)
            pygame.draw.lines(self._image_rachado, (0, 0, 0), False, pts_crack, 2)
        self._image_base = self._image_rachado

    def reset_pos(self):
        self.rect = self._image_normal.get_rect(center=(random.randint(25, LARGURA - 25), -60))
        self.vel_y = random.uniform(1.5, 2.8) + (self._get_horda() - 1) * 0.5

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


class MeteoroEspecial(Sprite):
    def __init__(self, hp, get_horda):
        super().__init__()
        self.vida = hp
        self._get_horda = get_horda
        self._image_normal = self._gerar_imagem()
        self._image_rachado = self._image_normal.copy()
        self._image_base = self._image_normal
        self.image = self._image_base
        self.angulo = random.randint(0, 360)
        self.vel_rotacao = random.uniform(-1.2, 1.2)
        self.reset_pos()

    def _gerar_imagem(self):
        tamanho = 200
        surf = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
        cx, cy = tamanho // 2, tamanho // 2
        num_pts = random.randint(9, 13)
        pts = []
        for i in range(num_pts):
            ang = (2 * math.pi / num_pts) * i + random.uniform(-0.25, 0.25)
            r = random.randint(68, 92)
            pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
        self.tom = random.randint(70, 105)
        pygame.draw.polygon(surf, (self.tom, self.tom, self.tom), pts)
        pygame.draw.polygon(surf, (self.tom - 30, self.tom - 30, self.tom - 30), pts, 3)
        for _ in range(4):
            cx2 = cx + random.randint(-25, 25)
            cy2 = cy + random.randint(-25, 25)
            pygame.draw.circle(surf, (self.tom - 25, self.tom - 25, self.tom - 25), (cx2, cy2), random.randint(5, 14))
        return surf

    def atualizar_visual(self):
        cx, cy = 100, 100
        for _ in range(random.randint(2, 4)):
            ang = random.uniform(0, 2 * math.pi)
            x = cx + random.uniform(-52, 52)
            y = cy + random.uniform(-52, 52)
            pts_crack = [(int(x), int(y))]
            for _ in range(random.randint(4, 7)):
                ang += random.uniform(-0.5, 0.5)
                x += math.cos(ang) * random.uniform(10, 22)
                y += math.sin(ang) * random.uniform(10, 22)
                pts_crack.append((int(x), int(y)))
            pygame.draw.lines(self._image_rachado, (0, 0, 0), False, pts_crack, 2)
            pygame.draw.lines(self._image_rachado, (0, 0, 0), False, pts_crack, 4)
        self._image_base = self._image_rachado

    def reset_pos(self):
        self.rect = self._image_normal.get_rect(center=(random.randint(100, LARGURA - 100), -150))
        self.vel_y = random.uniform(2.25, 4.2) + (self._get_horda() - 1) * 0.75

    def update(self):
        self.rect.y += self.vel_y
        self.angulo = (self.angulo + self.vel_rotacao) % 360
        self.image = pygame.transform.rotate(self._image_base, self.angulo)
        self.rect = self.image.get_rect(center=self.rect.center)
        if self.rect.top > ALTURA:
            self.reset_pos()


class Boss(Sprite):
    W, H = 200, 95

    def __init__(self, todos, grupo_tiros_inimigos, vida=600):
        super().__init__()
        self.vida = vida
        self.vida_max = vida
        self.image_base = self._gerar_imagem()
        self.image = self.image_base.copy()
        self.rect = self.image.get_rect(center=(LARGURA / 2, -120))
        self.pos_y_alvo = BOSS_POS_Y_ALVO
        self.vel = BOSS_VEL
        self.todos, self.grupo_tiros_inimigos = todos, grupo_tiros_inimigos
        self.ultimo_tiro = pygame.time.get_ticks()
        self.ultimo_feixe = pygame.time.get_ticks()
        self.estado = "NORMAL"
        self.timer_estado = 0

    def _gerar_imagem(self):
        W, H = self.W, self.H
        surf = pygame.Surface((W, H), pygame.SRCALPHA)
        cx = W // 2

        for ex in range(20, W - 10, 32):
            pygame.draw.ellipse(surf, (40, 0, 80), (ex, H - 18, 22, 18))
            pygame.draw.ellipse(surf, (120, 0, 200), (ex + 3, H - 14, 16, 12))
            pygame.draw.ellipse(surf, (200, 100, 255), (ex + 6, H - 10, 10, 6))

        for px, pw in ((2, 28), (W - 30, 28)):
            pygame.draw.rect(surf, (60, 0, 100), (px, H // 2 - 14, pw, 28), border_radius=5)
            pygame.draw.rect(surf, (130, 0, 200), (px + 3, H // 2 - 10, pw - 6, 20), border_radius=3)

        for bx in (6, W - 10):
            pygame.draw.rect(surf, (80, 0, 130), (bx, H // 2 - 3, 12, 6), border_radius=2)

        hull = [
            (cx, 4), (cx + 55, 18), (cx + 80, 35),
            (cx + 75, H - 22), (cx + 40, H - 8), (cx, H - 4),
            (cx - 40, H - 8), (cx - 75, H - 22), (cx - 80, 35), (cx - 55, 18),
        ]
        pygame.draw.polygon(surf, (55, 0, 90), hull)
        pygame.draw.polygon(surf, (130, 0, 210), hull, 2)

        pygame.draw.line(surf, (100, 0, 160), (cx - 40, 20), (cx - 60, H - 25), 1)
        pygame.draw.line(surf, (100, 0, 160), (cx + 40, 20), (cx + 60, H - 25), 1)
        pygame.draw.line(surf, (100, 0, 160), (cx - 20, 10), (cx - 35, H - 15), 1)
        pygame.draw.line(surf, (100, 0, 160), (cx + 20, 10), (cx + 35, H - 15), 1)

        pygame.draw.circle(surf, (160, 0, 255), (cx, H // 2 - 5), 20)
        pygame.draw.circle(surf, (210, 80, 255), (cx, H // 2 - 5), 14)
        pygame.draw.circle(surf, (240, 180, 255), (cx, H // 2 - 5), 7)

        pygame.draw.ellipse(surf, (255, 220, 100), (cx - 12, 10, 24, 10))
        pygame.draw.ellipse(surf, (255, 255, 180), (cx - 7, 12, 14, 6))

        return surf

    def _pulsar_core(self, t):
        cx = self.W // 2
        cy = self.H // 2 - 5
        r = 22 + int(4 * math.sin(t * 0.006))
        a = int(160 + 80 * math.sin(t * 0.006))
        pygame.draw.circle(self.image, (180, 0, 255, min(255, a)), (cx, cy), r, 2)

    def _atualizar_imagem(self, agora):
        self.image = self.image_base.copy()
        self._pulsar_core(agora)

    def _disparar_tiro(self, agora):
        for off in (-30, 0, 30):
            orb = ProjetilBoss(self.rect.centerx + off, self.rect.bottom)
            self.todos.add(orb)
            self.grupo_tiros_inimigos.add(orb)
        self.ultimo_tiro = agora

    def _disparar_feixe(self, agora):
        largura_g = LARGURA // 2
        x_ale = random.randint(largura_g // 2, LARGURA - largura_g // 2)
        vel_golpe = 3.5 if self.vida <= self.vida_max // 2 else 2.0
        feixe = FeixeBoss(x_ale, self.rect.bottom + 22, largura_g, vel_golpe)
        self.todos.add(feixe)
        self.grupo_tiros_inimigos.add(feixe)
        self.ultimo_feixe = agora

    def _iniciar_laser(self, agora):
        self.estado = "PREPARANDO"
        self.timer_estado = agora + 1500

    def update(self):
        agora = pygame.time.get_ticks()

        if self.rect.centery < self.pos_y_alvo:
            self.rect.y += 2
            self._atualizar_imagem(agora)
            return

        self._atualizar_imagem(agora)

        if self.estado == "NORMAL":
            self.rect.x += self.vel
            if self.rect.right > LARGURA or self.rect.left < 0:
                self.vel *= -1
            if agora - self.ultimo_tiro > BOSS_COOLDOWN_TIRO:
                self._disparar_tiro(agora)
            if agora - self.ultimo_feixe > BOSS_COOLDOWN_FEIXE:
                self._disparar_feixe(agora)
            if random.random() < BOSS_PROB_LASER:
                self._iniciar_laser(agora)

        elif self.estado == "PREPARANDO":
            self.image.set_alpha(100 if (agora // 100) % 2 == 0 else 255)
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
