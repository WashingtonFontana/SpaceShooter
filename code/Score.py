from code.DBProxy import DBProxy
from code.Const import SCORE_ENEMY_DESTROYED, SCORE_LEVEL_COMPLETE, SCORE_BONUS_TIME


class Score:
    """
    Classe que gerencia a pontuação do jogo.

    Atributos:
        current_score (int): Pontuação atual
        high_score (int): Maior pontuação
        player_name (str): Nome do jogador
        level (int): Nível atual
        observers (list): Lista de observers
        db_proxy (DBProxy): Proxy do banco de dados
    """

    def __init__(self, player_name: str = 'Player', db_proxy: DBProxy = None):
        """
        Inicializa o gerenciador de pontuação.

        Args:
            player_name (str): Nome do jogador
            db_proxy (DBProxy): Proxy do banco de dados
        """
        self.current_score = 0
        self.high_score = 0
        self.player_name = player_name
        self.level = 1
        self.observers = []
        self.db_proxy = db_proxy or DBProxy()

        # Carregar maior pontuação do banco de dados
        self._load_high_score()

    def _load_high_score(self):
        """Carrega a maior pontuação do banco de dados."""
        try:
            scores = self.db_proxy.get_high_scores(limit=1)
            if scores:
                self.high_score = scores[0][1]  # score está no índice 1
        except Exception as e:
            print(f"⚠ Erro ao carregar maior pontuação: {e}")

    def add_score(self, points: int):
        """
        Adiciona pontos à pontuação.

        Args:
            points (int): Quantidade de pontos
        """
        self.current_score += points
        self.notify_observers('score_changed', {
            'score': self.current_score,
            'points_added': points
        })

    def add_enemy_destroyed_score(self):
        """Adiciona pontos por inimigo destruído."""
        self.add_score(SCORE_ENEMY_DESTROYED)

    def add_level_complete_score(self):
        """Adiciona pontos por completar um nível."""
        self.add_score(SCORE_LEVEL_COMPLETE)

    def add_time_bonus(self, seconds_remaining: int):
        """
        Adiciona bônus de tempo.

        Args:
            seconds_remaining (int): Segundos restantes
        """
        bonus = seconds_remaining * SCORE_BONUS_TIME
        self.add_score(bonus)

    def set_level(self, level: int):
        """
        Define o nível atual.

        Args:
            level (int): Nível
        """
        self.level = level
        self.notify_observers('level_changed', {'level': level})

    def save_score(self) -> bool:
        """
        Salva a pontuação no banco de dados.

        Returns:
            bool: True se salvo com sucesso
        """
        success = self.db_proxy.save_score(self.player_name, self.current_score, self.level)

        if success and self.current_score > self.high_score:
            self.high_score = self.current_score
            self.notify_observers('high_score_achieved', {
                'high_score': self.high_score
            })

        return success

    def get_high_scores(self, limit: int = 10) -> list:
        """
        Obtém as maiores pontuações.

        Args:
            limit (int): Quantidade de pontuações

        Returns:
            list: Lista de pontuações
        """
        return self.db_proxy.get_high_scores(limit)

    def reset(self):
        """Reseta a pontuação."""
        self.current_score = 0
        self.level = 1
        self.notify_observers('score_reset', {})

    def attach_observer(self, observer):
        """
        Anexa um observer.

        Args:
            observer: Observer a ser anexado
        """
        self.observers.append(observer)

    def detach_observer(self, observer):
        """
        Remove um observer.

        Args:
            observer: Observer a ser removido
        """
        self.observers.remove(observer)

    def notify_observers(self, event_type: str, data: dict):
        """
        Notifica todos os observers.

        Args:
            event_type (str): Tipo de evento
            data (dict): Dados do evento
        """
        for observer in self.observers:
            observer.update(event_type, data)

    def __repr__(self) -> str:
        """Representação em string do gerenciador de pontuação."""
        return f"Score(player='{self.player_name}', current={self.current_score}, high={self.high_score}, level={self.level})"