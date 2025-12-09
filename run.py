"""
Script de Entrada Principal
============================
Ponto de entrada para executar a aplicação.
Este script garante que os imports funcionem corretamente.

Uso:
    python run.py

Author: Sistema AFN
Date: 2025-12-09
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Agora pode importar os módulos
from src.main import main

if __name__ == "__main__":
    sys.exit(main())

