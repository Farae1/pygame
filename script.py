import pygame
import random
import math

pygame.init()
LARGURA, ALTURA = 600, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Galaga: Final Battle")
clock = pygame.time.Clock()

PRETO, BRANCO, VERDE = (0, 0, 0), (255, 255, 255), (0, 255, 0)
VERMELHO, ROXO, AMARELO, CINZA = (255, 50, 50), (150, 0, 255), (255, 255, 0), (100, 100, 100)

fonte_placar = pygame.font.SysFont("Arial", 25, bold=True)
fonte_grande = pygame.font.SysFont("Arial", 60, bold=True)
fonte_media = pygame.font.SysFont("Arial", 35, bold=True)


class Jogador(pygame.sprite.Sprite):
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


class Tiro(pygame.sprite.Sprite):
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
        if self.rect.bottom < 0: self.kill()


class TiroInimigo(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura, cor, vida, vel):
        super().__init__()
        self.vida = vida
        self.image = pygame.Surface((largura, altura))
        self.image.fill(cor)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = vel

    def update(self):
        self.rect.y += self.vel
        if self.rect.top > ALTURA: self.kill()


class LaserBoss(pygame.sprite.Sprite):
    def __init__(self, x, largura):
        super().__init__()
        self.image = pygame.Surface((largura, ALTURA), pygame.SRCALPHA)
        self.image.fill((255, 0, 0, 180))
        self.rect = self.image.get_rect(topleft=(x, 0))
        self.tempo_morte = pygame.time.get_ticks() + 1000

    def update(self):
        if pygame.time.get_ticks() > self.tempo_morte:
            self.kill()


