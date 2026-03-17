import pygame

from src.core.constants import LARGURA, ALTURA, TITULO


class Tela:
    def __init__(self, largura: int = LARGURA, altura: int = ALTURA):
        self._largura = largura
        self._altura = altura
        self.surface = pygame.display.set_mode((largura, altura))
        pygame.display.set_caption(TITULO)

    def preencher(self, cor):
        self.surface.fill(cor)

    def desenhar(self, grupo):
        grupo.draw(self.surface)

    def blit(self, surface, pos):
        self.surface.blit(surface, pos)

    def atualizar(self):
        pygame.display.flip()
