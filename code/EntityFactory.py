from code.Player import Player
from code.Enemy import Enemy
from code.PlayerShot import PlayerShot
from code.EnemyShot import EnemyShot
from code.AssetManager import AssetManager
from code.Const import (ENTITY_SIZE, PLAYER_SPEED, ENEMY_SPEED,
                        PLAYER_SHOT_SPEED, ENEMY_SHOT_SPEED)


class EntityFactory:
    """
    Factory que cria diferentes tipos de entidades do jogo.

    Centraliza a criação de objetos, facilitando manutenção e expansão.
    """

    def __init__(self, asset_manager: AssetManager = None):
        """
        Inicializa a factory.

        Args:
            asset_manager (AssetManager): Gerenciador de assets
        """
        self.asset_manager = asset_manager or AssetManager()

    def create_player(self, name: str, x: float, y: float) -> Player:
        """
        Cria um jogador.

        Args:
            name (str): Nome do jogador
            x (float): Posição X
            y (float): Posição Y

        Returns:
            Player: Jogador criado
        """
        player = Player(
            name=name,
            x=x,
            y=y,
            width=ENTITY_SIZE.get('Player', 40),
            height=ENTITY_SIZE.get('Player', 40),
            asset_manager=self.asset_manager
        )
        player.set_velocity(0, 0)
        return player

    def create_enemy(self, name: str, x: float, y: float,
                     patrol_points: list = None, enemy_type: str = 'basic') -> Enemy:
        """
        Cria um inimigo.

        Args:
            name (str): Nome do inimigo
            x (float): Posição X
            y (float): Posição Y
            patrol_points (list): Pontos de patrulha
            enemy_type (str): Tipo de inimigo ('basic', 'fast', 'strong')

        Returns:
            Enemy: Inimigo criado
        """
        enemy = Enemy(
            name=name,
            x=x,
            y=y,
            width=ENTITY_SIZE.get('Enemy', 35),
            height=ENTITY_SIZE.get('Enemy', 35),
            patrol_points=patrol_points,
            enemy_type=enemy_type,
            asset_manager=self.asset_manager
        )

        # Configurar velocidade baseado no tipo
        if enemy_type == 'fast':
            enemy.set_velocity(ENEMY_SPEED * 1.5, 0)
        elif enemy_type == 'strong':
            enemy.set_velocity(ENEMY_SPEED * 0.7, 0)
        else:
            enemy.set_velocity(ENEMY_SPEED, 0)

        return enemy

    def create_player_shot(self, name: str, x: float, y: float) -> PlayerShot:
        """
        Cria um tiro do jogador.

        Args:
            name (str): Nome do tiro
            x (float): Posição X
            y (float): Posição Y

        Returns:
            PlayerShot: Tiro criado
        """
        shot = PlayerShot(
            name=name,
            x=x,
            y=y,
            width=ENTITY_SIZE.get('PlayerShot', 8),
            height=ENTITY_SIZE.get('PlayerShot', 8),
            asset_manager=self.asset_manager
        )
        shot.set_velocity(0, -PLAYER_SHOT_SPEED)
        return shot

    def create_enemy_shot(self, name: str, x: float, y: float,
                          target_x: float = None, target_y: float = None) -> EnemyShot:
        """
        Cria um tiro do inimigo.

        Args:
            name (str): Nome do tiro
            x (float): Posição X
            y (float): Posição Y
            target_x (float): Posição X do alvo (para calcular direção)
            target_y (float): Posição Y do alvo (para calcular direção)

        Returns:
            EnemyShot: Tiro criado
        """
        shot = EnemyShot(
            name=name,
            x=x,
            y=y,
            width=ENTITY_SIZE.get('EnemyShot', 6),
            height=ENTITY_SIZE.get('EnemyShot', 6),
            asset_manager=self.asset_manager
        )

        # Se houver alvo, calcular direção
        if target_x is not None and target_y is not None:
            dx = target_x - x
            dy = target_y - y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance > 0:
                # Normalizar e aplicar velocidade
                vx = (dx / distance) * ENEMY_SHOT_SPEED
                vy = (dy / distance) * ENEMY_SHOT_SPEED
                shot.set_velocity(vx, vy)
            else:
                shot.set_velocity(0, ENEMY_SHOT_SPEED)
        else:
            shot.set_velocity(0, ENEMY_SHOT_SPEED)

        return shot

    def create_batch_enemies(self, count: int, base_x: float, base_y: float,
                             spacing: int = 150) -> list:
        """
        Cria um lote de inimigos.

        Args:
            count (int): Quantidade de inimigos
            base_x (float): Posição X base
            base_y (float): Posição Y base
            spacing (int): Espaçamento entre inimigos

        Returns:
            list: Lista de inimigos criados
        """
        enemies = []
        for i in range(count):
            x = base_x + (i * spacing)
            enemy = self.create_enemy(
                name=f'Enemy_{i}',
                x=x,
                y=base_y,
                enemy_type='basic'
            )
            enemies.append(enemy)
        return enemies