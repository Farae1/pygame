import math
import random

import pygame

from src.core.constants import (
    LARGURA, ALTURA, FPS,
    PRETO, BRANCO, VERDE, VERMELHO, AMARELO,
    PONTOS_POR_METEORO_NORMAL, PONTOS_POR_METEORO_ESPECIAL,
    VIDAS_INICIAIS, INVENCIVEL_DURACAO,
    COOLDOWN_TIRO, WEAPON_MAX_LV,
    ARMA_PONTOS_POR_NIVEL, ARMA_PONTOS_DANO2,
    ARMA_PONTOS_ESCALA_PASSO, ARMA_PONTOS_ESCALA_MAX,
    FURIA_DURACAO, FURIA_RECARGA, FURIA_MULT,
    HORDAS_POR_BOSS, HORDA_DURACAO_BASE, HORDA_DURACAO_ESCALA,
    SPAWN_INTERVALO_MIN, SPAWN_INTERVALO_BASE, SPAWN_INTERVALO_ESCALA,
    BOSS_HP_BASE, BOSS_HP_ESCALA,
    METEORO_HP_BASE, METEORO_HP_ESCALA,
    METEORO_ESPECIAL_HP_BASE, METEORO_ESPECIAL_HP_ESCALA,
    METEORO_PROB_ESPECIAL_MAX, METEORO_PROB_ESPECIAL_BASE, METEORO_PROB_ESPECIAL_ESCALA,
)
from src.core.tela import Tela
from src.components.jogador import Jogador
from src.components.tiros import Tiro
from src.components.inimigos import MeteoroNormal, MeteoroEspecial, FragmentoMeteoro, ImpactoTiro, Boss

pygame.init()

tela = Tela()
clock = pygame.time.Clock()

fonte_grande = pygame.font.SysFont("Arial", 60, bold=True)
fonte_media = pygame.font.SysFont("Arial", 35, bold=True)
fonte_horda = pygame.font.SysFont("Arial", 45, bold=True)
fonte_hud = pygame.font.SysFont("Arial", 18, bold=True)
fonte_hud_small = pygame.font.SysFont("Arial", 13)

todos_sprites = pygame.sprite.Group()
grupo_inimigos = pygame.sprite.Group()
grupo_tiros = pygame.sprite.Group()
grupo_tiros_inimigos = pygame.sprite.Group()

pontos = 0
vidas = VIDAS_INICIAIS
fase_boss = False
game_over = False
chefao = None
horda_atual = 0
proxima_horda = 1
pontos_inicio_horda = 0
pausa_ate = 0
mensagem_horda = ""
mensagem_ate = 0
ciclo_boss = 0
pontos_arma = 0
energia = 100.0
furia_ativa = False
furia_inicio = 0
recarrega_inicio = 0
ultimo_tiro = 0


def get_horda():
    return max(1, horda_atual)


def duracao_horda(n):
    return int(HORDA_DURACAO_BASE * (1 + HORDA_DURACAO_ESCALA * math.log(n)))


def intervalo_spawn(horda):
    return max(SPAWN_INTERVALO_MIN, int(SPAWN_INTERVALO_BASE / (1 + SPAWN_INTERVALO_ESCALA * math.log(horda))))


def hp_boss(ciclo):
    return int(BOSS_HP_BASE + BOSS_HP_ESCALA * math.log(ciclo + 1)) if ciclo > 0 else BOSS_HP_BASE


