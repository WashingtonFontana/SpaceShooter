import pygame
from abc import ABC, abstractmethod

# Classe base para todos os objetos do jogo (Jogador, Inimigos, Tiros
class Entity(ABC):

    def __init__(self, name: str, x: float, y: float, width: int = 40, height: int = 40):
        """Define os atributos básicos: nome, posição, tamanho e vida."""
        self.name = name
        self.x = x
        self.y = y
        self.vx = 0.0  # Velocidade horizontal
        self.vy = 0.0  # Velocidade vertical
        self.width = width
        self.height = height
        self.health = 100
        self.is_alive = True

        # Cria a representação visual básica e o retângulo de colisão
        self.image = pygame.Surface((width, height))
        self.image.fill((128, 128, 128))  # Cor cinza padrão
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    @abstractmethod
    def update(self):
        """Lógica de atualização (deve ser criada em cada objeto específico)."""
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        """Desenho na tela (deve ser criado em cada objeto específico)."""
        pass

    def move(self, dx: float, dy: float):
        """Altera a posição x/y e sincroniza o retângulo de colisão."""
        self.x += dx
        self.y += dy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def set_velocity(self, vx: float, vy: float):
        """Define a velocidade de movimento nos dois eixos."""
        self.vx = vx
        self.vy = vy

    def apply_velocity(self):
        """Faz a entidade se mover automaticamente usando sua velocidade atual."""
        self.move(self.vx, self.vy)

    def take_damage(self, damage: int):
        """Reduz a saúde e marca a entidade como morta se chegar a zero."""
        self.health -= damage
        if self.health <= 0:
            self.is_alive = False

    def heal(self, amount: int):
        """Recupera saúde sem ultrapassar o limite de 100."""
        self.health += amount
        if self.health > 100:
            self.health = 100

    def collides_with(self, other: 'Entity') -> bool:
        """Checa se o retângulo desta entidade encostou no de outra."""
        return self.rect.colliderect(other.rect)

    def distance_to(self, other: 'Entity') -> float:
        """Calcula a distância em linha reta até outra entidade."""
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx ** 2 + dy ** 2) ** 0.5

    def get_position(self) -> tuple:
        """Retorna as coordenadas atuais (x, y)."""
        return (self.x, self.y)

    def set_position(self, x: float, y: float):
        """Teletransporta a entidade para uma nova coordenada."""
        self.x = x
        self.y = y
        self.rect.x = int(x)
        self.rect.y = int(y)

    def is_out_of_bounds(self, width: int, height: int) -> bool:
        """Verifica se o objeto saiu completamente da área visível da tela."""
        return (self.x < -self.width or
                self.x > width or
                self.y < -self.height or
                self.y > height)

    def __repr__(self) -> str:
        """Mostra o nome e estado da entidade no console (útil para testes)."""
        return f"{self.__class__.__name__}(name='{self.name}', pos=({self.x}, {self.y}), health={self.health})"