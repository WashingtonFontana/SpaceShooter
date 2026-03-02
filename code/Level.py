import sys

import pygame
from code.EntityFactory import EntityFactory
from code.EntityMediator import EntityMediator
from code.Const import (C_WHITE, WIN_WIDTH, WIN_HEIGHT, SCORE_ENEMY_DESTROYED,
                        C_GREEN, C_RED, DIFFICULTY_SETTINGS, SPRITE_BACKGROUNDS, PLAYER_KEY_ESCAPE)


class Level:
    def __init__(self, window, level_number: int, difficulty: str, db_proxy):
        self.window = window
        self.entity_factory = EntityFactory()
        self.mediator = EntityMediator()
        self.db_proxy = db_proxy
        self.level_number = level_number
        self.difficulty = difficulty
        self.settings = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS['normal'])

        # --- LÓGICA DE TROCA DE BACKGROUND ---
        # Seleciona a imagem baseada no nível (ex: Level 1 usa índice 0, Level 2 usa índice 1...)
        bg_index = (level_number - 1) % len(SPRITE_BACKGROUNDS)
        selected_bg = SPRITE_BACKGROUNDS[bg_index]

        # Carrega a imagem selecionada e redimensiona para o tamanho da janela
        self.background = self.entity_factory.asset_manager.load_sprite(
            selected_bg, (WIN_WIDTH, WIN_HEIGHT)
        )

        # Inicialização do Player e Inimigos
        self.player = self.entity_factory.create_player("Player", WIN_WIDTH // 2, WIN_HEIGHT - 80)
        self.player.health = self.settings['player_health']

        self.enemies = []
        self.player_shots = []
        self.enemy_shots = []

        self.spawn_enemies()
        self.running = True

    def spawn_enemies(self):
        """Cria inimigos em grade para garantir que fiquem dentro da tela."""
        num_enemies = 5 + (self.level_number * 2)
        cols = 5
        spacing_x = 150
        spacing_y = 80
        margin_x = (WIN_WIDTH - (cols * spacing_x)) // 2

        for i in range(num_enemies):
            col = i % cols
            row = i // cols
            x = margin_x + (col * spacing_x)
            y = 50 + (row * spacing_y)

            patrol = [(x, y), (min(x + 40, WIN_WIDTH - 40), y), (max(x - 40, 0), y)]
            enemy = self.entity_factory.create_enemy(f"Enemy_{i}", x, y, patrol_points=patrol)

            enemy.shoot_chance = self.settings['enemy_shoot_chance']
            enemy.health = self.settings['enemy_health']
            self.enemies.append(enemy)

    def run(self):
        """Executa o loop do nível."""
        clock = pygame.time.Clock()
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)

        if self.player and not self.player.is_alive:
            self.db_proxy.save_score("Player1", self.mediator.get_score(), self.level_number)
            return "game_over"
        return "next_level" if not self.enemies else "menu"

    def handle_events(self):
        """
        Processa os eventos do jogo.
        Usa o handle_input do Player e verifica o ESC.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Detecta a tecla ESC para voltar ao Menu
                if event.key == PLAYER_KEY_ESCAPE:
                    self.running = False
                    return "MENU"

        # 1. Processa entrada do Player (Movimento e Gatilho)
        # handle_input() define vx/vy e retorna True se o Espaço estiver pressionado
        is_shooting = self.player.handle_input()

        # 2. Verifica se pode atirar
        if self.player.can_shoot(is_shooting):
            # Aqui você chama a sua Factory para criar o tiro, ex:
            # self.player.shoot()
            # self.entity_factory.create_player_shot(self.player)
            pass

        return "PLAYING"

    def update(self):
        # Update do Player
        is_shooting = self.player.handle_input()
        self.player.update()
        if self.player.can_shoot(is_shooting):
            new_shot = self.entity_factory.create_player_shot("PShot", self.player.x + 16, self.player.y)
            self.player_shots.append(new_shot)
            self.player.shoot()

        # Update Inimigos
        for enemy in self.enemies:
            enemy.update()
            if enemy.shoot():
                e_shot = self.entity_factory.create_enemy_shot("EShot", enemy.x + 15, enemy.y + 30)
                self.enemy_shots.append(e_shot)

        self.update_projectiles()
        self.check_collisions()

        if not self.enemies: self.running = False

    def update_projectiles(self):
        for s in self.player_shots[:]:
            s.update()
            if s.y < -20: self.player_shots.remove(s)
        for s in self.enemy_shots[:]:
            s.update()
            if s.y > WIN_HEIGHT: self.enemy_shots.remove(s)

    def check_collisions(self):
        for shot in self.player_shots[:]:
            for enemy in self.enemies[:]:
                if shot.collides_with(enemy):
                    enemy.take_damage(1)
                    if not enemy.is_alive:
                        self.mediator.on_enemy_destroyed({'score': SCORE_ENEMY_DESTROYED})
                        self.enemies.remove(enemy)
                    if shot in self.player_shots: self.player_shots.remove(shot)

        for shot in self.enemy_shots[:]:
            if shot.collides_with(self.player):
                self.player.take_damage(shot.damage)
                self.mediator.on_player_hit(shot.damage)
                if shot in self.enemy_shots: self.enemy_shots.remove(shot)
                if not self.player.is_alive: self.running = False

    def draw(self):
        """Renderiza os elementos na tela com o background atualizado."""
        if self.background:
            self.window.blit(self.background, (0, 0))
        else:
            self.window.fill((0, 0, 0))

        self.player.draw(self.window)
        for e in self.enemies: e.draw(self.window)
        for s in self.player_shots: s.draw(self.window)
        for s in self.enemy_shots: s.draw(self.window)

        self._draw_hud()
        pygame.display.flip()

    def _draw_hud(self):
        font = pygame.font.Font(None, 32)
        score_txt = font.render(f"SCORE: {self.mediator.get_score()}", True, C_WHITE)
        self.window.blit(score_txt, (20, 20))

        hp_color = C_GREEN if self.player.health > 30 else C_RED
        hp_txt = font.render(f"HP: {int(self.player.health)}", True, hp_color)
        self.window.blit(hp_txt, (WIN_WIDTH - 100, 20))