def _hud_coracao(surf, cx, cy, r, cor):
    r2 = max(1, r // 2)
    pygame.draw.circle(surf, cor, (cx - r2, cy - r2 // 2), r2)
    pygame.draw.circle(surf, cor, (cx + r2, cy - r2 // 2), r2)
    pygame.draw.polygon(surf, cor, [(cx - r, cy - r2 // 2), (cx + r, cy - r2 // 2), (cx, cy + r)])


def _hud_estrela(surf, cx, cy, ro, ri, cor):
    pts = []
    for i in range(5):
        a_o = -math.pi / 2 + i * 2 * math.pi / 5
        a_i = a_o + math.pi / 5
        pts.append((cx + ro * math.cos(a_o), cy + ro * math.sin(a_o)))
        pts.append((cx + ri * math.cos(a_i), cy + ri * math.sin(a_i)))
    pygame.draw.polygon(surf, cor, pts)


def _hud_raio(surf, cx, cy, cor):
    pygame.draw.polygon(surf, cor, [
        (cx + 3, cy - 8), (cx - 2, cy - 1), (cx + 2, cy - 1),
        (cx - 3, cy + 8), (cx + 2, cy + 1), (cx - 2, cy + 1),
    ])


def _hud_hex(surf, cx, cy, r, cor, filled=False):
    pts = [(int(cx + r * math.cos(math.pi / 6 + i * math.pi / 3)),
            int(cy + r * math.sin(math.pi / 6 + i * math.pi / 3))) for i in range(6)]
    pygame.draw.polygon(surf, cor, pts) if filled else pygame.draw.polygon(surf, cor, pts, 1)


def _barra(surf, bx, by, bw, bh, proporcao, cor, borda=False):
    pygame.draw.rect(surf, (35, 35, 35), (bx, by, bw, bh), border_radius=5)
    fill_w = int(bw * max(0.0, min(proporcao, 1.0)))
    if fill_w > 0:
        pygame.draw.rect(surf, cor, (bx, by, fill_w, bh), border_radius=5)
    if borda:
        pygame.draw.rect(surf, cor, (bx, by, bw, bh), 1, border_radius=5)


def desenhar_hud():
    surf = tela.surface
    panel = pygame.Surface((LARGURA, 60), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 160))
    surf.blit(panel, (0, 0))

    y_icon, x = 14, 12

    _hud_coracao(surf, x + 7, y_icon, 7, VERMELHO)
    t = fonte_hud.render(str(vidas), True, BRANCO)
    surf.blit(t, (x + 17, y_icon - 9))
    x += 17 + t.get_width() + 14

    _hud_estrela(surf, x + 7, y_icon, 8, 4, AMARELO)
    t = fonte_hud.render(str(pontos), True, BRANCO)
    surf.blit(t, (x + 17, y_icon - 9))
    x += 17 + t.get_width() + 14

    wlv = min(WEAPON_MAX_LV, (pontos_arma // ARMA_PONTOS_POR_NIVEL) + 1)
    lv_cor = VERMELHO if furia_ativa else VERDE
    _hud_raio(surf, x + 6, y_icon, lv_cor)
    t = fonte_hud.render(f"Lv.{wlv}", True, lv_cor)
    surf.blit(t, (x + 15, y_icon - 9))
    x += 15 + t.get_width() + 14

    if horda_atual > 0:
        label = f"BOSS {ciclo_boss + 1}" if fase_boss else f"H.{horda_atual}"
        h_cor = (255, 80, 80) if fase_boss else (180, 180, 255)
        _hud_hex(surf, x + 7, y_icon, 7, h_cor, filled=fase_boss)
        t = fonte_hud.render(label, True, h_cor)
        surf.blit(t, (x + 17, y_icon - 9))

    if furia_ativa:
        bar_cor, label_e = VERMELHO, "FURIA ATIVA  [R]"
    elif energia >= 100:
        bar_cor, label_e = VERDE, "ENERGIA PRONTA  [R]"
    else:
        bar_cor, label_e = (230, 200, 0), f"RECARREGANDO  {int(energia)}%"

    _barra(surf, 12, 37, 170, 10, energia / 100, bar_cor, borda=(furia_ativa or energia >= 100))
    surf.blit(fonte_hud_small.render(label_e, True, bar_cor), (190, 37))

    if fase_boss and chefao is not None and chefao.alive():
        bw_b, by_b = 220, 68
        bx_b = LARGURA // 2 - bw_b // 2
        _barra(surf, bx_b, by_b, bw_b, 14, chefao.vida / chefao.vida_max, VERDE)
        pygame.draw.rect(surf, VERMELHO, (bx_b, by_b, bw_b, 14), 1, border_radius=5)
        t_b = fonte_hud_small.render(f"BOSS  {chefao.vida} / {chefao.vida_max}", True, BRANCO)
        surf.blit(t_b, (bx_b + bw_b // 2 - t_b.get_width() // 2, by_b + 1))


def desenhar_game_over():
    itens = [
        (fonte_grande, "GAME OVER", VERMELHO, -100),
        (fonte_media, f"SCORE: {pontos}", BRANCO, -20),
        (fonte_media, f"HORDA: {horda_atual}", BRANCO, 30),
        (fonte_media, "R - Reiniciar", BRANCO, 80),
    ]
    for fonte, texto, cor, dy in itens:
        txt = fonte.render(texto, True, cor)
        tela.blit(txt, (LARGURA // 2 - txt.get_width() // 2, ALTURA // 2 + dy))


def renderizar(agora):
    tela.preencher(PRETO)
    if game_over:
        desenhar_game_over()
    else:
        tela.desenhar(todos_sprites)
        desenhar_hud()
        if mensagem_horda and agora < mensagem_ate:
            txt = fonte_horda.render(mensagem_horda, True, VERMELHO)
            tela.blit(txt, (LARGURA // 2 - txt.get_width() // 2, ALTURA // 2 - txt.get_height() // 2))
    tela.atualizar()


def spawn_inimigo():
    hp_v = METEORO_HP_BASE + int(METEORO_HP_ESCALA * math.log(horda_atual + 1))
    hp_e = METEORO_ESPECIAL_HP_BASE + int(METEORO_ESPECIAL_HP_ESCALA * math.log(horda_atual + 1))
    prob = min(METEORO_PROB_ESPECIAL_MAX, METEORO_PROB_ESPECIAL_BASE + METEORO_PROB_ESPECIAL_ESCALA * math.log(horda_atual + 1))
    novo = MeteoroEspecial(hp_e, get_horda) if random.random() < prob else MeteoroNormal(hp_v, get_horda)
    todos_sprites.add(novo)
    grupo_inimigos.add(novo)


def atirar(agora):
    global ultimo_tiro
    if not (pygame.key.get_pressed()[pygame.K_SPACE] and agora - ultimo_tiro >= COOLDOWN_TIRO):
        return
    ultimo_tiro = agora
    num = min(WEAPON_MAX_LV, (pontos_arma // ARMA_PONTOS_POR_NIVEL) + 1)
    dano_at = 2 if pontos_arma >= ARMA_PONTOS_DANO2 else 1
    if furia_ativa:
        dano_at = int(dano_at * FURIA_MULT)
    esc_at = 1 + (0.5 * (min(pontos_arma, ARMA_PONTOS_ESCALA_MAX) // ARMA_PONTOS_ESCALA_PASSO))
    for i in range(num):
        off = (i - (num - 1) / 2) * 20
        t = Tiro(player.rect.centerx + off, player.rect.top, dano_at, esc_at, furia=furia_ativa)
        todos_sprites.add(t)
        grupo_tiros.add(t)


def atualizar_furia(agora):
    global furia_ativa, energia, recarrega_inicio
    if furia_ativa:
        elapsed = agora - furia_inicio
        energia = max(0.0, 100.0 - elapsed * 100.0 / FURIA_DURACAO)
        if elapsed >= FURIA_DURACAO:
            furia_ativa = False
            recarrega_inicio = agora
            energia = 0.0
    elif recarrega_inicio > 0:
        energia = min(100.0, (agora - recarrega_inicio) * 100.0 / FURIA_RECARGA)


def iniciar_boss():
    global fase_boss, chefao
    fase_boss = True
    for s in grupo_inimigos:
        s.kill()
    chefao = Boss(todos_sprites, grupo_tiros_inimigos, hp_boss(ciclo_boss))
    todos_sprites.add(chefao)
    grupo_inimigos.add(chefao)


def agendar_proxima_horda(agora):
    global pausa_ate, mensagem_horda, mensagem_ate
    pausa_ate = agora + 2000
    mensagem_horda = f"INICIANDO HORDA {proxima_horda}"
    mensagem_ate = agora + 4000


def ativar_horda():
    global pausa_ate, horda_atual, proxima_horda, pontos_inicio_horda
    pausa_ate = 0
    horda_atual = proxima_horda
    proxima_horda += 1
    pontos_inicio_horda = pontos
    pygame.time.set_timer(SPAWN_TIMER, intervalo_spawn(horda_atual))


def atualizar_hordas(agora):
    if fase_boss:
        return
    horda_completa = horda_atual == 0 or pontos >= pontos_inicio_horda + duracao_horda(horda_atual)
    if horda_completa and pausa_ate == 0:
        if horda_atual > 0 and horda_atual % HORDAS_POR_BOSS == 0:
            iniciar_boss()
        else:
            agendar_proxima_horda(agora)
    if pausa_ate > 0 and agora >= pausa_ate:
        ativar_horda()


def destruir_meteoro(inimigo):
    global pontos, pontos_arma
    if isinstance(inimigo, MeteoroNormal):
        for _ in range(random.randint(4, 7)):
            todos_sprites.add(FragmentoMeteoro(inimigo.rect.centerx, inimigo.rect.centery, inimigo.tom))
    ganho = PONTOS_POR_METEORO_ESPECIAL if isinstance(inimigo, MeteoroEspecial) else PONTOS_POR_METEORO_NORMAL
    pontos += ganho
    pontos_arma += ganho
    inimigo.kill()


def matar_boss(agora):
    global fase_boss, ciclo_boss, pontos_arma
    chefao.kill()
    fase_boss = False
    ciclo_boss += 1
    pontos_arma = 0
    agendar_proxima_horda(agora)


def processar_colisoes(agora):
    for inimigo, balas in pygame.sprite.groupcollide(grupo_inimigos, grupo_tiros, False, True).items():
        total_dano = sum(b.dano for b in balas)
        if isinstance(inimigo, Boss):
            inimigo.vida -= total_dano
            if inimigo.vida <= 0:
                matar_boss(agora)
        else:
            inimigo.vida -= total_dano
            if isinstance(inimigo, (MeteoroNormal, MeteoroEspecial)):
                for b in balas:
                    todos_sprites.add(ImpactoTiro(b.rect.centerx, b.rect.centery))
            if inimigo.vida <= 0:
                destruir_meteoro(inimigo)
            elif isinstance(inimigo, (MeteoroNormal, MeteoroEspecial)):
                inimigo.atualizar_visual()

    for p, balas in pygame.sprite.groupcollide(grupo_tiros_inimigos, grupo_tiros, False, True).items():
        if hasattr(p, 'vida'):
            p.vida -= sum(b.dano for b in balas)
            if p.vida <= 0:
                p.kill()


def verificar_hit_jogador(agora):
    global vidas, game_over
    if player.invencivel:
        return
    tocou = pygame.sprite.spritecollideany(player, grupo_inimigos) or \
            pygame.sprite.spritecollideany(player, grupo_tiros_inimigos)
    if not tocou:
        return
    vidas -= 1
    if vidas <= 0:
        game_over = True
    else:
        player.invencivel = True
        player.tempo_invencivel = agora + INVENCIVEL_DURACAO


def resetar_jogo():
    global pontos, vidas, fase_boss, game_over, player, chefao
    global horda_atual, proxima_horda, pontos_inicio_horda
    global pausa_ate, mensagem_horda, mensagem_ate, ciclo_boss, pontos_arma
    global energia, furia_ativa, furia_inicio, recarrega_inicio, ultimo_tiro

    pontos = 0
    vidas = VIDAS_INICIAIS
    fase_boss = False

    game_over = False
    chefao = None
    horda_atual = 0
    proxima_horda = 1
    pontos_inicio_horda = 0
    pausa_ate = 0
    mensagem_horda = ""
    mensagem_ate = 0

    ciclo_boss = 0
    pontos_arma = 0
    energia = 100.0
    furia_ativa = False
    furia_inicio = 0
    recarrega_inicio = 0
    ultimo_tiro = 0

    todos_sprites.empty()
    grupo_inimigos.empty()
    grupo_tiros.empty()
    grupo_tiros_inimigos.empty()
    player = Jogador()
    todos_sprites.add(player)


player = Jogador()
todos_sprites.add(player)

SPAWN_TIMER = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_TIMER, 1000)

rodando = True
while rodando:
    clock.tick(FPS)
    agora = pygame.time.get_ticks()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        if evento.type == pygame.KEYDOWN:
            if game_over:
                if evento.key == pygame.K_r:
                    resetar_jogo()
            elif evento.key == pygame.K_r and energia >= 100 and not furia_ativa:
                furia_ativa = True
                furia_inicio = agora
        if not game_over and evento.type == SPAWN_TIMER and not fase_boss and horda_atual > 0 and pausa_ate == 0:
            spawn_inimigo()

    if not game_over:
        atualizar_furia(agora)
        atirar(agora)
        atualizar_hordas(agora)
        todos_sprites.update()
        processar_colisoes(agora)
        verificar_hit_jogador(agora)

    renderizar(agora)

pygame.quit()
