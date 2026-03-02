import pygame
import os

# ============================================================================
# CONFIGURAÇÕES DA JANELA
# ============================================================================
WIN_WIDTH = 1024
WIN_HEIGHT = 768
WIN_TITLE = "SPACE SHOOTER"
FPS = 60
BACKGROUND_COLOR = (0, 0, 0)

# ============================================================================
# CORES (Exigidas pelo Menu.py e HUD)
# ============================================================================
C_WHITE = (255, 255, 255)
C_BLACK = (0, 0, 0)
C_RED = (255, 0, 0)
C_GREEN = (0, 255, 0)
C_BLUE = (0, 0, 255)
C_YELLOW = (255, 255, 0)
C_CYAN = (0, 255, 255)
C_MAGENTA = (255, 0, 255)
C_GRAY = (128, 128, 128)
C_LIGHT_GRAY = (200, 200, 200)
C_DARK_GRAY = (50, 50, 50)
C_ORANGE = (255, 165, 0)
C_PURPLE = (128, 0, 128)

# ============================================================================
# EVENTOS CUSTOMIZADOS (Exigidos pelo EntityMediator.py)
# ============================================================================
EVENT_ENEMY_DESTROYED = pygame.USEREVENT + 1
EVENT_PLAYER_HIT = pygame.USEREVENT + 2
EVENT_LEVEL_COMPLETE = pygame.USEREVENT + 3
EVENT_GAME_OVER = pygame.USEREVENT + 4

# ============================================================================
# PONTUAÇÃO (Correção do ImportError no Score.py)
# ============================================================================
SCORE_ENEMY_DESTROYED = 100
SCORE_LEVEL_COMPLETE = 500
SCORE_BONUS_TIME = 10  # Restaurado para o Score.py funcionar

# ============================================================================
# INIMIGOS E JOGADOR (Balanceamento de Combate)
# ============================================================================
ENEMY_HEALTH = 1
ENEMY_SHOOT_INTERVAL = 45
ENEMY_SHOOT_CHANCE = 0.35
ENEMY_SPEED = 2
ENEMY_SHOT_SPEED = 4

PLAYER_HEALTH = 100
PLAYER_SPEED = 6
PLAYER_SHOT_SPEED = 12
PLAYER_SHOOT_INTERVAL = 12

# ============================================================================
# TAMANHOS DE ENTIDADES
# ============================================================================
ENTITY_SIZE = {
    'Player': 45,
    'Enemy': 40,
    'PlayerShot': 10,
    'EnemyShot': 8,
    'Explosion': 55
}

# ============================================================================
# MENU E INSTRUÇÕES (Exigidos pelo Menu.py)
# ============================================================================
MENU_OPTIONS = {
    'title': 'SPACE SHOOTER',
    'subtitle': 'Defend the Galaxy',
    'options': [
        {'id': 0, 'label': 'NEW GAME', 'color': (50, 150, 200), 'hover_color': (100, 200, 255)},
        {'id': 1, 'label': 'HIGH SCORES', 'color': (150, 100, 200), 'hover_color': (200, 150, 255)},
        {'id': 2, 'label': 'EXIT', 'color': (200, 50, 50), 'hover_color': (255, 100, 100)}
    ]
}

GAME_INSTRUCTIONS = {
    "title": "CONTROLES",
    "instructions": [
        "SETA CIMA - Mover para cima",
        "SETA BAIXO - Mover para baixo",
        "SETA ESQUERDA - Mover esquerda",
        "SETA DIREITA - Mover direita",
        "SPACE - Atirar",
        "ESC - Sair"
    ]
}

# ============================================================================
# ESTADOS DE JOGO E CONTROLES
# ============================================================================
GAME_STATE_MENU = 'menu'
GAME_STATE_PLAYING = 'playing'
GAME_STATE_GAME_OVER = 'game_over'
GAME_STATE_WIN = 'win'

PLAYER_KEY_LEFT = pygame.K_LEFT
PLAYER_KEY_RIGHT = pygame.K_RIGHT
PLAYER_KEY_UP = pygame.K_UP
PLAYER_KEY_DOWN = pygame.K_DOWN
PLAYER_KEY_SHOOT = pygame.K_SPACE
PLAYER_KEY_ESCAPE = pygame.K_ESCAPE

# ============================================================================
# BANCO DE DADOS E ASSETS
# ============================================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'scores.db')
DB_TABLE_SCORES = 'scores'

ASSETS_PATH = 'assets'

# Lista de backgrounds para troca de fases
SPRITE_BACKGROUNDS = [
    'background.png',
    'background_1.png',
    'background_2.webp',
    'background_3.png'
]

# Outros Sprites
SPRITE_PLAYER = 'player.png'
SPRITE_ENEMY = 'enemy.png'
SPRITE_PLAYER_SHOT = 'player_shot.png'
SPRITE_ENEMY_SHOT = 'enemy_shot.png'
SPRITE_EXPLOSION = 'explosion.png'

SOUND_PLAYER_SHOOT = 'player_shoot.wav'
SOUND_ENEMY_SHOOT = 'enemy_shoot.wav'
SOUND_EXPLOSION = 'explosion.wav'
SOUND_PLAYER_HIT = 'player_hit.wav'
MUSIC_BACKGROUND = 'Fund_music.mp3'
MUSIC_MENU = 'Menu.mp3'

# ============================================================================
# DIFICULDADE
# ============================================================================
DIFFICULTY_NORMAL = 'normal'
DIFFICULTY_SETTINGS = {
    'easy': {'enemy_speed': 1.5, 'enemy_shoot_chance': 0.15, 'player_health': 150, 'enemy_health': 1},
    'normal': {'enemy_speed': 2.0, 'enemy_shoot_chance': 0.35, 'player_health': 100, 'enemy_health': 1},
    'hard': {'enemy_speed': 3.5, 'enemy_shoot_chance': 0.55, 'player_health': 60, 'enemy_health': 2}
}