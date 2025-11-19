import sqlite3
from datetime import datetime
from logger import GameLogger 

class DatabaseManager:
    def __init__(self):
        self.db_file = 'ranking.db'
        self.logger = GameLogger()
        self._initialize_db()

    def _initialize_db(self):
        """Cria a tabela de scores se ela não existir e garante a integridade da conexão."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    difficulty TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.commit()
            self.logger.log_info("Banco de dados do ranking inicializado com sucesso.")
        except sqlite3.Error as e:
            self.logger.log_error(f"Erro ao inicializar o banco de dados: {e}")
        finally:
            if conn:
                conn.close()

    def save_score(self, name, score, difficulty):
        """Salva a pontuação no banco de dados e garante o commit."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if name == "Player Temp":
            name = "Player"

        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scores (name, score, difficulty, timestamp)
                VALUES (?, ?, ?, ?)
            """, (name, score, difficulty, timestamp))
            
            conn.commit() 
            self.logger.log_info(f"Pontuação salva: {score} ({difficulty})")
        except sqlite3.Error as e:
            self.logger.log_error(f"Falha ao salvar pontuação no DB: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()

    def get_top_scores(self):
        """Recupera as 10 melhores pontuações para exibição no ranking."""
        scores = []
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, score, difficulty, timestamp 
                FROM scores 
                ORDER BY score DESC, timestamp ASC 
                LIMIT 10
            """)
            scores = cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.log_error(f"Falha ao buscar ranking no DB: {e}")
            return []
        finally:
            if conn:
                conn.close()
        
        return scores