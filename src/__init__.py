"""
Databricks Post Processor
==========================
Sistema profissional de scraping, processamento com IA e integração.

Author: Sistema AFN
Date: 2025-12-09
Version: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "Sistema AFN"
__description__ = "Sistema profissional de scraping e processamento de posts Databricks"

# Exports principais
from src.main import Application
from src.config import config
from src.logger import get_logger

__all__ = [
    'Application',
    'config',
    'get_logger',
]

