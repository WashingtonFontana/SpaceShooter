from code.Const import EVENT_ENEMY_DESTROYED, EVENT_PLAYER_HIT, EVENT_LEVEL_COMPLETE


class EntityMediator:
    """
    Mediator que centraliza a comunicação entre entidades.

    Evita acoplamento direto entre objetos, permitindo comunicação
    através de um intermediário.
    """

    def __init__(self):
        """Inicializa o mediator."""
        self.listeners = {}
        self.score = 0
        self.level = 1
        self.enemies_destroyed = 0
        self.player_hits = 0

    def register_listener(self, event_type: str, callback):
        """
        Registra um listener para um tipo de evento.

        Args:
            event_type (str): Tipo de evento
            callback: Função a ser chamada quando o evento ocorrer
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    def unregister_listener(self, event_type: str, callback):
        """
        Remove um listener.

        Args:
            event_type (str): Tipo de evento
            callback: Função a ser removida
        """
        if event_type in self.listeners:
            self.listeners[event_type].remove(callback)

    def notify(self, event_type: str, data: dict = None):
        """
        Notifica todos os listeners de um evento.

        Args:
            event_type (str): Tipo de evento
            data (dict): Dados do evento
        """
        if data is None:
            data = {}

        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                callback(data)

    def on_enemy_destroyed(self, enemy_data: dict):
        """
        Chamado quando um inimigo é destruído.

        Args:
            enemy_data (dict): Dados do inimigo
        """
        self.enemies_destroyed += 1
        score_points = enemy_data.get('score', 100)
        self.score += score_points

        # Notificar listeners
        self.notify(EVENT_ENEMY_DESTROYED, {
            'enemy': enemy_data,
            'score': score_points,
            'total_score': self.score,
            'enemies_destroyed': self.enemies_destroyed
        })

    def on_player_hit(self, damage: int):
        """
        Chamado quando o jogador é atingido.

        Args:
            damage (int): Dano recebido
        """
        self.player_hits += 1

        # Notificar listeners
        self.notify(EVENT_PLAYER_HIT, {
            'damage': damage,
            'total_hits': self.player_hits
        })

    def on_level_complete(self, level_data: dict):
        """
        Chamado quando um nível é completado.

        Args:
            level_data (dict): Dados do nível
        """
        self.level += 1
        bonus_score = level_data.get('bonus', 500)
        self.score += bonus_score

        # Notificar listeners
        self.notify(EVENT_LEVEL_COMPLETE, {
            'level': self.level - 1,
            'bonus': bonus_score,
            'total_score': self.score
        })

    def get_score(self) -> int:
        """
        Retorna a pontuação atual.

        Returns:
            int: Pontuação
        """
        return self.score

    def get_level(self) -> int:
        """
        Retorna o nível atual.

        Returns:
            int: Nível
        """
        return self.level

    def get_enemies_destroyed(self) -> int:
        """
        Retorna a quantidade de inimigos destruídos.

        Returns:
            int: Quantidade
        """
        return self.enemies_destroyed

    def reset(self):
        """Reseta o mediator."""
        self.score = 0
        self.level = 1
        self.enemies_destroyed = 0
        self.player_hits = 0

    def __repr__(self) -> str:
        """Representação em string do mediator."""
        return f"EntityMediator(score={self.score}, level={self.level}, enemies_destroyed={self.enemies_destroyed})"