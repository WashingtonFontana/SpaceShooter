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
    """
    Classe principal que orquestra todo o jogo, gerenciando estados e transições.
    """

    def __init__(self):
        """Inicializa o motor do jogo e os recursos básicos."""
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"⚠ Aviso: Não foi possível inicializar áudio: {e}")
            os.environ['SDL_AUDIODRIVER'] = 'dummy'

        self.window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        pygame.display.set_caption(WIN_TITLE)
        self.clock = pygame.time.Clock()

        self.running = True
        self.state = GAME_STATE_MENU
        self.current_level = 1
        self.difficulty = DIFFICULTY_NORMAL

        # Gerenciadores de recursos e banco de dados
        assets_path = os.path.join(os.path.dirname(__file__), '..', 'assets')
        self.asset_manager = AssetManager(assets_path)
        self.db_proxy = DBProxy()

        self.menu = None
        self.level = None

        print("✓ Jogo inicializado com sucesso!")

    def run(self):
        """Loop mestre que alterna entre os estados do jogo."""
        while self.running:
            if self.state == GAME_STATE_MENU:
                self._run_menu()
            elif self.state == GAME_STATE_PLAYING:
                self._run_level()
            elif self.state == GAME_STATE_GAME_OVER:
                self._run_game_over()
            elif self.state == GAME_STATE_WIN:
                self._run_win()

        self._cleanup()

    def _run_menu(self):
        """Gerencia a exibição e interação do menu principal."""
        self.asset_manager.play_music(MUSIC_MENU, loops=-1)
        self.menu = Menu(self.window)
        option_id = self.menu.run()

        if option_id == -1:
            self.running = False
        elif option_id == 0:  # NEW GAME
            self.current_level = 1
            self.state = GAME_STATE_PLAYING
        elif option_id == 1:  # HIGH SCORES
            self._show_high_scores()
        elif option_id == 2:  # EXIT
            self.running = False

    def _run_level(self):
        """Inicia e processa um nível de combate."""
        self.asset_manager.stop_music()
        self.asset_manager.play_music(MUSIC_BACKGROUND, loops=-1)

        self.level = Level(
            self.window,
            self.current_level,
            self.difficulty,
            self.db_proxy
        )
        result = self.level.run()

        if result == 'game_over':
            self.state = GAME_STATE_GAME_OVER
        elif result in ['next_level', 'win']:
            self.current_level += 1
            self.state = GAME_STATE_PLAYING
        else:
            self.state = GAME_STATE_MENU

    def _run_game_over(self):
        """
        Tela de derrota: Exibe a pontuação final e permite reiniciar com ESPAÇO.
        """
        print("▶ Processando fim de jogo...")

        final_score = self.level.mediator.get_score() if self.level else 0

        # Chama a classe Score apenas para garantir o carregamento do módulo
        # Removida a variável 'score_manager' para eliminar o aviso de não utilizada.
        Score(DB_PATH)

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
                    if event.key == pygame.K_SPACE:
                        # Reinicia o progresso do jogo
                        self.current_level = 1
                        self.state = GAME_STATE_PLAYING
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GAME_STATE_MENU
                        waiting = False

            if self.level:
                self.level.draw()

            overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.window.blit(overlay, (0, 0))

            # Renderização da interface de texto
            text_game_over = font_big.render("GAME OVER", True, C_RED)
            text_score = font_medium.render(f"PONTUAÇÃO FINAL: {final_score}", True, C_WHITE)
            text_retry = font_small.render("ESPAÇO para Reiniciar | ESC para Menu", True, (200, 200, 200))

            self.window.blit(text_game_over, text_game_over.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 80)))
            self.window.blit(text_score, text_score.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2)))
            self.window.blit(text_retry, text_retry.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 100)))

            pygame.display.flip()
            self.clock.tick(FPS)

    def _run_win(self):
        """Tela de vitória entre níveis."""
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

            overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.window.blit(overlay, (0, 0))

            font = pygame.font.Font(None, 60)
            txt = font.render("NÍVEL CONCLUÍDO!", True, (0, 255, 0))
            self.window.blit(txt, txt.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2)))

            pygame.display.flip()
            self.clock.tick(FPS)

    def _show_high_scores(self):
        """Busca no banco de dados e exibe o ranking."""
        scores = self.db_proxy.get_high_scores(limit=10)
        font_title = pygame.font.Font(None, 72)
        font_score = pygame.font.Font(None, 32)

        showing = True
        while showing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    showing = False
                if event.type == pygame.KEYDOWN:
                    showing = False

            self.window.fill(BACKGROUND_COLOR)
            title_text = font_title.render("HIGH SCORES", True, (0, 255, 255))
            self.window.blit(title_text, title_text.get_rect(center=(WIN_WIDTH // 2, 50)))

            y_offset = 150
            for i, (name, score, level, date) in enumerate(scores):
                txt = font_score.render(f"{i + 1}. {name} - {score} Pts (Lvl {level})", True, C_WHITE)
                self.window.blit(txt, (WIN_WIDTH // 2 - 120, y_offset))
                y_offset += 40

            pygame.display.flip()
            self.clock.tick(FPS)

        self.state = GAME_STATE_MENU

    def _cleanup(self):
        """Finaliza recursos de banco de dados e assets."""
        self.db_proxy.close()
        self.asset_manager.unload_all()
        pygame.quit()