"""
Módulo de Gerenciamento de Banco de Dados
==========================================
Gerencia persistência de dados processados usando SQLite.

Author: Sistema AFN
Date: 2025-12-09
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import List, Set
from src.config import config
from src.logger import get_logger


logger = get_logger(__name__)


class DatabaseManager:
    """Gerenciador de banco de dados SQLite."""
    
    def __init__(self, db_path: Path = None):
        """
        Inicializa gerenciador de banco de dados.
        
        Args:
            db_path: Caminho do banco de dados (usa config se não fornecido)
        """
        self.db_path = db_path or config.get_database_path()
        self._ensure_database_exists()
        logger.info(f"DatabaseManager inicializado: {self.db_path}")
    
    def _ensure_database_exists(self) -> None:
        """Garante que o banco de dados e tabelas existem."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS processados (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        link TEXT UNIQUE NOT NULL,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_link 
                    ON processados(link);
                """)
                
                conn.commit()
                logger.debug("Tabelas de banco de dados verificadas/criadas")
                
        except sqlite3.Error as exc:
            logger.error(f"Erro ao criar estrutura do banco: {str(exc)}")
            raise
    
    @contextmanager
    def _get_connection(self):
        """
        Context manager para conexões com banco de dados.
        Garante fechamento adequado da conexão.
        
        Yields:
            Conexão SQLite
        """
        conn = sqlite3.connect(str(self.db_path))
        try:
            yield conn
        finally:
            conn.close()
    
    def mark_as_processed(self, link: str) -> bool:
        """
        Marca link como processado no banco de dados.
        
        Args:
            link: URL do post processado
            
        Returns:
            True se inserido com sucesso, False se já existia
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO processados (link) VALUES (?)",
                    (link,)
                )
                conn.commit()
                
                was_inserted = cursor.rowcount > 0
                if was_inserted:
                    logger.debug(f"Link marcado como processado: {link}")
                
                return was_inserted
                
        except sqlite3.Error as exc:
            logger.error(f"Erro ao marcar link como processado: {str(exc)}")
            return False
    
    def is_processed(self, link: str) -> bool:
        """
        Verifica se link já foi processado.
        
        Args:
            link: URL a verificar
            
        Returns:
            True se já foi processado
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT 1 FROM processados WHERE link = ? LIMIT 1",
                    (link,)
                )
                return cursor.fetchone() is not None
                
        except sqlite3.Error as exc:
            logger.error(f"Erro ao verificar link processado: {str(exc)}")
            return False
    
    def get_all_processed_links(self) -> Set[str]:
        """
        Retorna conjunto de todos os links processados.
        
        Returns:
            Set com URLs processadas
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT link FROM processados")
                links = {row[0] for row in cursor.fetchall()}
                logger.debug(f"Recuperados {len(links)} links processados")
                return links
                
        except sqlite3.Error as exc:
            logger.error(f"Erro ao recuperar links processados: {str(exc)}")
            return set()
    
    def filter_unprocessed(self, links: List[str]) -> List[str]:
        """
        Filtra lista de links removendo os já processados.
        
        Args:
            links: Lista de URLs a filtrar
            
        Returns:
            Lista apenas com URLs não processados
        """
        processed = self.get_all_processed_links()
        unprocessed = [link for link in links if link not in processed]
        
        logger.info(
            f"Filtrados {len(links)} links: "
            f"{len(unprocessed)} nao processados, "
            f"{len(links) - len(unprocessed)} ja processados"
        )
        
        return unprocessed
    
    def get_statistics(self) -> dict:
        """
        Retorna estatísticas do banco de dados.
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM processados")
                total = cursor.fetchone()[0]
                
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM processados 
                    WHERE DATE(processed_at) = DATE('now')
                    """
                )
                today = cursor.fetchone()[0]
                
                return {
                    'total_processed': total,
                    'processed_today': today
                }
                
        except sqlite3.Error as exc:
            logger.error(f"Erro ao obter estatísticas: {str(exc)}")
            return {'total_processed': 0, 'processed_today': 0}

