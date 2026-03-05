from code.Player import Player
from code.Enemy import Enemy
from code.PlayerShot import PlayerShot
from code.EnemyShot import EnemyShot
from code.AssetManager import AssetManager
from code.Const import (ENTITY_SIZE, PLAYER_SPEED, ENEMY_SPEED,
                        PLAYER_SHOT_SPEED, ENEMY_SHOT_SPEED)


class EntityFactory:
    """
    EntityFactory que centraliza a criação de todos os objetos do jogo.

    Centraliza a criação de objetos, facilitando manutenção e expansão.
    """

    def __init__(self, asset_manager: AssetManager = None):
        """Inicializa a fábrica e conecta o gerenciador de imagens e sons."""
        self.asset_manager = asset_manager or AssetManager()

    def create_player(self, name: str, x: float, y: float) -> Player:
        """Cria o jogador com o tamanho padrão e velocidade inicial zerada."""
        player = Player(
            name=name,
            x=x,
            y=y,
            width=ENTITY_SIZE.get('Player', 40),
            height=ENTITY_SIZE.get('Player', 40),
            asset_manager=self.asset_manager
        )
        player.set_velocity(0, 0) # Começa parado
        return player

    def create_enemy(self, name: str, x: float, y: float,
                     patrol_points: list = None, enemy_type: str = 'basic') -> Enemy:
        """Cria um inimigo e define sua velocidade de acordo com o tipo (Rápido, Forte ou Básico)."""
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

        # Ajusta a velocidade conforme o tipo do inimigo
        if enemy_type == 'fast':
            enemy.set_velocity(ENEMY_SPEED * 1.5, 0)
        elif enemy_type == 'strong':
            enemy.set_velocity(ENEMY_SPEED * 0.7, 0)
        else:
            enemy.set_velocity(ENEMY_SPEED, 0)

        return enemy

    def create_player_shot(self, name: str, x: float, y: float) -> PlayerShot:
        """Cria o tiro do jogador subindo na vertical com a velocidade definida nas constantes."""
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
        """Cria o tiro do inimigo. Se houver um alvo (player), calcula a direção para acertá-lo."""
        shot = EnemyShot(
            name=name,
            x=x,
            y=y,
            width=ENTITY_SIZE.get('EnemyShot', 6),
            height=ENTITY_SIZE.get('EnemyShot', 6),
            asset_manager=self.asset_manager
        )

        # Lógica para fazer o tiro perseguir a posição do jogador
        if target_x is not None and target_y is not None:
            dx = target_x - x
            dy = target_y - y
            distance = (dx ** 2 + dy ** 2) ** 0.5 # Cálculo da distância

            if distance > 0:
                # Move o tiro na direção exata do alvo
                vx = (dx / distance) * ENEMY_SHOT_SPEED
                vy = (dy / distance) * ENEMY_SHOT_SPEED
                shot.set_velocity(vx, vy)
            else:
                shot.set_velocity(0, ENEMY_SHOT_SPEED)
        else:
            # Se não houver alvo, o tiro apenas desce reto
            shot.set_velocity(0, ENEMY_SHOT_SPEED)
        return shot

    def create_batch_enemies(self, count: int, base_x: float, base_y: float,
                             spacing: int = 150) -> list:
        """Cria vários inimigos básicos de uma vez, alinhados horizontalmente com um espaço entre eles."""
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