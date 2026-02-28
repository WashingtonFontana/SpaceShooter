import pygame
import os


class AssetManager:
    """
    Singleton que gerencia o carregamento de assets (imagens e sons).

    Garante que apenas uma instância exista durante toda a execução do jogo.
    """

    _instance = None

    def __new__(cls, assets_path: str = 'assets'):
        """Implementa o padrão Singleton."""
        if cls._instance is None:
            cls._instance = super(AssetManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, assets_path: str = 'assets'):
        """
        Inicializa o gerenciador de assets.

        Args:
            assets_path (str): Caminho da pasta de assets
        """
        if self._initialized:
            return

        self.assets_path = assets_path
        self.sprites = {}
        self.sounds = {}
        self.music = None
        self._initialized = True

        # Criar pasta se não existir
        if not os.path.exists(self.assets_path):
            os.makedirs(self.assets_path)
            print(f"✓ Pasta de assets criada: {self.assets_path}")

    def load_sprite(self, sprite_name: str, default_size: tuple = (40, 40)) -> pygame.Surface:
        """
        Carrega um sprite (imagem) da pasta assets/.

        Args:
            sprite_name (str): Nome do arquivo (ex: 'player.png')
            default_size (tuple): Tamanho para redimensionar a imagem

        Returns:
            pygame.Surface: Imagem carregada e redimensionada ou superfície colorida padrão
        """
        # Caminho do arquivo
        file_path = os.path.join(self.assets_path, sprite_name)

        try:
            # Tentar carregar a imagem
            if os.path.exists(file_path):
                image = pygame.image.load(file_path)

                # Redimensionar se tamanho foi especificado
                if default_size and len(default_size) == 2:
                    image = pygame.transform.scale(image, (int(default_size[0]), int(default_size[1])))

                self.sprites[sprite_name] = image
                print(f"✓ Sprite carregado: {sprite_name} - Tamanho: {image.get_size()}")
                return image
            else:
                print(f"⚠ Arquivo não encontrado: {file_path}")
                # Retornar superfície padrão
                return self.create_default_surface(default_size)

        except Exception as e:
            print(f"✗ Erro ao carregar sprite {sprite_name}: {e}")
            return self.create_default_surface(default_size)

    def load_sound(self, sound_name: str) -> pygame.mixer.Sound:
        """
        Carrega um som da pasta assets/.

        Args:
            sound_name (str): Nome do arquivo (ex: 'shoot.wav')

        Returns:
            pygame.mixer.Sound: Som carregado ou None
        """
        # Verificar se já foi carregado
        if sound_name in self.sounds:
            return self.sounds[sound_name]

        # Caminho do arquivo
        file_path = os.path.join(self.assets_path, sound_name)

        try:
            # Tentar carregar o som
            if os.path.exists(file_path):
                try:
                    sound = pygame.mixer.Sound(file_path)
                    self.sounds[sound_name] = sound
                    print(f"✓ Som carregado: {sound_name}")
                    return sound
                except pygame.error as e:
                    print(f"⚠ Aviso: Não foi possível carregar som {sound_name}: {e}")
                    return None
            else:
                print(f"⚠ Arquivo de som não encontrado: {file_path}")
                return None

        except Exception as e:
            print(f"✗ Erro ao carregar som {sound_name}: {e}")
            return None

    def load_music(self, music_name: str) -> bool:
        """
        Carrega música de fundo da pasta assets/.

        Args:
            music_name (str): Nome do arquivo (ex: 'background_music.wav')

        Returns:
            bool: True se carregou com sucesso
        """
        # Caminho do arquivo
        file_path = os.path.join(self.assets_path, music_name)

        try:
            # Tentar carregar a música
            if os.path.exists(file_path):
                try:
                    pygame.mixer.music.load(file_path)
                    self.music = music_name
                    print(f"✓ Música carregada: {music_name}")
                    return True
                except pygame.error as e:
                    print(f"⚠ Aviso: Não foi possível carregar música {music_name}: {e}")
                    return False
            else:
                print(f"⚠ Arquivo de música não encontrado: {file_path}")
                return False

        except Exception as e:
            print(f"✗ Erro ao carregar música {music_name}: {e}")
            return False

    def play_sound(self, sound_name: str, loops: int = 0):
        """
        Reproduz um som.

        Args:
            sound_name (str): Nome do som a reproduzir
            loops (int): Número de repetições (0 = uma vez)
        """
        sound = self.load_sound(sound_name)
        if sound:
            sound.play(loops)

    def play_music(self, music_name: str, loops: int = -1):
        """
        Reproduz música de fundo.

        Args:
            music_name (str): Nome da música a reproduzir
            loops (int): Número de repetições (-1 = infinito)
        """
        if self.load_music(music_name):
            pygame.mixer.music.play(loops)

    def stop_music(self):
        """Para a música de fundo."""
        pygame.mixer.music.stop()

    def set_music_volume(self, volume: float):
        """
        Define o volume da música.

        Args:
            volume (float): Volume (0.0 a 1.0)
        """
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))

    def set_sound_volume(self, sound_name: str, volume: float):
        """
        Define o volume de um som.

        Args:
            sound_name (str): Nome do som
            volume (float): Volume (0.0 a 1.0)
        """
        sound = self.load_sound(sound_name)
        if sound:
            sound.set_volume(max(0.0, min(1.0, volume)))

    @staticmethod
    def create_default_surface(size: tuple = (40, 40)) -> pygame.Surface:
        """
        Cria uma superfície padrão quando arquivo não é encontrado.

        Args:
            size (tuple): Tamanho da superfície

        Returns:
            pygame.Surface: Superfície colorida
        """
        surface = pygame.Surface(size)
        surface.fill((100, 100, 100))
        return surface

    def unload_all(self):
        """Descarrega todos os assets."""
        self.sprites.clear()
        self.sounds.clear()
        self.music = None
        print("✓ Todos os assets foram descarregados")

    def list_assets(self):
        """Lista todos os assets disponíveis na pasta."""
        print(f"\n=== Assets em {self.assets_path} ===")

        if os.path.exists(self.assets_path):
            files = os.listdir(self.assets_path)
            if files:
                for file in sorted(files):
                    file_path = os.path.join(self.assets_path, file)
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        print(f"  {file} ({size} bytes)")
            else:
                print("  (pasta vazia)")
        else:
            print("  (pasta não existe)")
