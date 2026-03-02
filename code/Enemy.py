import pygame
import random
from code.Entity import Entity
from code.AssetManager import AssetManager
from code.Const import (ENEMY_HEALTH, ENEMY_SHOOT_INTERVAL, ENEMY_SHOOT_CHANCE,
                        SPRITE_ENEMY, SOUND_ENEMY_SHOOT, ENEMY_SPEED, WIN_WIDTH)


class Enemy(Entity):
    def __init__(self, name: str, x: float, y: float, width: int = 35,
                 height: int = 35, patrol_points: list = None,
                 enemy_type: str = 'basic', asset_manager: AssetManager = None):
        super().__init__(name, x, y, width, height)

        # Define patrulha horizontal automática se não houver pontos específicos
        if not patrol_points:
            self.patrol_points = [(x, y), (min(x + 100, WIN_WIDTH - width), y), (max(x - 100, 0), y)]
        else:
            self.patrol_points = patrol_points

        self.current_patrol_index = 0
        self.shoot_cooldown = 0
        self.shoot_interval = ENEMY_SHOOT_INTERVAL
        self.shoot_chance = ENEMY_SHOOT_CHANCE
        self.enemy_type = enemy_type
        self.asset_manager = asset_manager or AssetManager()
        self.health = ENEMY_HEALTH if enemy_type != 'strong' else ENEMY_HEALTH * 2

        self.image = self.asset_manager.load_sprite(SPRITE_ENEMY, (width, height))
        self.rect = self.image.get_rect(topleft=(int(x), int(y)))

    def update(self):
        """Atualiza movimento de patrulha e cooldown de tiro."""
        self.patrol()

        # Sincroniza o rect com a posição float para evitar borrões
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def patrol(self):
        """Move o inimigo entre os pontos de patrulha."""
        if not self.patrol_points:
            return

        target_x, target_y = self.patrol_points[self.current_patrol_index]

        dx = target_x - self.x
        dy = target_y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance < 5:
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
        else:
            # Movimentação baseada na velocidade constante
            self.x += (dx / distance) * ENEMY_SPEED
            self.y += (dy / distance) * ENEMY_SPEED

    def shoot(self) -> bool:
        """Verifica se o inimigo pode disparar."""
        if self.shoot_cooldown <= 0 and random.random() < self.shoot_chance:
            self.shoot_cooldown = self.shoot_interval
            self.asset_manager.play_sound(SOUND_ENEMY_SHOOT)
            return True
        return False

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)