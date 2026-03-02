import pygame
from code.Entity import Entity
from code.AssetManager import AssetManager
from code.Const import (PLAYER_HEALTH, PLAYER_SHOOT_INTERVAL, SPRITE_PLAYER,
                        SOUND_PLAYER_SHOOT, PLAYER_SPEED, WIN_WIDTH, WIN_HEIGHT,
                        PLAYER_KEY_LEFT, PLAYER_KEY_RIGHT, PLAYER_KEY_UP,
                        PLAYER_KEY_DOWN, PLAYER_KEY_SHOOT)


class Player(Entity):
    def __init__(self, name: str, x: float, y: float, width: int, height: int, asset_manager: AssetManager = None):
        super().__init__(name, x, y, width, height)
        self.health = PLAYER_HEALTH
        self.asset_manager = asset_manager or AssetManager()
        self.image = self.asset_manager.load_sprite(SPRITE_PLAYER, (width, height))
        self.rect = self.image.get_rect(topleft=(int(x), int(y)))

        # Controle de tiro
        self.shoot_cooldown = 0
        self.shoot_interval = PLAYER_SHOOT_INTERVAL

    def handle_input(self):
        """Processa entrada do teclado para movimento e retorna estado do gatilho."""
        keys = pygame.key.get_pressed()

        self.vx = 0
        self.vy = 0

        if keys[PLAYER_KEY_LEFT]:
            self.vx = -PLAYER_SPEED
        elif keys[PLAYER_KEY_RIGHT]:
            self.vx = PLAYER_SPEED

        if keys[PLAYER_KEY_UP]:
            self.vy = -PLAYER_SPEED
        elif keys[PLAYER_KEY_DOWN]:
            self.vy = PLAYER_SPEED

        return keys[PLAYER_KEY_SHOOT]

    def update(self):
        """Atualiza posição, limites e cooldown."""
        self.apply_velocity()

        # Boundary Check - Mantém o jogador dentro da janela
        self.x = max(0.0, min(float(self.x), float(WIN_WIDTH - self.width)))
        self.y = max(0.0, min(float(self.y), float(WIN_HEIGHT - self.height)))

        # Sincroniza o Rect para desenho nítido
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def can_shoot(self, is_shoot_pressed: bool):
        """Verifica se o jogador pressionou a tecla e se o tempo de recarga acabou."""
        return is_shoot_pressed and self.shoot_cooldown <= 0

    def shoot(self):
        """Reseta o relógio da arma e toca o som de disparo."""
        self.shoot_cooldown = self.shoot_interval
        self.asset_manager.play_sound(SOUND_PLAYER_SHOOT)
        return True

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)

    def take_damage(self, damage: int):
        super().take_damage(damage)
        self.asset_manager.play_sound('player_hit.wav')

    def __repr__(self) -> str:
        return f"Player(pos=({self.x}, {self.y}), health={self.health})"