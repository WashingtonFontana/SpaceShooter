import pygame
from code.EntityFactory import EntityFactory
from code.EntityMediator import EntityMediator
from code.Score import Score
from code.AssetManager import AssetManager
from code.Const import (WIN_WIDTH, WIN_HEIGHT, C_BLACK, C_WHITE, C_RED, C_GREEN,
                        SPAWN_POSITIONS, PATROL_POINTS, PLAYER_KEY_ESCAPE,
                        PLAYER_KEY_SHOOT, GAME_STATE_PLAYING, GAME_STATE_GAME_OVER,
                        GAME_STATE_WIN, DIFFICULTY_NORMAL, DIFFICULTY_SETTINGS)


class Level:
    """Classe que gerencia um nível do jogo."""

    def __init__(self, window: pygame.Surface, level_number: int = 1,
                 difficulty: str = DIFFICULTY_NORMAL, db_proxy=None):
        """
        Inicializa um nível.

        Args:
            window (pygame.Surface): Janela do jogo
            level_number (int): Número do nível
            difficulty (str): Dificuldade
        """
        self.window = window
        self.level_number = level_number
        self.difficulty = difficulty
        self.state = GAME_STATE_PLAYING

        # Gerenciadores
        self.asset_manager = AssetManager('assets')
        self.entity_factory = EntityFactory(self.asset_manager)
        self.mediator = EntityMediator()
        self.score = Score(db_proxy=db_proxy)
        self.score.set_level(self.level_number)

        # Carregar fundo baseado no nível
        self.background = self._load_background(level_number)

        # Entidades
        self.player = self.entity_factory.create_player('Player',
                                                        SPAWN_POSITIONS['Player'][0],
                                                        SPAWN_POSITIONS['Player'][1])

        self.enemies = []
        self.player_shots = []
        self.enemy_shots = []

        # Criar inimigos
        self._create_enemies()

        # Fontes
        self.font_title = pygame.font.Font(None, 48)
        self.font_text = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # Configurações de dificuldade
        self.difficulty_settings = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS[DIFFICULTY_NORMAL])
        self.player.health = self.difficulty_settings['player_health']

    def _load_background(self, level_number: int):
        """Carrega o fundo baseado no nível."""
        try:
            # Selecionar fundo baseado no nível
            backgrounds = ['background_1.png', 'background_2.webp', 'background_3.png']
            bg_index = (level_number - 1) % len(backgrounds)
            bg_name = backgrounds[bg_index]

            # Carregar e redimensionar
            bg = self.asset_manager.load_sprite(bg_name, (WIN_WIDTH, WIN_HEIGHT))
            return bg
        except Exception as e:
            print(f"Erro ao carregar fundo: {e}")
            return None

    def _create_enemies(self):
        """Cria os inimigos do nível."""
        enemy_count = 2 + self.level_number
        for i in range(enemy_count):
            x = 100 + (i * 200)
            enemy = self.entity_factory.create_enemy(
                name=f'Enemy_{i}',
                x=x,
                y=50,
                patrol_points=[(x, 50), (x + 100, 50), (x, 50)]
            )
            self.enemies.append(enemy)

    def handle_events(self) -> bool:
        """
        Processa eventos do nível.

        Returns:
            bool: False se deve sair
        """
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == PLAYER_KEY_ESCAPE:
                    return False
                elif event.key == PLAYER_KEY_SHOOT:
                    if self.player.shoot():
                        shot = self.entity_factory.create_player_shot(
                            f'PlayerShot_{len(self.player_shots)}',
                            self.player.x + self.player.width // 2,
                            self.player.y
                        )
                        self.player_shots.append(shot)

        # Processar movimento do jogador
        keys_dict = {
            pygame.K_LEFT: keys[pygame.K_LEFT],
            pygame.K_RIGHT: keys[pygame.K_RIGHT],
            pygame.K_UP: keys[pygame.K_UP],
            pygame.K_DOWN: keys[pygame.K_DOWN],
        }
        self.player.handle_input(keys_dict)

        return True

    def update(self):
        """Atualiza a lógica do nível."""
        if self.state != GAME_STATE_PLAYING:
            return

        # Atualizar jogador
        self.player.update()

        # Atualizar inimigos
        for enemy in self.enemies:
            enemy.update()

            # Inimigos atiram
            if enemy.can_shoot():
                shot = self.entity_factory.create_enemy_shot(
                    f'EnemyShot_{len(self.enemy_shots)}',
                    enemy.x + enemy.width // 2,
                    enemy.y + enemy.height,
                    self.player.x + self.player.width // 2,
                    self.player.y + self.player.height // 2
                )
                self.enemy_shots.append(shot)

        # Atualizar tiros do jogador
        for shot in self.player_shots[:]:
            shot.update()

            # Remover se saiu da tela
            if shot.is_out_of_bounds(WIN_WIDTH, WIN_HEIGHT):
                self.player_shots.remove(shot)

            # Verificar colisão com inimigos
            for enemy in self.enemies[:]:
                if shot.collides_with(enemy):
                    enemy.take_damage(shot.damage)
                    if shot in self.player_shots:
                        self.player_shots.remove(shot)

                    if not enemy.is_alive:
                        self.enemies.remove(enemy)
                        self.score.add_enemy_destroyed_score()
                        self.mediator.on_enemy_destroyed({'score': 100})
                    break

        # Atualizar tiros dos inimigos
        for shot in self.enemy_shots[:]:
            shot.update()

            # Remover se saiu da tela
            if shot.is_out_of_bounds(WIN_WIDTH, WIN_HEIGHT):
                self.enemy_shots.remove(shot)

            # Verificar colisão com jogador
            if shot.collides_with(self.player):
                self.player.take_damage(shot.damage)
                if shot in self.enemy_shots:
                    self.enemy_shots.remove(shot)

                self.mediator.on_player_hit(shot.damage)

                if not self.player.is_alive:
                    self.state = GAME_STATE_GAME_OVER

        # Verificar vitória
        if len(self.enemies) == 0:
            self.state = GAME_STATE_WIN
            self.score.add_level_complete_score()
            self.score.set_level(self.level_number)

    def draw(self):
        """Desenha o nível na tela."""
        # Fundo
        if self.background:
            self.window.blit(self.background, (0, 0))
        else:
            self.window.fill(C_BLACK)

        # Desenhar inimigos
        for enemy in self.enemies:
            enemy.draw(self.window)

        # Desenhar tiros
        for shot in self.player_shots:
            shot.draw(self.window)

        for shot in self.enemy_shots:
            shot.draw(self.window)

        # Desenhar jogador
        self.player.draw(self.window)

        # Desenhar HUD
        self._draw_hud()

        # Desenhar game over
        if self.state == GAME_STATE_GAME_OVER:
            self._draw_game_over()

        # Desenhar vitória
        if self.state == GAME_STATE_WIN:
            self._draw_win()

        pygame.display.flip()

    def _draw_hud(self):
        """Desenha o HUD (cabeçalho com informações)."""
        # Pontuação
        score_text = self.font_small.render(f'Score: {self.score.current_score}', True, C_WHITE)
        self.window.blit(score_text, (10, 10))

        # Nível
        level_text = self.font_small.render(f'Level: {self.level_number}', True, C_WHITE)
        self.window.blit(level_text, (WIN_WIDTH // 2 - 50, 10))

        # Saúde do jogador
        health_text = self.font_small.render(f'Health: {self.player.health}', True,
                                             C_GREEN if self.player.health > 30 else C_RED)
        self.window.blit(health_text, (WIN_WIDTH - 200, 10))

        # Inimigos restantes
        enemies_text = self.font_small.render(f'Enemies: {len(self.enemies)}', True, C_WHITE)
        self.window.blit(enemies_text, (10, WIN_HEIGHT - 30))

    def _draw_game_over(self):
        """Desenha a tela de game over."""
        # Fundo semi-transparente
        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(C_BLACK)
        self.window.blit(overlay, (0, 0))

        # Texto
        game_over_text = self.font_title.render("GAME OVER", True, C_RED)
        game_over_rect = game_over_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 50))
        self.window.blit(game_over_text, game_over_rect)

        # Pontuação final
        final_score_text = self.font_text.render(f"Final Score: {self.score.current_score}", True, C_WHITE)
        final_score_rect = final_score_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 20))
        self.window.blit(final_score_text, final_score_rect)

        # Instrução
        restart_text = self.font_small.render("Pressione ESPAÇO para voltar ao menu", True, C_WHITE)
        restart_rect = restart_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 80))
        self.window.blit(restart_text, restart_rect)

    def _draw_win(self):
        """Desenha a tela de vitória."""
        # Fundo semi-transparente
        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(C_BLACK)
        self.window.blit(overlay, (0, 0))

        # Texto
        win_text = self.font_title.render("LEVEL COMPLETE!", True, C_GREEN)
        win_rect = win_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 50))
        self.window.blit(win_text, win_rect)

        # Pontuação
        score_text = self.font_text.render(f"Score: {self.score.current_score}", True, C_WHITE)
        score_rect = score_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 20))
        self.window.blit(score_text, score_rect)

        # Instrução
        next_text = self.font_small.render("Pressione ESPAÇO para próximo nível", True, C_WHITE)
        next_rect = next_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 80))
        self.window.blit(next_text, next_rect)

    def run(self) -> str:
        """
        Executa o loop do nível.

        Returns:
            str: Estado final ('game_over', 'next_level', 'menu')
        """
        clock = pygame.time.Clock()

        # LOOP PRINCIPAL DO NÍVEL
        while self.state == GAME_STATE_PLAYING:

            # Processar eventos
            if not self.handle_events():
                # Atualiza nível antes de salvar
                self.score.set_level(self.level_number)

                print(
                    f"\n[DEBUG] Salvando pontuação (saída): "
                    f"{self.score.player_name} - "
                    f"{self.score.current_score} pontos - "
                    f"Nível {self.score.level}"
                )

                result = self.score.save_score()
                print(f"[DEBUG] Resultado da gravação: {result}")

                return 'menu'

            # Atualizar lógica
            self.update()

            # Desenhar tela
            self.draw()

            clock.tick(60)

        # ---------------------------------------------------------
        # O JOGO SAIU DO LOOP (GAME OVER ou WIN)
        # ---------------------------------------------------------

        # Atualiza nível antes de salvar
        self.score.set_level(self.level_number)

        print(
            f"\n[DEBUG] Salvando pontuação final: "
            f"{self.score.player_name} - "
            f"{self.score.current_score} pontos - "
            f"Nível {self.score.level}"
        )

        result = self.score.save_score()
        print(f"[DEBUG] Resultado da gravação: {result}")

        # Tela de espera (pressionar espaço)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'menu'

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False

            self.draw()
            pygame.display.flip()
            clock.tick(60)

        # Retorno correto
        if self.state == GAME_STATE_WIN:
            return 'next_level'
        else:
            return 'game_over'