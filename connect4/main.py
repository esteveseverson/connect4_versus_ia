import math
import random
import sys
from threading import Timer

import numpy as np
import pygame

# Constantes
LINHAS = 6
COLUNAS = 7

TURNO_JOGADOR = 0
TURNO_IA = 1

PECA_JOGADOR = 1
PECA_IA = 2

AZUL = (0, 0, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
AMARELO = (255, 255, 0)


class Tabuleiro:
    def __init__(self):
        self.tabuleiro = np.zeros((LINHAS, COLUNAS))

    def soltar_peca(self, linha, coluna, peca):
        self.tabuleiro[linha][coluna] = peca

    def validar_movimento(self, coluna):
        return self.tabuleiro[0][coluna] == 0

    def obter_proxima_linha(self, coluna):
        for linha in range(LINHAS - 1, -1, -1):
            if self.tabuleiro[linha][coluna] == 0:
                return linha

    def movimento_ganhador(self, player) -> bool:
        # Verificar horizontal
        for linha in range(LINHAS):
            for coluna in range(COLUNAS - 3):
                if all(
                    self.tabuleiro[linha][coluna + i] == player for i in range(4)
                ):
                    return True

        # Verificar vertical
        for linha in range(LINHAS - 3):
            for coluna in range(COLUNAS):
                if all(
                    self.tabuleiro[linha + i][coluna] == player for i in range(4)
                ):
                    return True

        # Verificar diagonal principal \
        for linha in range(LINHAS - 3):
            for coluna in range(COLUNAS - 3):
                if all(
                    self.tabuleiro[linha + i][coluna + i] == player for i in range(4)
                ):
                    return True

        # Verificar diagonal secundaria /
        for linha in range(3, LINHAS):
            for coluna in range(COLUNAS - 3):
                if all(
                    self.tabuleiro[linha - i][coluna + i] == player for i in range(4)
                ):
                    return True

        return False

    def get_movimentos_validos(self):
        return [
            coluna for coluna in range(COLUNAS) if self.validar_movimento(coluna)
        ]


class IA:
    def __init__(self, profundidade=4, usar_poda=False):
        self.profundidade = profundidade
        self.usar_poda = usar_poda

    @staticmethod
    def avaliar_janela(janela, peca):
        peca_oponente = PECA_JOGADOR if peca == PECA_IA else PECA_IA
        pontuacao = 0
        if janela.count(peca) == 4:
            pontuacao += 100
        elif janela.count(peca) == 3 and janela.count(0) == 1:
            pontuacao += 5
        elif janela.count(peca) == 2 and janela.count(0) == 2:
            pontuacao += 2

        if janela.count(peca_oponente) == 3 and janela.count(0) == 1:
            pontuacao -= 4

        return pontuacao

    def avaliar_tabuleiro(self, tabuleiro, peca):
        pontuacao = 0
        # Coluna central
        coluna_central = [int(i) for i in list(tabuleiro[:, COLUNAS // 2])]
        pontuacao += coluna_central.count(peca) * 6

        # Linhas
        for r in range(LINHAS):
            linha_array = [int(i) for i in list(tabuleiro[r, :])]
            for c in range(COLUNAS - 3):
                janela = linha_array[c : c + 4]
                pontuacao += self.avaliar_janela(janela, peca)

        # Colunas
        for c in range(COLUNAS):
            coluna_array = [int(i) for i in list(tabuleiro[:, c])]
            for r in range(LINHAS - 3):
                janela = coluna_array[r : r + 4]
                pontuacao += self.avaliar_janela(janela, peca)

        # Diagonais positivas
        for r in range(3, LINHAS):
            for c in range(COLUNAS - 3):
                janela = [tabuleiro[r - i][c + i] for i in range(4)]
                pontuacao += self.avaliar_janela(janela, peca)

        # Diagonais negativas
        for r in range(3, LINHAS):
            for c in range(3, COLUNAS):
                janela = [tabuleiro[r - i][c - i] for i in range(4)]
                pontuacao += self.avaliar_janela(janela, peca)

        return pontuacao

    def minimax(self, tabuleiro_obj, profundidade, alfa, beta, jogador_maximizador):
        locais_validos = tabuleiro_obj.get_movimentos_validos()
        terminal = (
            tabuleiro_obj.movimento_ganhador(PECA_JOGADOR)
            or tabuleiro_obj.movimento_ganhador(PECA_IA)
            or not locais_validos
        )

        if profundidade == 0 or terminal:
            if terminal:
                if tabuleiro_obj.movimento_ganhador(PECA_IA):
                    return None, 10000000
                elif tabuleiro_obj.movimento_ganhador(PECA_JOGADOR):
                    return None, -10000000
                else:
                    return None, 0
            else:
                return None, self.avaliar_tabuleiro(tabuleiro_obj.tabuleiro, PECA_IA)

        if jogador_maximizador:
            valor = -math.inf
            coluna = random.choice(locais_validos)
            for col in locais_validos:
                linha = tabuleiro_obj.obter_proxima_linha(col)
                copia_tabuleiro = Tabuleiro()
                copia_tabuleiro.tabuleiro = np.copy(tabuleiro_obj.tabuleiro)
                copia_tabuleiro.soltar_peca(linha, col, PECA_IA)
                novo_valor = self.minimax(
                    copia_tabuleiro, profundidade - 1, alfa, beta, False
                )[1]
                if novo_valor > valor:
                    valor = novo_valor
                    coluna = col
                if self.usar_poda:
                    alfa = max(alfa, valor)
                    if alfa >= beta:
                        break
            return coluna, valor
        else:
            valor = math.inf
            coluna = random.choice(locais_validos)
            for col in locais_validos:
                linha = tabuleiro_obj.obter_proxima_linha(col)
                copia_tabuleiro = Tabuleiro()
                copia_tabuleiro.tabuleiro = np.copy(tabuleiro_obj.tabuleiro)
                copia_tabuleiro.soltar_peca(linha, col, PECA_JOGADOR)
                novo_valor = self.minimax(
                    copia_tabuleiro, profundidade - 1, alfa, beta, True
                )[1]
                if novo_valor < valor:
                    valor = novo_valor
                    coluna = col
                if self.usar_poda:
                    beta = min(beta, valor)
                    if alfa >= beta:
                        break
            return coluna, valor


class Jogo:
    def __init__(self):
        self.tabuleiro = Tabuleiro()
        self.ia = IA(profundidade=4, usar_poda=False)
        self.jogo_acabou = False
        self.em_andamento = True
        self.turno = random.randint(TURNO_JOGADOR, TURNO_IA)

        pygame.init()
        self.TAMANHO_QUADRADO = 100
        self.largura = COLUNAS * self.TAMANHO_QUADRADO
        self.altura = (LINHAS + 1) * self.TAMANHO_QUADRADO
        self.raio_circulo = int(self.TAMANHO_QUADRADO / 2 - 5)
        self.tela = pygame.display.set_mode((self.largura, self.altura))
        self.fonte = pygame.font.SysFont('monospace', 75)
        self.desenhar_tabuleiro()

    def desenhar_tabuleiro(self):
        for c in range(COLUNAS):
            for r in range(LINHAS):
                pygame.draw.rect(
                    self.tela,
                    AZUL,
                    (
                        c * self.TAMANHO_QUADRADO,
                        r * self.TAMANHO_QUADRADO + self.TAMANHO_QUADRADO,
                        self.TAMANHO_QUADRADO,
                        self.TAMANHO_QUADRADO,
                    ),
                )
                cor = PRETO
                if self.tabuleiro.tabuleiro[r][c] == PECA_JOGADOR:
                    cor = VERMELHO
                elif self.tabuleiro.tabuleiro[r][c] == PECA_IA:
                    cor = AMARELO
                pygame.draw.circle(
                    self.tela,
                    cor,
                    (
                        int(c * self.TAMANHO_QUADRADO + self.TAMANHO_QUADRADO / 2),
                        int(
                            r * self.TAMANHO_QUADRADO
                            + self.TAMANHO_QUADRADO
                            + self.TAMANHO_QUADRADO / 2
                        ),
                    ),
                    self.raio_circulo,
                )
        pygame.display.update()

    def terminar_jogo(self):
        self.jogo_acabou = True
        print('Jogo terminado!')

    def loop(self):
        while not self.jogo_acabou:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    sys.exit()
                if evento.type == pygame.MOUSEMOTION and self.em_andamento:
                    pygame.draw.rect(
                        self.tela, PRETO, (0, 0, self.largura, self.TAMANHO_QUADRADO)
                    )
                    xpos = pygame.mouse.get_pos()[0]
                    if self.turno == TURNO_JOGADOR:
                        pygame.draw.circle(
                            self.tela,
                            VERMELHO,
                            (xpos, int(self.TAMANHO_QUADRADO / 2)),
                            self.raio_circulo,
                        )

                if evento.type == pygame.MOUSEBUTTONDOWN and self.em_andamento:
                    pygame.draw.rect(
                        self.tela, PRETO, (0, 0, self.largura, self.TAMANHO_QUADRADO)
                    )
                    if self.turno == TURNO_JOGADOR:
                        xpos = evento.pos[0]
                        coluna = int(math.floor(xpos / self.TAMANHO_QUADRADO))
                        if self.tabuleiro.validar_movimento(coluna):
                            linha = self.tabuleiro.obter_proxima_linha(coluna)
                            self.tabuleiro.soltar_peca(linha, coluna, PECA_JOGADOR)
                            if self.tabuleiro.movimento_ganhador(PECA_JOGADOR):
                                print('JOGADOR VENCEU')
                                mensagem = self.fonte.render(
                                    'JOGADOR VENCEU', 1, VERMELHO
                                )
                                self.tela.blit(mensagem, (40, 10))
                                self.em_andamento = False
                                Timer(3.0, self.terminar_jogo).start()
                        self.desenhar_tabuleiro()
                        self.turno = (self.turno + 1) % 2

            if self.turno == TURNO_IA and not self.jogo_acabou and self.em_andamento:
                coluna, _ = self.ia.minimax(
                    self.tabuleiro, self.ia.profundidade, -math.inf, math.inf, True
                )
                if self.tabuleiro.validar_movimento(coluna):
                    pygame.time.wait(500)
                    linha = self.tabuleiro.obter_proxima_linha(coluna)
                    self.tabuleiro.soltar_peca(linha, coluna, PECA_IA)
                    if self.tabuleiro.movimento_ganhador(PECA_IA):
                        print('IA VENCEU!')
                        mensagem = self.fonte.render('IA VENCEU!', 1, AMARELO)
                        self.tela.blit(mensagem, (40, 10))
                        self.em_andamento = False
                        Timer(3.0, self.terminar_jogo).start()
                self.desenhar_tabuleiro()
                self.turno = (self.turno + 1) % 2


if __name__ == '__main__':
    jogo = Jogo()
    jogo.loop()
