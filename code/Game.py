import pygame
import os
from code.Menu import Menu
from code.Level import Level
from code.Score import Score
from code.DBProxy import DBProxy
from code.AssetManager import AssetManager
from code.Const import (WIN_WIDTH, WIN_HEIGHT, WIN_TITLE, FPS, BACKGROUND_COLOR,
                        GAME_STATE_MENU, GAME_STATE_PLAYING, GAME_STATE_GAME_OVER,
                        GAME_STATE_WIN, DIFFICULTY_NORMAL, MUSIC_BACKGROUND,
                        MUSIC_MENU, C_WHITE, C_RED, DB_PATH)


class Game:
    """Classe mestre que controla as transições entre telas e o fluxo do jogo."""
    def __init__(self):
        """Inicializa o Pygame, a janela, o áudio e os gerenciadores de dados."""
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error as e:
            # Caso o computador não tenha saída de áudio, desativa o som para evitar erro fatal
            print(f"⚠ Aviso: Não foi possível inicializar áudio: {e}")
            os.environ['SDL_AUDIODRIVER'] = 'dummy'

        self.window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        pygame.display.set_caption(WIN_TITLE)
        self.clock = pygame.time.Clock()

        self.running = True
        self.state = GAME_STATE_MENU
        self.current_level = 1
        self.difficulty = DIFFICULTY_NORMAL

        # Configura o caminho das pastas e inicia Banco de Dados e Gerenciador de Arquivos
        assets_path = os.path.join(os.path.dirname(__file__), '..', 'assets')
        self.asset_manager = AssetManager(assets_path)
        self.db_proxy = DBProxy()

        self.menu = None
        self.level = None

        print("✓ Jogo inicializado com sucesso!")

    def run(self):
        """Loop principal que decide qual estado (menu, jogando, fim) deve ser executado."""
        while self.running:
            if self.state == GAME_STATE_MENU:
                self._run_menu()
            elif self.state == GAME_STATE_PLAYING:
                self._run_level()
            elif self.state == GAME_STATE_GAME_OVER:
                self._run_game_over()
            elif self.state == GAME_STATE_WIN:
                self._run_win()

        # Ao sair do loop, limpa os recursos da memória
        self._cleanup()

    def _run_menu(self):
        """Gerencia o menu inicial e as escolhas do jogador (Novo Jogo, Ranking ou Sair)."""
        self.asset_manager.play_music(MUSIC_MENU, loops=-1)
        self.menu = Menu(self.window)
        option_id = self.menu.run()

        if option_id == -1: # Fechar janela
            self.running = False
        elif option_id == 0:  # Iniciar novo jogo
            self.current_level = 1
            self.state = GAME_STATE_PLAYING
        elif option_id == 1:  # Ver recordes
            self._show_high_scores()
        elif option_id == 2:  # Sair do jogo
            self.running = False

    def _run_level(self):
        """Cria e executa a fase atual, trocando a música e gerenciando o resultado (vitória/derrota)."""
        self.asset_manager.stop_music()
        self.asset_manager.play_music(MUSIC_BACKGROUND, loops=-1)

        # Instancia o nível com as configurações atuais
        self.level = Level(
            self.window,
            self.current_level,
            self.difficulty,
            self.db_proxy
        )
        result = self.level.run()

        # Decide para qual estado ir baseado no resultado retornado pela classe Level
        if result == 'game_over':
            self.state = GAME_STATE_GAME_OVER
        elif result in ['next_level', 'win']:
            self.current_level += 1
            self.state = GAME_STATE_PLAYING
        else:
            self.state = GAME_STATE_MENU

    def _run_game_over(self):
        """Exibe a tela de derrota com a pontuação e aguarda comando para reiniciar ou sair."""
        final_score = self.level.mediator.get_score() if self.level else 0
        Score(DB_PATH) # Sincroniza o módulo de pontuação

        waiting = True
        font_big = pygame.font.Font(None, 80)
        font_medium = pygame.font.Font(None, 50)
        font_small = pygame.font.Font(None, 32)

        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE: # Reinicia o progresso
                        self.current_level = 1
                        self.state = GAME_STATE_PLAYING
                        waiting = False
                    elif event.key == pygame.K_ESCAPE: # Volta ao menu
                        self.state = GAME_STATE_MENU
                        waiting = False

            # Desenha o fundo da última fase com uma camada preta semitransparente por cima
            if self.level:
                self.level.draw()

            overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.window.blit(overlay, (0, 0))

            # Renderiza as mensagens de Game Over e Pontuação
            text_game_over = font_big.render("GAME OVER", True, C_RED)
            text_score = font_medium.render(f"PONTUAÇÃO FINAL: {final_score}", True, C_WHITE)
            text_retry = font_small.render("ESPAÇO para Reiniciar | ESC para Menu", True, (200, 200, 200))

            self.window.blit(text_game_over, text_game_over.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 80)))
            self.window.blit(text_score, text_score.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2)))
            self.window.blit(text_retry, text_retry.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 100)))

            pygame.display.flip()
            self.clock.tick(FPS)

    def _run_win(self):
        """Tela de transição exibida ao concluir um nível com sucesso."""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.current_level += 1
                        self.state = GAME_STATE_PLAYING
                        waiting = False

            if self.level:
                self.level.draw()

            # Camada visual para destacar a mensagem de vitória
            overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.window.blit(overlay, (0, 0))

            font = pygame.font.Font(None, 60)
            txt = font.render("NÍVEL CONCLUÍDO!", True, (0, 255, 0))
            self.window.blit(txt, txt.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2)))

            pygame.display.flip()
            self.clock.tick(FPS)

    def _show_high_scores(self):
        """Busca as melhores pontuações salvas e desenha a lista de recordes na tela."""
        scores = self.db_proxy.get_high_scores(limit=10)
        font_title = pygame.font.Font(None, 72)
        font_score = pygame.font.Font(None, 32)

        showing = True
        while showing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    showing = False
                if event.type == pygame.KEYDOWN: # Sai da tela com qualquer tecla
                    showing = False

            self.window.fill(BACKGROUND_COLOR)
            title_text = font_title.render("HIGH SCORES", True, (0, 255, 255))
            self.window.blit(title_text, title_text.get_rect(center=(WIN_WIDTH // 2, 50)))

            # Lista cada recorde encontrado no banco de dados
            y_offset = 150
            for i, (name, score, level, date) in enumerate(scores):
                txt = font_score.render(f"{i + 1}. {name} - {score} Pts (Lvl {level})", True, C_WHITE)
                self.window.blit(txt, (WIN_WIDTH // 2 - 120, y_offset))
                y_offset += 40

            pygame.display.flip()
            self.clock.tick(FPS)

        self.state = GAME_STATE_MENU

    def _cleanup(self):
        """Fecha a conexão com o banco de dados e libera o áudio e memória antes de fechar."""
        self.db_proxy.close()
        self.asset_manager.unload_all()
        pygame.quit()