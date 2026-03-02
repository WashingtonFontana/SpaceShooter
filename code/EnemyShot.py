import pygame
from code.Entity import Entity
from code.AssetManager import AssetManager
from code.Const import SPRITE_ENEMY_SHOT


class EnemyShot(Entity):
    def __init__(self, name: str, x: float, y: float, width: int = 6,
                 height: int = 6, asset_manager: AssetManager = None):
        super().__init__(name, x, y, width, height)
        self.damage = 5
        self.asset_manager = asset_manager or AssetManager()
        self.image = self.asset_manager.load_sprite(SPRITE_ENEMY_SHOT, (width, height))
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def update(self):
        """Aplica velocidade e sincroniza o retângulo para evitar rastros visuais."""
        self.apply_velocity()
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)

    def __repr__(self) -> str:
        """Representação em string do tiro."""
        return f"EnemyShot(pos=({self.x}, {self.y}), damage={self.damage})"
