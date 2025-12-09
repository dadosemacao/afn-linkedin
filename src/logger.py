"""
Módulo de Logging Profissional
===============================
Sistema de logging estruturado e profissional sem uso de emojis.
Implementa rotação de logs e diferentes níveis de severidade.

Author: Sistema AFN
Date: 2025-12-09
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from src.config import config


class LoggerFactory:
    """Factory para criação de loggers padronizados."""
    
    _loggers = {}
    _initialized = False
    
    @classmethod
    def _initialize_logging(cls) -> None:
        """Configura o sistema de logging uma única vez."""
        if cls._initialized:
            return
        
        # Garante que o diretório de logs existe
        log_dir = Path(config.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuração do formatter
        formatter = logging.Formatter(config.log_format)
        
        # Handler para arquivo com rotação
        file_handler = RotatingFileHandler(
            config.log_file,
            maxBytes=config.log_max_bytes,
            backupCount=config.log_backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, config.log_level))
        file_handler.setFormatter(formatter)
        
        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Configuração do logger raiz
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, config.log_level))
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        cls._initialized = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Retorna um logger configurado para o módulo especificado.
        
        Args:
            name: Nome do módulo (geralmente __name__)
            
        Returns:
            Logger configurado e pronto para uso
        """
        if not cls._initialized:
            cls._initialize_logging()
        
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger
        
        return cls._loggers[name]
    
    @classmethod
    def log_exception(cls, logger: logging.Logger, message: str, exc: Exception) -> None:
        """
        Loga exceção de forma estruturada.
        
        Args:
            logger: Logger a ser utilizado
            message: Mensagem descritiva do contexto
            exc: Exceção capturada
        """
        logger.error(f"{message}: {type(exc).__name__} - {str(exc)}", exc_info=True)
    
    @classmethod
    def log_operation_start(cls, logger: logging.Logger, operation: str) -> None:
        """Loga início de operação."""
        logger.info(f"INICIO - {operation}")
    
    @classmethod
    def log_operation_end(cls, logger: logging.Logger, operation: str, success: bool = True) -> None:
        """Loga fim de operação."""
        status = "SUCESSO" if success else "FALHA"
        logger.info(f"FIM - {operation} - Status: {status}")


# Função helper para uso direto
def get_logger(name: str) -> logging.Logger:
    """
    Função helper para obter logger rapidamente.
    
    Args:
        name: Nome do módulo (use __name__)
        
    Returns:
        Logger configurado
    """
    return LoggerFactory.get_logger(name)

