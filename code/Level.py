import sys

import pygame
from code.EntityFactory import EntityFactory
from code.EntityMediator import EntityMediator
from code.Const import (C_WHITE, WIN_WIDTH, WIN_HEIGHT, SCORE_ENEMY_DESTROYED,
                        C_GREEN, C_RED, DIFFICULTY_SETTINGS, SPRITE_BACKGROUNDS, PLAYER_KEY_ESCAPE)


class Level:
    """Prepara o nível, as fábricas de objetos e as configurações de dificuldade."""
    def __init__(self, window, level_number: int, difficulty: str, db_proxy):
        self.window = window
        self.entity_factory = EntityFactory()
        self.mediator = EntityMediator()
        self.db_proxy = db_proxy
        self.level_number = level_number
        self.difficulty = difficulty
        self.settings = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS['normal'])

        # --- LÓGICA DE TROCA DE BACKGROUND ---
        # Define qual fundo usar com base no número da fase
        bg_index = (level_number - 1) % len(SPRITE_BACKGROUNDS)
        selected_bg = SPRITE_BACKGROUNDS[bg_index]

        # Carrega e ajusta a imagem de fundo para o tamanho da tela
        self.background = self.entity_factory.asset_manager.load_sprite(
            selected_bg, (WIN_WIDTH, WIN_HEIGHT)
        )

        # Cria o jogador e define sua vida inicial conforme a dificuldade
        self.player = self.entity_factory.create_player("Player", WIN_WIDTH // 2, WIN_HEIGHT - 80)
        self.player.health = self.settings['player_health']

        # Listas para gerenciar inimigos e projéteis em cena
        self.enemies = []
        self.player_shots = []
        self.enemy_shots = []

        # Inicia a fase criando os inimigos
        self.spawn_enemies()
        self.running = True

    def spawn_enemies(self):
        """Organiza os inimigos em fileiras e define seus caminhos de patrulha."""
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

            # Define três pontos (origem, direita, esquerda) para o inimigo patrulhar
            patrol = [(x, y), (min(x + 40, WIN_WIDTH - 40), y), (max(x - 40, 0), y)]
            enemy = self.entity_factory.create_enemy(f"Enemy_{i}", x, y, patrol_points=patrol)

            # Ajusta força e agressividade do inimigo pela dificuldade da fase
            enemy.shoot_chance = self.settings['enemy_shoot_chance']
            enemy.health = self.settings['enemy_health']
            self.enemies.append(enemy)

    def run(self):
        """Mantém o nível rodando a 60 FPS e decide o próximo estado ao terminar."""
        clock = pygame.time.Clock()
        while self.running:
            self.handle_events() # Escuta entradas
            self.update() # Processa lógica
            self.draw() # Desenha na tela
            clock.tick(60)

        # Ao sair do loop, verifica se o jogador perdeu para salvar o score
        if self.player and not self.player.is_alive:
            self.db_proxy.save_score("Player1", self.mediator.get_score(), self.level_number)
            return "game_over"
        # Retorna vitória se não sobrarem inimigos, caso contrário volta ao menu
        return "next_level" if not self.enemies else "menu"

    def handle_events(self):
        """Verifica se o jogador quer fechar o jogo ou voltar ao menu (ESC)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Detecta a tecla ESC para voltar ao Menu
                if event.key == PLAYER_KEY_ESCAPE:
                    self.running = False
                    return "MENU"

        # Captura se o jogador está tentando atirar
        is_shooting = self.player.handle_input()

        # 2. Verifica se pode atirar
        if self.player.can_shoot(is_shooting):
            # Aqui chama a sua Factory para criar o tiro
            pass
        return "PLAYING"

    def update(self):
        """Atualiza movimentos, disparos e checa se alguém foi atingido."""
        is_shooting = self.player.handle_input()
        self.player.update()

        # Cria novo tiro do jogador se ele apertar espaço e o cooldown permitir
        if self.player.can_shoot(is_shooting):
            new_shot = self.entity_factory.create_player_shot("PShot", self.player.x + 16, self.player.y)
            self.player_shots.append(new_shot)
            self.player.shoot()

        # Atualiza inimigos e verifica se algum deles decide atirar
        for enemy in self.enemies:
            enemy.update()
            if enemy.shoot():
                e_shot = self.entity_factory.create_enemy_shot("EShot", enemy.x + 15, enemy.y + 30)
                self.enemy_shots.append(e_shot)

        self.update_projectiles() # Move tiros e remove os que saíram da tela
        self.check_collisions() # Checa colisões entre tiros e personagens

        # Termina a fase se todos os inimigos morrerem
        if not self.enemies: self.running = False

    def update_projectiles(self):
        """Move os tiros e limpa a memória removendo tiros fora dos limites da tela."""
        for s in self.player_shots[:]:
            s.update()
            if s.y < -20: self.player_shots.remove(s)
        for s in self.enemy_shots[:]:
            s.update()
            if s.y > WIN_HEIGHT: self.enemy_shots.remove(s)

    def check_collisions(self):
        """Lógica de impacto: tiros do player nos inimigos e tiros inimigos no player."""
        # Colisão: Tiro do Player -> Inimigo
        for shot in self.player_shots[:]:
            for enemy in self.enemies[:]:
                if shot.collides_with(enemy):
                    enemy.take_damage(1)
                    if not enemy.is_alive:
                        self.mediator.on_enemy_destroyed({'score': SCORE_ENEMY_DESTROYED})
                        self.enemies.remove(enemy)
                    if shot in self.player_shots: self.player_shots.remove(shot)

        # Colisão: Tiro do Inimigo -> Player
        for shot in self.enemy_shots[:]:
            if shot.collides_with(self.player):
                self.player.take_damage(shot.damage)
                self.mediator.on_player_hit(shot.damage)
                if shot in self.enemy_shots: self.enemy_shots.remove(shot)
                if not self.player.is_alive: self.running = False

    def draw(self):
        """Desenha o fundo, personagens e projéteis na ordem correta."""
        if self.background:
            self.window.blit(self.background, (0, 0))
        else:
            self.window.fill((0, 0, 0))

        self.player.draw(self.window)
        for e in self.enemies: e.draw(self.window)
        for s in self.player_shots: s.draw(self.window)
        for s in self.enemy_shots: s.draw(self.window)

        self._draw_hud() # Desenha placar e vida por cima de tudo
        pygame.display.flip()

    def _draw_hud(self):
        """Exibe as informações de texto (Pontos e Vida) na tela."""
        font = pygame.font.Font(None, 32)
        score_txt = font.render(f"SCORE: {self.mediator.get_score()}", True, C_WHITE)
        self.window.blit(score_txt, (20, 20))

        # Muda a cor do texto da vida para vermelho se estiver baixa
        hp_color = C_GREEN if self.player.health > 30 else C_RED
        hp_txt = font.render(f"HP: {int(self.player.health)}", True, hp_color)
        self.window.blit(hp_txt, (WIN_WIDTH - 100, 20))