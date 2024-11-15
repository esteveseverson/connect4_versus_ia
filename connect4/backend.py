import math


class Connect4:
    def __init__(
        self,
        linhas: int = 7,
        colunas: int = 8,
        ply: int = 4,
        usar_alpha_beta: bool = False,
    ):
        self.linhas = linhas
        self.colunas = colunas
        self.tabuleiro = [[0 for _ in range(colunas)] for _ in range(linhas)]
        self.ply = ply
        self.usar_alpha_beta = usar_alpha_beta
        self.player_atual = 1  # 1 para jogador, -1 para IA

    def desenhar_tabuleiro(self):
        for linha in self.tabuleiro:
            print('  '.join(map(str, linha)))
        print('\n')

    def validar_movimento(self, coluna) -> bool:
        return self.tabuleiro[0][coluna] == 0

    def get_movimentos_validos(self) -> list[int]:
        return [
            coluna
            for coluna in range(self.colunas)
            if self.validar_movimento(coluna)
        ]

    def realizar_jogada(self, coluna, player):
        for linha in reversed(self.tabuleiro):
            if linha[coluna] == 0:
                linha[coluna] = player
                return

    def retornar_movimento(self, coluna):
        for linha in self.tabuleiro:
            if linha[coluna] != 0:
                linha[coluna] = 0
                return

    def movimento_ganhador(self, player) -> bool:
        # Verificar horizontal
        for linha in range(self.linhas):
            for coluna in range(self.colunas - 3):
                if all(
                    self.tabuleiro[linha][coluna + i] == player for i in range(4)
                ):
                    return True

        # Verificar vertical
        for linha in range(self.linhas - 3):
            for coluna in range(self.colunas):
                if all(
                    self.tabuleiro[linha + i][coluna] == player for i in range(4)
                ):
                    return True

        # Verificar diagonal principal \
        for linha in range(self.linhas - 3):
            for coluna in range(self.colunas - 3):
                if all(
                    self.tabuleiro[linha + i][coluna + i] == player for i in range(4)
                ):
                    return True

        # Verificar diagonal secundaria /
        for linha in range(3, self.linhas):
            for coluna in range(self.colunas - 3):
                if all(
                    self.tabuleiro[linha - i][coluna + i] == player for i in range(4)
                ):
                    return True

        return False

    @staticmethod
    def avaliar_janela(janela: list[int]) -> int | float:
        JOGADA_GANHADORA = 4
        CELULAS_LIVRES = 1

        pontos = 0
        ia = -1
        jogador = 1

        # Casos de vitória
        if janela.count(ia) == JOGADA_GANHADORA:
            return math.inf

        if janela.count(jogador) == JOGADA_GANHADORA:
            return -math.inf

        # Casos de 3 alinhados
        if janela.count(jogador) == (
            JOGADA_GANHADORA - 1 and janela.count(0) == CELULAS_LIVRES
        ):
            pontos -= 1000

        if janela.count(ia) == (
            JOGADA_GANHADORA - 1 and janela.count(0) == CELULAS_LIVRES
        ):
            pontos += 500

        # Casos de 2 alinhados
        if janela.count(ia) == (
            JOGADA_GANHADORA - 2 and janela.count(0) >= CELULAS_LIVRES + 1
        ):
            pontos += 50

        if janela.count(jogador) == (
            JOGADA_GANHADORA - 2 and janela.count(0) >= CELULAS_LIVRES + 1
        ):
            pontos -= 200

        return pontos

    def avaliar_tabuleiro(self) -> int:
        pontos = 0

        coluna_central = self.colunas // 2
        centro = [
            self.tabuleiro[linha][coluna_central] for linha in range(self.linhas)
        ]
        pontos += centro.count(-1) * 5

        # avaliando linhas
        for linha in range(self.linhas):
            for coluna in range(self.colunas - 3):
                janela = [self.tabuleiro[linha][coluna + i] for i in range(4)]
                pontos += self.avaliar_janela(janela)

        # avaliando colunas
        for coluna in range(self.colunas):
            for linha in range(self.linhas - 3):
                janela = [self.tabuleiro[linha + i][coluna] for i in range(4)]
                pontos += self.avaliar_janela(janela)

        # avaliando as diagonais \
        for linha in range(self.linhas - 3):
            for coluna in range(self.colunas - 3):
                janela = [self.tabuleiro[linha + i][coluna + i] for i in range(4)]
                pontos += self.avaliar_janela(janela)

        # avaliando as diagonais /
        for linha in range(3, self.linhas):
            for coluna in range(self.colunas - 3):
                janela = [self.tabuleiro[linha - i][coluna + i] for i in range(4)]
                pontos += self.avaliar_janela(janela)

        return pontos

    def minimax(self, profundidade, alpha, beta, maximizar_jogador):
        movimentos_validos = self.get_movimentos_validos()
        if profundidade == 0 or not movimentos_validos:
            return self.avaliar_tabuleiro(), None

        if maximizar_jogador:
            valor_maximo = -math.inf
            melhor_movimento = None

            for coluna in movimentos_validos:
                self.realizar_jogada(coluna, 1)
                eval = self.minimax(profundidade - 1, alpha, beta, False)[0]
                self.retornar_movimento(coluna)

                if eval > valor_maximo:
                    valor_maximo = eval
                    melhor_movimento = coluna

                alpha = max(alpha, eval)
                if self.usar_alpha_beta and beta <= alpha:
                    break
            return valor_maximo, melhor_movimento

        if not maximizar_jogador:
            valor_minimo = math.inf
            melhor_movimento = None

            for coluna in movimentos_validos:
                self.realizar_jogada(coluna, -1)
                eval = self.minimax(profundidade - 1, alpha, beta, True)[0]
                self.retornar_movimento(coluna)

                if eval < valor_minimo:
                    valor_minimo = eval
                    melhor_movimento = coluna
                beta = min(beta, eval)

                if self.usar_alpha_beta and beta <= alpha:
                    break

            return valor_minimo, melhor_movimento

    def turno_ia(self):
        movimentos_validos = self.get_movimentos_validos()

        # Prioridade: bloquear vitória do jogador
        for coluna in movimentos_validos:
            self.realizar_jogada(coluna, 1)
            if self.movimento_ganhador(1):
                self.retornar_movimento(coluna)
                self.realizar_jogada(coluna, -1)
                return

            self.retornar_movimento(coluna)

        # Prioriodade secundária: Bloquear ameaças críticas
        maior_ameaca = None
        melhor_pontuacao = -math.inf

        for coluna in movimentos_validos:
            self.realizar_jogada(coluna, -1)
            pontuacao_atual = self.avaliar_tabuleiro()
            self.retornar_movimento(coluna)

            if pontuacao_atual > melhor_pontuacao:
                melhor_pontuacao = pontuacao_atual
                maior_ameaca = coluna

        if maior_ameaca is not None:
            self.realizar_jogada(maior_ameaca, -1)
            return

        # Caso contrário, faça o melhor movimento da IA
        _, melhor_movimento = self.minimax(self.ply, -math.inf, math.inf, True)
        if melhor_movimento is not None:
            self.realizar_jogada(melhor_movimento, -1)

    def turno_humano(self, coluna):
        if self.validar_movimento(coluna):
            self.realizar_jogada(coluna, 1)

    def jogar(self):
        while True:
            self.desenhar_tabuleiro()
            if self.player_atual == 1:
                coluna = int(input(f'escolha a coluna (1-{self.colunas}): ')) - 1
                if not self.validar_movimento(coluna):
                    print('Movimento inválido! Realize outro.')
                    continue
                self.turno_humano(coluna)
            else:
                self.turno_ia()

            if self.movimento_ganhador(self.player_atual):
                self.desenhar_tabuleiro()
                vencedor = str(
                    'O jogador ganhou' if self.player_atual == 1 else 'A I.A. venceu'
                )
                print(vencedor)
                break

            self.player_atual *= -1


game = Connect4(ply=4)
game.jogar()
