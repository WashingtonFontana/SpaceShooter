import pygame
from code.Entity import Entity
from code.AssetManager import AssetManager
from code.Const import (PLAYER_SPEED, PLAYER_HEALTH, PLAYER_SHOOT_INTERVAL,
                        WIN_WIDTH, WIN_HEIGHT, C_LIGHT_BLUE, SPRITE_PLAYER,
                        SOUND_PLAYER_SHOOT)


class Player(Entity):
    """
    Classe que representa o jogador.

    Atributos:
        shoot_cooldown (int): Cooldown de tiro
        max_shots (int): Máximo de tiros simultâneos
        active_shots (list): Tiros ativos
        asset_manager (AssetManager): Gerenciador de assets
    """

    def __init__(self, name: str, x: float, y: float, width: int = 40,
                 height: int = 40, asset_manager: AssetManager = None):
        """
        Inicializa o jogador.

        Args:
            name (str): Nome do jogador
            x (float): Posição X
            y (float): Posição Y
            width (int): Largura
            height (int): Altura
            asset_manager (AssetManager): Gerenciador de assets
        """
        super().__init__(name, x, y, width, height)

        self.speed = PLAYER_SPEED
        self.health = PLAYER_HEALTH
        self.shoot_cooldown = 0
        self.shoot_interval = PLAYER_SHOOT_INTERVAL
        self.active_shots = []
        self.asset_manager = asset_manager or AssetManager()

        # Carregar sprite
        self.image = self.asset_manager.load_sprite(SPRITE_PLAYER, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = int(x)
        self.rect.y = int(y)

    def handle_input(self, keys: dict):
        """
        Processa entrada do teclado.

        Args:
            keys (dict): Dicionário de teclas pressionadas
        """
        from code.Const import (PLAYER_KEY_LEFT, PLAYER_KEY_RIGHT,
                                PLAYER_KEY_UP, PLAYER_KEY_DOWN)

        # Movimento horizontal
        if keys.get(PLAYER_KEY_LEFT):
            self.vx = -self.speed
        elif keys.get(PLAYER_KEY_RIGHT):
            self.vx = self.speed
        else:
            self.vx = 0

        # Movimento vertical
        if keys.get(PLAYER_KEY_UP):
            self.vy = -self.speed
        elif keys.get(PLAYER_KEY_DOWN):
            self.vy = self.speed
        else:
            self.vy = 0

    def update(self):
        """Atualiza o jogador."""
        # Aplicar velocidade
        self.apply_velocity()

        # Limitar aos limites da tela
        self.x = max(0, min(WIN_WIDTH - self.width, self.x))
        self.y = max(0, min(WIN_HEIGHT - self.height, self.y))

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Atualizar cooldown de tiro
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def draw(self, surface: pygame.Surface):
        """
        Desenha o jogador na tela.

        Args:
            surface (pygame.Surface): Superfície para desenhar
        """
        surface.blit(self.image, self.rect)

    def can_shoot(self) -> bool:
        """
        Verifica se pode atirar.

        Returns:
            bool: True se pode atirar
        """
        return self.shoot_cooldown <= 0

    def shoot(self) -> bool:
        """
        Tira um tiro.

        Returns:
            bool: True se conseguiu atirar
        """
        if self.can_shoot():
            self.shoot_cooldown = self.shoot_interval
            self.asset_manager.play_sound(SOUND_PLAYER_SHOOT)
            return True
        return False

    def take_damage(self, damage: int):
        """
        Aplica dano ao jogador.

        Args:
            damage (int): Quantidade de dano
        """
        super().take_damage(damage)
        self.asset_manager.play_sound('player_hit.wav')

    def __repr__(self) -> str:
        """Representação em string do jogador."""
        return f"Player(pos=({self.x}, {self.y}), health={self.health}, cooldown={self.shoot_cooldown})"