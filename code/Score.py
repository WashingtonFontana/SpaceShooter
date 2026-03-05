from code.DBProxy import DBProxy
from code.Const import SCORE_ENEMY_DESTROYED, SCORE_LEVEL_COMPLETE, SCORE_BONUS_TIME


class Score:
    """Classe que controla os pontos e recordes do jogo."""

    def __init__(self, player_name: str = 'Player', db_proxy: DBProxy = None):
        """Prepara o sistema de pontos e busca o recorde no banco de dados."""
        self.current_score = 0
        self.high_score = 0
        self.player_name = player_name
        self.level = 1
        self.observers = []  # Lista de módulos que precisam saber quando o ponto muda
        self.db_proxy = db_proxy or DBProxy()

        # Carrega o recorde atual assim que o jogo começa
        self._load_high_score()

    def _load_high_score(self):
        """Busca no banco de dados qual foi a maior pontuação até hoje."""
        try:
            scores = self.db_proxy.get_high_scores(limit=1)
            if scores:
                self.high_score = scores[0][1]
        except Exception as e:
            print(f"⚠ Erro ao carregar recorde: {e}")

    def add_score(self, points: int):
        """Soma pontos ao total e avisa a interface para atualizar o desenho."""
        self.current_score += points
        self.notify_observers('score_changed', {
            'score': self.current_score,
            'points_added': points
        })

    def add_enemy_destroyed_score(self):
        """Dá pontos por destruir um inimigo."""
        self.add_score(SCORE_ENEMY_DESTROYED)

    def add_level_complete_score(self):
        """Dá pontos por passar de fase."""
        self.add_score(SCORE_LEVEL_COMPLETE)

    def add_time_bonus(self, seconds_remaining: int):
        """Calcula e dá bônus se o jogador terminou a fase rápido."""
        bonus = seconds_remaining * SCORE_BONUS_TIME
        self.add_score(bonus)

    def set_level(self, level: int):
        """Atualiza em qual fase o jogador está."""
        self.level = level
        self.notify_observers('level_changed', {'level': level})

    def save_score(self) -> bool:
        """Salva os pontos no banco e verifica se o jogador bateu o próprio recorde."""
        success = self.db_proxy.save_score(self.player_name, self.current_score, self.level)

        # Se bateu o recorde, atualiza o valor e avisa o jogo
        if success and self.current_score > self.high_score:
            self.high_score = self.current_score
            self.notify_observers('high_score_achieved', {
                'high_score': self.high_score
            })

        return success

    def get_high_scores(self, limit: int = 10) -> list:
        """Retorna a lista dos melhores jogadores do ranking."""
        return self.db_proxy.get_high_scores(limit)

    def reset(self):
        """Zera os pontos e o nível para começar um novo jogo do zero."""
        self.current_score = 0
        self.level = 1
        self.notify_observers('score_reset', {})

    def attach_observer(self, observer):
        """Adiciona um módulo (como o HUD da tela) para receber atualizações."""
        self.observers.append(observer)

    def detach_observer(self, observer):
        """Remove um módulo da lista de atualizações."""
        self.observers.remove(observer)

    def notify_observers(self, event_type: str, data: dict):
        """Envia um alerta para todos os módulos conectados sobre uma mudança nos pontos."""
        for observer in self.observers:
            observer.update(event_type, data)

    def __repr__(self) -> str:
        """Mostra as informações do Score de forma organizada no console."""
        return f"Score(player='{self.player_name}', current={self.current_score}, high={self.high_score}, level={self.level})"