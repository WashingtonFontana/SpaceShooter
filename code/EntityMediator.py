from code.Const import EVENT_ENEMY_DESTROYED, EVENT_PLAYER_HIT, EVENT_LEVEL_COMPLETE


class EntityMediator:
    """
    Mediator que centraliza a comunicação entre entidades.
    Evita acoplamento direto entre objetos, permitindo comunicação
    através de um intermediário.
    """
    def __init__(self):
        """Inicializa os contadores de pontos, nível e a lista de interessados (listeners)."""
        self.listeners = {} # Dicionário que guarda quem quer ser avisado de cada evento
        self.score = 0
        self.level = 1
        self.enemies_destroyed = 0
        self.player_hits = 0

    def register_listener(self, event_type: str, callback):
        """Cadastra uma função para ser avisada sempre que um evento específico acontecer."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    def unregister_listener(self, event_type: str, callback):
        """Remove um interessado da lista de avisos."""
        if event_type in self.listeners:
            self.listeners[event_type].remove(callback)

    def notify(self, event_type: str, data: dict = None):
        """Envia um alerta para todos que estão "escutando" um determinado evento."""
        if data is None:
            data = {}

        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                callback(data)

    def on_enemy_destroyed(self, enemy_data: dict):
        """Ação disparada quando um inimigo morre: aumenta pontos e avisa o jogo."""
        self.enemies_destroyed += 1
        score_points = enemy_data.get('score', 100)
        self.score += score_points

        # Notifica que um inimigo foi destruído com os dados atualizados
        self.notify(EVENT_ENEMY_DESTROYED, {
            'enemy': enemy_data,
            'score': score_points,
            'total_score': self.score,
            'enemies_destroyed': self.enemies_destroyed
        })

    def on_player_hit(self, damage: int):
        """Ação disparada quando o jogador leva dano: registra o acerto e avisa o jogo."""
        self.player_hits += 1

        # Notifica que o jogador foi atingido
        self.notify(EVENT_PLAYER_HIT, {
            'damage': damage,
            'total_hits': self.player_hits
        })

    def on_level_complete(self, level_data: dict):
        """Ação disparada ao vencer a fase: sobe o nível, soma bônus e avisa o jogo."""
        self.level += 1
        bonus_score = level_data.get('bonus', 500)
        self.score += bonus_score

        # Notifica que a fase foi concluída
        self.notify(EVENT_LEVEL_COMPLETE, {
            'level': self.level - 1,
            'bonus': bonus_score,
            'total_score': self.score
        })

    def get_score(self) -> int:
        """Retorna o total de pontos atual."""
        return self.score

    def get_level(self) -> int:
        """Retorna em qual nível o jogo está."""
        return self.level

    def get_enemies_destroyed(self) -> int:
        """Retorna quantos inimigos foram derrotados no total."""
        return self.enemies_destroyed

    def reset(self):
        """Zera todos os dados para começar uma nova partida limpa."""
        self.score = 0
        self.level = 1
        self.enemies_destroyed = 0
        self.player_hits = 0

    def __repr__(self) -> str:
        """Mostra um resumo rápido do mediador no console para testes."""
        return f"EntityMediator(score={self.score}, level={self.level}, enemies_destroyed={self.enemies_destroyed})"