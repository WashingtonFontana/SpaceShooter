import sqlite3
import os
from datetime import datetime
from code.Const import DB_PATH, DB_TABLE_SCORES


class DBProxy:
    """
    Proxy que controla o acesso ao banco de dados.

    Implementa cache, validação e controle de acesso.
    """

    def __init__(self, db_path: str = DB_PATH):
        """
        Inicializa o proxy.

        Args:
            db_path (str): Caminho do banco de dados
        """
        self.db_path = db_path
        self.connection = None
        self.cache = {}
        self._initialize_db()

    def _initialize_db(self):
        """Inicializa o banco de dados."""
        try:
            # Garantir que o diretório existe
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)

            # Criar conexão com timeout
            self.connection = sqlite3.connect(self.db_path, timeout=10.0)
            self.connection.isolation_level = None  # Autocommit mode

            cursor = self.connection.cursor()

            # Criar tabela se não existir
            create_table_sql = f'''
                CREATE TABLE IF NOT EXISTS {DB_TABLE_SCORES} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    level INTEGER NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''

            cursor.execute(create_table_sql)
            self.connection.commit()

            print(f"✓ Banco de dados inicializado: {os.path.abspath(self.db_path)}")
            print(f"✓ Conexão SQLite estabelecida com sucesso")

        except Exception as e:
            print(f"✗ Erro ao inicializar banco de dados: {e}")
            print(f"✗ Caminho tentado: {os.path.abspath(self.db_path)}")

    def _ensure_connection(self):
        """Garante que a conexão está aberta."""
        try:
            if self.connection is None:
                self.connection = sqlite3.connect(self.db_path, timeout=10.0)
                self.connection.isolation_level = None
                print("✓ Conexão com banco de dados restaurada")
            else:
                # Testar se a conexão está viva
                self.connection.execute('SELECT 1')
        except Exception as e:
            print(f"⚠ Reconectando ao banco de dados: {e}")
            try:
                self.connection = sqlite3.connect(self.db_path, timeout=10.0)
                self.connection.isolation_level = None
            except Exception as e2:
                print(f"✗ Erro ao reconectar: {e2}")

    def save_score(self, player_name: str, score: int, level: int) -> bool:
        """
        Salva uma pontuação no banco de dados.

        Args:
            player_name (str): Nome do jogador
            score (int): Pontuação
            level (int): Nível alcançado

        Returns:
            bool: True se salvo com sucesso
        """
        try:
            # Garantir conexão
            self._ensure_connection()

            # Converter para tipos primitivos
            player_name = str(player_name).strip()
            score = int(score)
            level = int(level)

            # Validar entrada
            if not player_name or len(player_name) > 50:
                print("✗ Nome do jogador inválido")
                return False

            if score < 0 or level < 1:
                print("✗ Pontuação ou nível inválido")
                return False

            # Inserir no banco de dados
            cursor = self.connection.cursor()

            insert_sql = f'''
                INSERT INTO {DB_TABLE_SCORES} (player_name, score, level)
                VALUES (?, ?, ?)
            '''

            cursor.execute(insert_sql, (player_name, score, level))
            self.connection.commit()

            print(f"✓ Pontuação salva com sucesso: {player_name} - {score} pontos - Nível {level}")

            # Limpar cache
            self.cache.clear()
            return True

        except sqlite3.OperationalError as e:
            print(f"✗ Erro operacional do SQLite: {e}")
            return False
        except sqlite3.IntegrityError as e:
            print(f"✗ Erro de integridade do banco de dados: {e}")
            return False
        except Exception as e:
            print(f"✗ Erro ao salvar pontuação: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_high_scores(self, limit: int = 10) -> list:
        """
        Obtém as maiores pontuações.

        Args:
            limit (int): Quantidade de pontuações a retornar

        Returns:
            list: Lista de pontuações
        """
        try:
            # Garantir conexão
            self._ensure_connection()

            # Verificar cache
            cache_key = f'high_scores_{limit}'
            if cache_key in self.cache:
                return self.cache[cache_key]

            # Buscar do banco de dados
            cursor = self.connection.cursor()

            select_sql = f'''
                SELECT player_name, score, level, date
                FROM {DB_TABLE_SCORES}
                ORDER BY score DESC
                LIMIT ?
            '''

            cursor.execute(select_sql, (limit,))
            scores = cursor.fetchall()

            # Armazenar em cache
            self.cache[cache_key] = scores

            return scores

        except Exception as e:
            print(f"✗ Erro ao obter pontuações: {e}")
            return []

    def get_player_scores(self, player_name: str) -> list:
        """
        Obtém as pontuações de um jogador específico.

        Args:
            player_name (str): Nome do jogador

        Returns:
            list: Lista de pontuações do jogador
        """
        try:
            # Garantir conexão
            self._ensure_connection()

            # Verificar cache
            cache_key = f'player_scores_{player_name}'
            if cache_key in self.cache:
                return self.cache[cache_key]

            # Buscar do banco de dados
            cursor = self.connection.cursor()

            select_sql = f'''
                SELECT player_name, score, level, date
                FROM {DB_TABLE_SCORES}
                WHERE player_name = ?
                ORDER BY score DESC
            '''

            cursor.execute(select_sql, (player_name,))
            scores = cursor.fetchall()

            # Armazenar em cache
            self.cache[cache_key] = scores

            return scores

        except Exception as e:
            print(f"✗ Erro ao obter pontuações do jogador: {e}")
            return []

    def get_total_scores(self) -> int:
        """
        Obtém a quantidade total de pontuações salvas.

        Returns:
            int: Quantidade
        """
        try:
            # Garantir conexão
            self._ensure_connection()

            cursor = self.connection.cursor()
            cursor.execute(f'SELECT COUNT(*) FROM {DB_TABLE_SCORES}')
            count = cursor.fetchone()[0]
            return count

        except Exception as e:
            print(f"✗ Erro ao contar pontuações: {e}")
            return 0

    def delete_score(self, score_id: int) -> bool:
        """
        Deleta uma pontuação.

        Args:
            score_id (int): ID da pontuação

        Returns:
            bool: True se deletado com sucesso
        """
        try:
            # Garantir conexão
            self._ensure_connection()

            cursor = self.connection.cursor()
            cursor.execute(f'DELETE FROM {DB_TABLE_SCORES} WHERE id = ?', (score_id,))
            self.connection.commit()

            # Limpar cache
            self.cache.clear()

            print(f"✓ Pontuação deletada: ID {score_id}")
            return True

        except Exception as e:
            print(f"✗ Erro ao deletar pontuação: {e}")
            return False

    def clear_all_scores(self) -> bool:
        """
        Deleta todas as pontuações.

        Returns:
            bool: True se deletado com sucesso
        """
        try:
            # Garantir conexão
            self._ensure_connection()

            cursor = self.connection.cursor()
            cursor.execute(f'DELETE FROM {DB_TABLE_SCORES}')
            self.connection.commit()

            # Limpar cache
            self.cache.clear()

            print("✓ Todas as pontuações foram deletadas")
            return True

        except Exception as e:
            print(f"✗ Erro ao deletar pontuações: {e}")
            return False

    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.connection:
            try:
                self.connection.close()
                print("✓ Conexão com banco de dados fechada")
            except Exception as e:
                print(f"⚠ Erro ao fechar conexão: {e}")

    def __del__(self):
        """Destrutor que fecha a conexão."""
        self.close()

    def __repr__(self) -> str:
        """Representação em string do proxy."""
        return f"DBProxy(db_path='{self.db_path}', total_scores={self.get_total_scores()})"