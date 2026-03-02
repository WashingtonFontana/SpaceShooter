import pygame
import os


class AssetManager:
    """
    Singleton que gerencia o carregamento de assets com cache e tratamento de erros.
    """
    _instance = None

    def __new__(cls, path: str = 'assets'):
        if cls._instance is None:
            cls._instance = super(AssetManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, path: str = 'assets'):
        if self._initialized:
            return

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.path = os.path.join(base_dir, path)

        self.sprites = {}
        self.sounds = {}
        self._initialized = True

        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def load_sprite(self, name: str, size: tuple = (40, 40), flip_y: bool = False, rotate: int = 0) -> pygame.Surface:
        """Carrega e transforma sprites com cache para performance."""
        cache_key = f"{name}_{size}_{flip_y}_{rotate}"

        if cache_key in self.sprites:
            return self.sprites[cache_key]

        file_path = os.path.join(self.path, name)
        if os.path.exists(file_path):
            try:
                surface = pygame.image.load(file_path).convert_alpha()
                if size:
                    surface = pygame.transform.scale(surface, size)
                if flip_y:
                    surface = pygame.transform.flip(surface, False, True)
                if rotate != 0:
                    surface = pygame.transform.rotate(surface, rotate)

                self.sprites[cache_key] = surface
                return surface
            except pygame.error:
                print(f"✗ Erro ao carregar imagem: {name}")

        return self._create_fallback(size)

    def load_sound(self, name: str) -> pygame.mixer.Sound:
        """
        Carrega sons garantindo retorno de objeto Sound válido.
        Resolve o erro: Expected type 'Sound', got 'None'.
        """
        if name in self.sounds:
            return self.sounds[name]

        file_path = os.path.join(self.path, name)
        if os.path.exists(file_path):
            try:
                sound = pygame.mixer.Sound(file_path)
                self.sounds[name] = sound
                return sound
            except pygame.error:
                print(f"✗ Erro no formato do som: {name}")

        # Retorna um som silencioso (fallback) para nunca retornar None
        return pygame.mixer.Sound(buffer=bytes([128] * 4410))

    def play_sound(self, name: str, volume: float = 0.5):
        """Reproduz um efeito sonoro usando o carregamento seguro."""
        sound = self.load_sound(name)
        sound.set_volume(max(0.0, min(1.0, volume)))
        sound.play()

    def play_music(self, name: str, volume: float = 0.5, loops: int = -1):
        """Inicia a música de fundo com verificação de existência."""
        file_path = os.path.join(self.path, name)
        if os.path.exists(file_path):
            try:
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
                pygame.mixer.music.play(loops)
            except pygame.error:
                print(f"✗ Falha ao tocar música: {name}")

    @staticmethod
    def stop_music():
        """Para a música global. Marcado como static por não usar 'self'."""
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

    @staticmethod
    def set_music_volume(volume: float):
        """Define o volume global da música. Marcado como static por não usar 'self'."""
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))

    @staticmethod
    def _create_fallback(size: tuple) -> pygame.Surface:
        """Cria superfície magenta para erros visuais."""
        surf = pygame.Surface(size)
        surf.fill((255, 0, 255))
        return surf

    def unload_all(self):
        """Limpa o cache e para o áudio."""
        self.sprites.clear()
        self.sounds.clear()
        self.stop_music()