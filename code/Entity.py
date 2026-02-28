import pygame
from abc import ABC, abstractmethod


class Entity(ABC):
    """
    Classe abstrata que representa uma entidade do jogo.

    Atributos:
        name (str): Nome da entidade
        x (float): Posição X
        y (float): Posição Y
        vx (float): Velocidade X
        vy (float): Velocidade Y
        width (int): Largura
        height (int): Altura
        health (int): Saúde
        is_alive (bool): Se está viva
        image (pygame.Surface): Imagem da entidade
        rect (pygame.Rect): Retângulo de colisão
    """

    def __init__(self, name: str, x: float, y: float, width: int = 40, height: int = 40):
        """
        Inicializa uma entidade.

        Args:
            name (str): Nome da entidade
            x (float): Posição X
            y (float): Posição Y
            width (int): Largura
            height (int): Altura
        """
        self.name = name
        self.x = x
        self.y = y
        self.vx = 0.0  # Velocidade X
        self.vy = 0.0  # Velocidade Y
        self.width = width
        self.height = height
        self.health = 100
        self.is_alive = True

        # Imagem e retângulo de colisão
        self.image = pygame.Surface((width, height))
        self.image.fill((128, 128, 128))  # Cor padrão cinza
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    @abstractmethod
    def update(self):
        """Atualiza a lógica da entidade."""
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        """Desenha a entidade na tela."""
        pass

    def move(self, dx: float, dy: float):
        """
        Move a entidade.

        Args:
            dx (float): Deslocamento X
            dy (float): Deslocamento Y
        """
        self.x += dx
        self.y += dy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def set_velocity(self, vx: float, vy: float):
        """
        Define a velocidade da entidade.

        Args:
            vx (float): Velocidade X
            vy (float): Velocidade Y
        """
        self.vx = vx
        self.vy = vy

    def apply_velocity(self):
        """Aplica a velocidade à posição."""
        self.move(self.vx, self.vy)

    def take_damage(self, damage: int):
        """
        Aplica dano à entidade.

        Args:
            damage (int): Quantidade de dano
        """
        self.health -= damage
        if self.health <= 0:
            self.is_alive = False

    def heal(self, amount: int):
        """
        Cura a entidade.

        Args:
            amount (int): Quantidade de cura
        """
        self.health += amount
        if self.health > 100:
            self.health = 100

    def collides_with(self, other: 'Entity') -> bool:
        """
        Verifica colisão com outra entidade.

        Args:
            other (Entity): Outra entidade

        Returns:
            bool: True se há colisão
        """
        return self.rect.colliderect(other.rect)

    def distance_to(self, other: 'Entity') -> float:
        """
        Calcula a distância para outra entidade.

        Args:
            other (Entity): Outra entidade

        Returns:
            float: Distância
        """
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx ** 2 + dy ** 2) ** 0.5

    def get_position(self) -> tuple:
        """
        Retorna a posição da entidade.

        Returns:
            tuple: (x, y)
        """
        return (self.x, self.y)

    def set_position(self, x: float, y: float):
        """
        Define a posição da entidade.

        Args:
            x (float): Posição X
            y (float): Posição Y
        """
        self.x = x
        self.y = y
        self.rect.x = int(x)
        self.rect.y = int(y)

    def is_out_of_bounds(self, width: int, height: int) -> bool:
        """
        Verifica se a entidade saiu dos limites da tela.

        Args:
            width (int): Largura da tela
            height (int): Altura da tela

        Returns:
            bool: True se saiu dos limites
        """
        return (self.x < -self.width or
                self.x > width or
                self.y < -self.height or
                self.y > height)

    def __repr__(self) -> str:
        """Representação em string da entidade."""
        return f"{self.__class__.__name__}(name='{self.name}', pos=({self.x}, {self.y}), health={self.health})"