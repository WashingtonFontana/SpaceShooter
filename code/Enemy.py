import pygame
import random
from code.Entity import Entity
from code.AssetManager import AssetManager
from code.Const import (ENEMY_HEALTH, ENEMY_SHOOT_INTERVAL, ENEMY_SHOOT_CHANCE,
                        SPRITE_ENEMY, SOUND_ENEMY_SHOOT, ENEMY_SPEED)


class Enemy(Entity):
    """
    Classe que representa um inimigo.

    Atributos:
        patrol_points (list): Pontos de patrulha
        current_patrol_index (int): Índice do ponto atual
        shoot_cooldown (int): Cooldown de tiro
        shoot_interval (int): Intervalo de tiro
        shoot_chance (float): Chance de atirar
        enemy_type (str): Tipo de inimigo
        asset_manager (AssetManager): Gerenciador de assets
    """

    def __init__(self, name: str, x: float, y: float, width: int = 35,
                 height: int = 35, patrol_points: list = None,
                 enemy_type: str = 'basic', asset_manager: AssetManager = None):
        """
        Inicializa um inimigo.

        Args:
            name (str): Nome do inimigo
            x (float): Posição X
            y (float): Posição Y
            width (int): Largura
            height (int): Altura
            patrol_points (list): Pontos de patrulha
            enemy_type (str): Tipo de inimigo
            asset_manager (AssetManager): Gerenciador de assets
        """
        super().__init__(name, x, y, width, height)

        # Inicializar patrol_points como lista
        if patrol_points is None:
            self.patrol_points = [(x, y)]
        elif isinstance(patrol_points, dict):
            # Se for dicionário, converter para lista
            self.patrol_points = list(patrol_points.values()) if patrol_points else [(x, y)]
        else:
            self.patrol_points = patrol_points if patrol_points else [(x, y)]

        self.current_patrol_index = 0
        self.shoot_cooldown = 0
        self.shoot_interval = ENEMY_SHOOT_INTERVAL
        self.shoot_chance = ENEMY_SHOOT_CHANCE
        self.enemy_type = enemy_type
        self.asset_manager = asset_manager or AssetManager()

        # Configurar saúde baseado no tipo
        if enemy_type == 'strong':
            self.health = ENEMY_HEALTH * 2
        else:
            self.health = ENEMY_HEALTH

        # Carregar sprite
        self.image = self.asset_manager.load_sprite(SPRITE_ENEMY, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = int(x)
        self.rect.y = int(y)

    def update(self):
        """Atualiza o inimigo."""
        # Patrulhar
        self.patrol()

        # Atualizar retângulo
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Atualizar cooldown de tiro
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def _extract_coordinates(self, point):
        """
        Extrai coordenadas X e Y de um ponto.

        Args:
            point: Ponto (tupla, lista ou outro)

        Returns:
            tuple: (x, y) como floats
        """
        try:
            # Se for tupla ou lista com 2 elementos
            if isinstance(point, (list, tuple)) and len(point) >= 2:
                x = point[0]
                y = point[1]

                # Se x ou y forem tuplas/listas, extrair o primeiro elemento
                if isinstance(x, (list, tuple)):
                    x = x[0] if len(x) > 0 else 0
                if isinstance(y, (list, tuple)):
                    y = y[0] if len(y) > 0 else 0

                return (float(x), float(y))
            else:
                return (0.0, 0.0)
        except (ValueError, TypeError, IndexError):
            return (0.0, 0.0)

    def patrol(self):
        """Patrulha entre os pontos definidos."""
        # Validar patrol_points
        if not self.patrol_points or len(self.patrol_points) == 0:
            self.patrol_points = [(self.x, self.y)]
            return

        # Validar índice
        if self.current_patrol_index >= len(self.patrol_points):
            self.current_patrol_index = 0

        # Obter ponto alvo com segurança
        try:
            target = self.patrol_points[self.current_patrol_index]
            target_x, target_y = self._extract_coordinates(target)
        except (IndexError, KeyError, TypeError):
            self.current_patrol_index = 0
            target = self.patrol_points[0]
            target_x, target_y = self._extract_coordinates(target)

        # Calcular distância e direção
        dx = target_x - self.x
        dy = target_y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # Se chegou ao ponto, ir para o próximo
        if distance < 5:
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
        else:
            # Mover em direção ao alvo
            if distance > 0:
                speed = ENEMY_SPEED
                self.x += (dx / distance) * speed
                self.y += (dy / distance) * speed

    def draw(self, surface: pygame.Surface):
        """
        Desenha o inimigo na tela.

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
        if self.shoot_cooldown <= 0:
            return random.random() < self.shoot_chance
        return False

    def shoot(self) -> bool:
        """
        Tira um tiro.

        Returns:
            bool: True se conseguiu atirar
        """
        if self.can_shoot():
            self.shoot_cooldown = self.shoot_interval
            self.asset_manager.play_sound(SOUND_ENEMY_SHOOT)
            return True
        return False

    def __repr__(self) -> str:
        """Representação em string do inimigo."""
        return f"Enemy(name='{self.name}', type='{self.enemy_type}', pos=({self.x}, {self.y}), health={self.health})"
