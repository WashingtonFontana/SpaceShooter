import sqlite3
import os
# O import 'from datetime import datetime' foi removido para eliminar o erro de 'Unused import'
from code.Const import DB_PATH, DB_TABLE_SCORES


class DBProxy:
    """
    Proxy que controla o acesso ao banco de dados SQLite.
    Implementa cache para consultas de High Scores e garante a integridade dos dados.
    """

    def __init__(self, db_path: str = DB_PATH):
        """Inicializa o proxy e configura o banco de dados."""
        self.db_path = db_path
        self.connection = None
        self.cache = {}
        self._table_name = DB_TABLE_SCORES
        self._initialize_db()

    def _initialize_db(self):
        """Cria o diretório e a tabela inicial se não existirem."""
        try:
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)

            self._ensure_connection()
            with self.connection:
                cursor = self.connection.cursor()
                # O campo 'date' usa o timestamp nativo do SQLite
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS {self._table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_name TEXT NOT NULL,
                        score INTEGER NOT NULL,
                        level INTEGER NOT NULL,
                        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            print(f"✓ Banco de dados inicializado em: {os.path.abspath(self.db_path)}")
        except sqlite3.Error as e:
            print(f"✗ Erro ao inicializar banco de dados: {e}")

    def _ensure_connection(self):
        """Garante que a conexão com o banco de dados esteja ativa."""
        try:
            if self.connection is None:
                self.connection = sqlite3.connect(self.db_path, timeout=10.0)
                self.connection.row_factory = sqlite3.Row
            else:
                self.connection.execute('SELECT 1')
        except (sqlite3.Error, AttributeError):
            self.connection = sqlite3.connect(self.db_path, timeout=10.0)

    def save_score(self, player_name: str, score: int, level: int) -> bool:
        """Salva uma nova pontuação e limpa o cache de consultas."""
        try:
            self._ensure_connection()
            name = str(player_name).strip()[:50]

            if not name or score < 0 or level < 1:
                print("⚠ Dados inválidos para salvamento de score.")
                return False

            with self.connection:
                self.connection.execute(
                    f"INSERT INTO {self._table_name} (player_name, score, level) VALUES (?, ?, ?)",
                    (name, int(score), int(level))
                )

            self.cache.clear()
            print(f"✓ Pontuação de {name} salva com sucesso.")
            return True
        except sqlite3.Error as e:
            print(f"✗ Erro ao salvar pontuação: {e}")
            return False

    def get_high_scores(self, limit: int = 10) -> list:
        """Retorna as maiores pontuações usando cache para performance."""
        cache_key = f"high_{limit}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            self._ensure_connection()
            cursor = self.connection.cursor()
            cursor.execute(
                f"SELECT player_name, score, level, date FROM {self._table_name} ORDER BY score DESC LIMIT ?",
                (limit,)
            )
            results = [tuple(row) for row in cursor.fetchall()]
            self.cache[cache_key] = results
            return results
        except sqlite3.Error as e:
            print(f"✗ Erro ao obter High Scores: {e}")
            return []

    def get_total_scores(self) -> int:
        """Retorna o número total de registros salvos."""
        try:
            self._ensure_connection()
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {self._table_name}")
            return cursor.fetchone()[0]
        except sqlite3.Error:
            return 0

    def clear_all_scores(self) -> bool:
        """Remove permanentemente todas as pontuações do banco."""
        try:
            self._ensure_connection()
            with self.connection:
                self.connection.execute(f"DELETE FROM {self._table_name}")
            self.cache.clear()
            return True
        except sqlite3.Error as e:
            print(f"✗ Erro ao limpar scores: {e}")
            return False

    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def __repr__(self) -> str:
        return f"DBProxy(path='{self.db_path}', entries={self.get_total_scores()})"