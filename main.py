import random

import pygame

from src.core.constants import (
    LARGURA, ALTURA,
    PRETO, BRANCO, VERDE, VERMELHO, ROXO, AMARELO,
)
from src.core.tela import Tela
from src.components.jogador import Jogador
from src.components.tiros import Tiro
from src.components.inimigos import MeteoroNormal, FragmentoMeteoro, ImpactoTiro, InimigoEspecial, Boss

pygame.init()

tela = Tela()
clock = pygame.time.Clock()

fonte_placar = pygame.font.SysFont("Arial", 25, bold=True)
fonte_grande = pygame.font.SysFont("Arial", 60, bold=True)
fonte_media = pygame.font.SysFont("Arial", 35, bold=True)

todos_sprites = pygame.sprite.Group()
grupo_inimigos = pygame.sprite.Group()
grupo_tiros = pygame.sprite.Group()
grupo_tiros_inimigos = pygame.sprite.Group()

pontos = 0
vidas = 3
fase_boss = False
vitoria = False
game_over = False
chefao = None


def get_pontos():
    return pontos


def resetar_jogo():
    global pontos, vidas, fase_boss, vitoria, game_over, player, chefao
    pontos = 0
    vidas = 3
    fase_boss = False
    vitoria = False
    game_over = False
    chefao = None
    todos_sprites.empty()
    grupo_inimigos.empty()
    grupo_tiros.empty()
    grupo_tiros_inimigos.empty()
    player = Jogador()
    todos_sprites.add(player)


player = Jogador()
todos_sprites.add(player)

SPAWN_TIMER = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_TIMER, 600)

ultimo_tiro = 0
COOLDOWN_TIRO = 180

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
                hp_v = 2
                hp_e = 3 if pontos < 1000 else 6
                if pontos < 1000:
                    if sorteio < 0.05:
                        novo = InimigoEspecial("esq", ROXO, hp_e, get_pontos)
                    elif sorteio < 0.10:
                        novo = InimigoEspecial("dir", AMARELO, hp_e, get_pontos)
                    else:
                        novo = MeteoroNormal(hp_v, get_pontos)
                else:
                    if sorteio < 0.30:
                        novo = InimigoEspecial("esq", ROXO, hp_e, get_pontos)
                    elif sorteio < 0.60:
                        novo = InimigoEspecial("dir", AMARELO, hp_e, get_pontos)
                    else:
                        novo = MeteoroNormal(hp_v, get_pontos)
                todos_sprites.add(novo)
                grupo_inimigos.add(novo)

    if not vitoria and not game_over:
        agora = pygame.time.get_ticks()
        if pygame.key.get_pressed()[pygame.K_SPACE] and agora - ultimo_tiro >= COOLDOWN_TIRO:
            ultimo_tiro = agora
            num = (pontos // 500) + 1
            dano_at = 2 if pontos >= 1000 else 1
            esc_at = 1 + (0.5 * (min(pontos, 900) // 300))
            for i in range(num):
                off = (i - (num - 1) / 2) * 20
                t = Tiro(player.rect.centerx + off, player.rect.top, dano_at, esc_at)
                todos_sprites.add(t)
                grupo_tiros.add(t)

    if not vitoria and not game_over:
        if pontos >= 1500 and not fase_boss:
            fase_boss = True
            for i in grupo_inimigos:
                i.kill()
            chefao = Boss(todos_sprites, grupo_tiros_inimigos)
            todos_sprites.add(chefao)
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
                if isinstance(inimigo, MeteoroNormal):
                    for b in balas:
                        todos_sprites.add(ImpactoTiro(b.rect.centerx, b.rect.centery))
                if inimigo.vida <= 0:
                    if isinstance(inimigo, MeteoroNormal):
                        for _ in range(random.randint(4, 7)):
                            f = FragmentoMeteoro(inimigo.rect.centerx, inimigo.rect.centery, inimigo.tom)
                            todos_sprites.add(f)
                    pontos += 35 if isinstance(inimigo, InimigoEspecial) else 10
                    inimigo.kill()
                elif isinstance(inimigo, (MeteoroNormal, InimigoEspecial)):
                    inimigo.atualizar_visual()

        hits_defesa = pygame.sprite.groupcollide(grupo_tiros_inimigos, grupo_tiros, False, True)
        for p, balas in hits_defesa.items():
            if hasattr(p, 'vida'):
                p.vida -= sum(b.dano for b in balas)
                if p.vida <= 0:
                    p.kill()

        if not player.invencivel:
            if pygame.sprite.spritecollideany(player, grupo_inimigos) or pygame.sprite.spritecollideany(player, grupo_tiros_inimigos):
                vidas -= 1
                if vidas <= 0:
                    game_over = True
                else:
                    player.invencivel = True
                    player.tempo_invencivel = pygame.time.get_ticks() + 5000

    tela.preencher(PRETO)
    if not vitoria and not game_over:
        tela.desenhar(todos_sprites)
        tela.blit(fonte_placar.render(f"SCORE: {pontos}", True, BRANCO), (20, 20))
        tela.blit(fonte_placar.render(f"LIVES: {vidas}", True, VERMELHO), (20, 50))
        tela.blit(fonte_placar.render(f"WEAPON LVL: {(pontos // 500) + 1}", True, VERDE), (20, 80))
        if fase_boss and chefao is not None and chefao.alive():
            pygame.draw.rect(tela.surface, VERMELHO, (LARGURA / 2 - 100, 20, 200, 20))
            pygame.draw.rect(tela.surface, VERDE, (LARGURA / 2 - 100, 20, max(0, chefao.vida // 3), 20))

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

    tela.atualizar()

pygame.quit()
