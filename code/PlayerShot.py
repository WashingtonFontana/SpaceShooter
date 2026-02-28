import pygame
from code.Entity import Entity
from code.AssetManager import AssetManager
from code.Const import SPRITE_PLAYER_SHOT


class PlayerShot(Entity):
    """
    Classe que representa um tiro do jogador.

    Atributos:
        damage (int): Dano causado
        asset_manager (AssetManager): Gerenciador de assets
    """

    def __init__(self, name: str, x: float, y: float, width: int = 8,
                 height: int = 8, asset_manager: AssetManager = None):
        """
        Inicializa um tiro do jogador.

        Args:
            name (str): Nome do tiro
            x (float): Posição X
            y (float): Posição Y
            width (int): Largura
            height (int): Altura
            asset_manager (AssetManager): Gerenciador de assets
        """
        super().__init__(name, x, y, width, height)

        self.damage = 10
        self.asset_manager = asset_manager or AssetManager()

        # Carregar sprite
        self.image = self.asset_manager.load_sprite(SPRITE_PLAYER_SHOT, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = int(x)
        self.rect.y = int(y)

    def update(self):
        """Atualiza o tiro."""
        # Aplicar velocidade
        self.apply_velocity()

        # Atualizar retângulo
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, surface: pygame.Surface):
        """
        Desenha o tiro na tela.

        Args:
            surface (pygame.Surface): Superfície para desenhar
        """
        surface.blit(self.image, self.rect)

    def __repr__(self) -> str:
        """Representação em string do tiro."""
        return f"PlayerShot(pos=({self.x}, {self.y}), damage={self.damage})"