class InimigoVermelho(pygame.sprite.Sprite):
    def __init__(self, hp):
        super().__init__()
        self.vida = hp
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.rect(self.image, VERMELHO, (0, 0, 30, 30), border_radius=5)
        self.reset_pos()

    def reset_pos(self):
        self.rect = self.image.get_rect(center=(random.randint(15, LARGURA - 15), -50))
        bonus_vel = (pontos // 200) * 2
        self.vel_y = random.randint(3, 5) + (bonus_vel / 5)

    def update(self):
        self.rect.y += self.vel_y
        if self.rect.top > ALTURA: self.reset_pos()


class InimigoEspecial(pygame.sprite.Sprite):
    def __init__(self, lado, cor, hp):
        super().__init__()
        self.cor_base = cor
        self.lado = lado
        self.vida = hp
        self.vida_max = hp
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
            if self.ponto_atual >= len(self.caminho): self.reset_pos()
        elif direcao.length() > 0:
            self.pos += direcao.normalize() * self.vel
        balanco = math.sin(pygame.time.get_ticks() * self.frequencia + self.tempo_offset) * self.amplitude
        self.rect.center = (self.pos.x + balanco, self.pos.y)


class Boss(pygame.sprite.Sprite):
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
            if self.rect.right > LARGURA or self.rect.left < 0: self.vel *= -1
            if agora - self.ultimo_bloco > 2000:
                bloco = TiroInimigo(self.rect.centerx, self.rect.bottom, 25, 25, VERDE, 12, 4)
                self.todos.add(bloco);
                self.grupo_tiros_inimigos.add(bloco)
                self.ultimo_bloco = agora
            if agora - self.ultimo_especial > 15000:
                largura_g = LARGURA // 2
                x_ale = random.randint(largura_g // 2, LARGURA - largura_g // 2)
                vel_golpe = 3.5 if self.vida <= 300 else 1.5
                esp = TiroInimigo(x_ale, self.rect.bottom, largura_g, 40, AMARELO, 120, vel_golpe)
                self.todos.add(esp);
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
                self.todos.add(laser);
                self.grupo_tiros_inimigos.add(laser)
        elif self.estado == "LASER":
            self.image.set_alpha(255)
            if agora > self.timer_estado: self.estado = "NORMAL"


def resetar_jogo():
    global pontos, vidas, fase_boss, vitoria, game_over, todos_sprites, grupo_inimigos, grupo_tiros, grupo_tiros_inimigos, player
    pontos = 0
    vidas = 3
    fase_boss = False
    vitoria = False
    game_over = False
    todos_sprites.empty()
    grupo_inimigos.empty()
    grupo_tiros.empty()
    grupo_tiros_inimigos.empty()
    player = Jogador()
    todos_sprites.add(player)


todos_sprites = pygame.sprite.Group()
grupo_inimigos = pygame.sprite.Group()
grupo_tiros = pygame.sprite.Group()
grupo_tiros_inimigos = pygame.sprite.Group()

player = Jogador()
todos_sprites.add(player)

SPAWN_TIMER = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_TIMER, 600)

pontos = 0
vidas = 3
fase_boss = False
vitoria = False
game_over = False

rodando = True
while rodando:
    clock.tick(60)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if (vitoria or game_over) and evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r:
                resetar_jogo()

        if not vitoria and not game_over:
            if evento.type == SPAWN_TIMER and not fase_boss:
                sorteio = random.random()
                hp_v = 1 if pontos < 1000 else 2
                hp_e = 3 if pontos < 1000 else 6
                if pontos < 1000:
                    if sorteio < 0.05:
                        novo = InimigoEspecial("esq", ROXO, hp_e)
                    elif sorteio < 0.10:
                        novo = InimigoEspecial("dir", AMARELO, hp_e)
                    else:
                        novo = InimigoVermelho(hp_v)
                else:
                    if sorteio < 0.30:
                        novo = InimigoEspecial("esq", ROXO, hp_e)
                    elif sorteio < 0.60:
                        novo = InimigoEspecial("dir", AMARELO, hp_e)
                    else:
                        novo = InimigoVermelho(hp_v)
                todos_sprites.add(novo);
                grupo_inimigos.add(novo)

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                num = (pontos // 500) + 1
                dano_at = 2 if pontos >= 1000 else 1
                esc_at = 1 + (0.5 * (min(pontos, 900) // 300))
                for i in range(num):
                    off = (i - (num - 1) / 2) * 20
                    t = Tiro(player.rect.centerx + off, player.rect.top, dano_at, esc_at)
                    todos_sprites.add(t);
                    grupo_tiros.add(t)

    if not vitoria and not game_over:
        if pontos >= 1500 and not fase_boss:
            fase_boss = True
            for i in grupo_inimigos: i.kill()
            chefao = Boss(todos_sprites, grupo_tiros_inimigos)
            todos_sprites.add(chefao);
            grupo_inimigos.add(chefao)

        todos_sprites.update()

        hits = pygame.sprite.groupcollide(grupo_inimigos, grupo_tiros, False, True)
        for inimigo, balas in hits.items():
            total_dano = sum(b.dano for b in balas)
            if isinstance(inimigo, Boss):
                inimigo.vida -= total_dano
                if inimigo.vida <= 0:
                    inimigo.kill()
                    vitoria = True
            else:
                inimigo.vida -= total_dano
                if inimigo.vida <= 0:
                    pontos += 35 if isinstance(inimigo, InimigoEspecial) else 10
                    inimigo.kill()
                elif isinstance(inimigo, InimigoEspecial):
                    inimigo.atualizar_visual()

        hits_defesa = pygame.sprite.groupcollide(grupo_tiros_inimigos, grupo_tiros, False, True)
        for p, balas in hits_defesa.items():
            if hasattr(p, 'vida'):
                p.vida -= sum(b.dano for b in balas)
                if p.vida <= 0: p.kill()

        if not player.invencivel:
            if pygame.sprite.spritecollideany(player, grupo_inimigos) or pygame.sprite.spritecollideany(player,
                                                                                                        grupo_tiros_inimigos):
                vidas -= 1
                if vidas <= 0:
                    game_over = True
                else:
                    player.invencivel = True
                    player.tempo_invencivel = pygame.time.get_ticks() + 5000

    tela.fill(PRETO)
    if not vitoria and not game_over:
        todos_sprites.draw(tela)
        tela.blit(fonte_placar.render(f"SCORE: {pontos}", True, BRANCO), (20, 20))
        tela.blit(fonte_placar.render(f"LIVES: {vidas}", True, VERMELHO), (20, 50))
        tela.blit(fonte_placar.render(f"WEAPON LVL: {(pontos // 500) + 1}", True, VERDE), (20, 80))
        if fase_boss and 'chefao' in locals() and chefao.alive():
            pygame.draw.rect(tela, VERMELHO, (LARGURA / 2 - 100, 20, 200, 20))
            pygame.draw.rect(tela, VERDE, (LARGURA / 2 - 100, 20, max(0, chefao.vida // 3), 20))

    elif vitoria:
        txt_v = fonte_grande.render("YOU WIN!", True, VERDE)
        txt_r = fonte_media.render("Press R to Restart", True, BRANCO)
        tela.blit(txt_v, (LARGURA // 2 - 130, ALTURA // 2 - 50))
        tela.blit(txt_r, (LARGURA // 2 - 135, ALTURA // 2 + 30))

    elif game_over:
        txt_g = fonte_grande.render("GAME OVER", True, VERMELHO)
        txt_s = fonte_media.render(f"FINAL SCORE: {pontos}", True, BRANCO)
        txt_r = fonte_media.render("Press R to Restart", True, BRANCO)
        tela.blit(txt_g, (LARGURA // 2 - 160, ALTURA // 2 - 80))
        tela.blit(txt_s, (LARGURA // 2 - 110, ALTURA // 2))
        tela.blit(txt_r, (LARGURA // 2 - 135, ALTURA // 2 + 60))

    pygame.display.flip()

pygame.quit()