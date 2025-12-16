"""
Módulo de Configuração
======================
Gerencia todas as configurações da aplicação de forma centralizada.
Carrega variáveis de ambiente e configurações de arquivo INI.

Author: Sistema AFN
Date: 2025-12-09
"""

import os
import configparser
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Classe centralizada de configuração da aplicação."""
    
    _instance: Optional['Config'] = None
    
    def __new__(cls) -> 'Config':
        """Implementa padrão Singleton para garantir única instância."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa configurações carregando .env e config.ini."""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._load_env()
        self._load_config_file()
        self._setup_paths()
    
    def _load_env(self) -> None:
        """Carrega variáveis de ambiente do arquivo .env."""
        load_dotenv()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.environment = os.getenv('ENVIRONMENT', 'production')
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY não configurada no arquivo .env")
    
    def _load_config_file(self) -> None:
        """Carrega configurações do arquivo config.ini."""
        config = configparser.ConfigParser()
        config_path = Path('config.ini')
        
        if not config_path.exists():
            raise FileNotFoundError("Arquivo config.ini não encontrado")
        
        config.read(config_path, encoding='utf-8')
        
        # Scraper configurations
        self.base_url = config.get('scraper', 'base_url')
        self.category_url = config.get('scraper', 'category_url')
        target_post_type_raw = config.get('scraper', 'target_post_type')
        # Processa lista de tipos separados por vírgula
        self.target_post_types = [
            t.strip().lower() 
            for t in target_post_type_raw.split(',') 
            if t.strip()
        ]
        # Mantém compatibilidade com código que usa target_post_type (singular)
        self.target_post_type = self.target_post_types[0] if self.target_post_types else ''
        self.scroll_delay = config.getfloat('scraper', 'scroll_delay')
        self.page_load_delay = config.getfloat('scraper', 'page_load_delay')
        
        # Selenium configurations
        self.selenium_headless = config.getboolean('selenium', 'headless')
        self.selenium_timeout = config.getint('selenium', 'timeout')
        self.user_agent = config.get('selenium', 'user_agent')
        
        # File paths
        self.output_posts_csv = config.get('files', 'output_posts_csv')
        self.output_summaries_json = config.get('files', 'output_summaries_json')
        self.database_name = config.get('files', 'database_name')
        
        # OpenAI configurations
        self.openai_model = config.get('openai', 'model')
        self.max_summary_chars = config.getint('openai', 'max_summary_chars')
        self.openai_timeout = config.getint('openai', 'timeout')
        
        # n8n configurations
        webhook_prod = config.get('n8n', 'webhook_url_production')
        webhook_test = config.get('n8n', 'webhook_url_test')
        use_prod = config.getboolean('n8n', 'use_production')
        self.webhook_url = webhook_prod if use_prod else webhook_test
        self.webhook_timeout = config.getint('n8n', 'request_timeout')
        
        # Logging configurations
        self.log_level = config.get('logging', 'log_level')
        self.log_format = config.get('logging', 'log_format')
        self.log_file = config.get('logging', 'log_file')
        self.log_max_bytes = config.getint('logging', 'max_bytes')
        self.log_backup_count = config.getint('logging', 'backup_count')
    
    def _setup_paths(self) -> None:
        """Cria estrutura de diretórios necessária."""
        directories = [
            'logs',
            'database',
            'dados',
            'reports',
            'docs',
            'graphics'
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def get_database_path(self) -> Path:
        """Retorna caminho completo do banco de dados."""
        return Path('database') / self.database_name
    
    def __repr__(self) -> str:
        """Representação string da configuração."""
        return f"Config(environment={self.environment})"


# Instância global de configuração
config = Config()

