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
                        MUSIC_MENU)


class Game:
    """
    Classe principal que orquestra todo o jogo.

    Atributos:
        window (pygame.Surface): Janela do jogo
        clock (pygame.time.Clock): Relógio do jogo
        running (bool): Se o jogo está rodando
        state (str): Estado atual do jogo
        current_level (int): Nível atual
        difficulty (str): Dificuldade
        asset_manager (AssetManager): Gerenciador de assets
        db_proxy (DBProxy): Proxy do banco de dados
    """

    def __init__(self):
        """Inicializa o jogo."""
        # Inicializar Pygame
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"⚠ Aviso: Não foi possível inicializar áudio: {e}")
            print("  O jogo continuará sem som.")
            # Desabilitar som em AssetManager
            os.environ['SDL_AUDIODRIVER'] = 'dummy'

        # Criar janela
        self.window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        pygame.display.set_caption(WIN_TITLE)

        # Relógio
        self.clock = pygame.time.Clock()

        # Estado
        self.running = True
        self.state = GAME_STATE_MENU
        self.current_level = 1
        self.difficulty = DIFFICULTY_NORMAL

        # Gerenciadores
        # Usar caminho absoluto para assets
        assets_path = os.path.join(os.path.dirname(__file__), '..', 'assets')
        self.asset_manager = AssetManager(assets_path)
        self.db_proxy = DBProxy()

        # Menu e nível
        self.menu = None
        self.level = None

        print("✓ Jogo inicializado com sucesso!")

    def run(self):
        """Executa o loop principal do jogo."""
        print("▶ Iniciando jogo...")

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
        """Executa o menu principal."""
        print("▶ Entrando no menu...")

        # Reproduzir música do menu
        self.asset_manager.play_music(MUSIC_MENU, loops=-1)

        # Criar e executar menu
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
        """Executa um nível."""
        print(f"▶ Iniciando nível {self.current_level}...")

        # Parar música do menu
        self.asset_manager.stop_music()

        # Reproduzir música de fundo
        self.asset_manager.play_music(MUSIC_BACKGROUND, loops=-1)

        # Criar e executar nível
        self.level = Level(
        self.window,
        self.current_level,
        self.difficulty,
        self.db_proxy
        )
        result = self.level.run()

        if result == 'menu':
            self.state = GAME_STATE_MENU
        elif result == 'game_over':
            self.state = GAME_STATE_GAME_OVER
        elif result == 'next_level':
            self.current_level += 1
            self.state = GAME_STATE_PLAYING

    def _run_game_over(self):
        """Executa a tela de game over."""
        print("▶ Jogo terminado!")

        # Aguardar entrada
        waiting = True
        clock = pygame.time.Clock()

        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.state = GAME_STATE_MENU
                        waiting = False

            # Desenhar última tela de game over
            if self.level:
                self.level.draw()

            pygame.display.flip()
            clock.tick(60)

    def _run_win(self):
        """Executa a tela de vitória."""
        print("▶ Nível completado!")

        # Aguardar entrada
        waiting = True
        clock = pygame.time.Clock()

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

            # Desenhar última tela de vitória
            if self.level:
                self.level.draw()

            pygame.display.flip()
            clock.tick(60)

    def _show_high_scores(self):
        """Exibe a tela de maiores pontuações."""
        print("▶ Exibindo maiores pontuações...")

        scores = self.db_proxy.get_high_scores(limit=10)

        # Criar tela de pontuações
        font_title = pygame.font.Font(None, 72)
        font_score = pygame.font.Font(None, 32)

        showing = True
        clock = pygame.time.Clock()

        while showing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    showing = False
                if event.type == pygame.KEYDOWN:
                    showing = False

            # Desenhar
            self.window.fill(BACKGROUND_COLOR)

            # Título
            title_text = font_title.render("HIGH SCORES", True, (0, 255, 255))
            title_rect = title_text.get_rect(center=(WIN_WIDTH // 2, 50))
            self.window.blit(title_text, title_rect)

            # Pontuações
            y_offset = 150
            if scores:
                for i, (name, score, level, date) in enumerate(scores):
                    score_text = font_score.render(
                        f"{i + 1}. {name} - {score} (Level {level})",
                        True, (255, 255, 255)
                    )
                    self.window.blit(score_text, (100, y_offset))
                    y_offset += 40
            else:
                no_scores_text = font_score.render("Nenhuma pontuação salva", True, (255, 255, 255))
                self.window.blit(no_scores_text, (WIN_WIDTH // 2 - 150, WIN_HEIGHT // 2))

            # Instrução
            font_small = pygame.font.Font(None, 24)
            back_text = font_small.render("Pressione qualquer tecla para voltar", True, (255, 255, 255))
            self.window.blit(back_text, (WIN_WIDTH // 2 - 150, WIN_HEIGHT - 50))

            pygame.display.flip()
            clock.tick(60)

        self.state = GAME_STATE_MENU

    def _cleanup(self):
        """Limpa recursos do jogo."""
        print("▶ Encerrando jogo...")

        # Fechar banco de dados
        self.db_proxy.close()

        # Descarregar assets
        self.asset_manager.unload_all()

        # Sair do Pygame
        pygame.quit()

        print("✓ Jogo encerrado com sucesso!")

    def __repr__(self) -> str:
        """Representação em string do jogo."""
        return f"Game(state='{self.state}', level={self.current_level}, difficulty='{self.difficulty}')"
