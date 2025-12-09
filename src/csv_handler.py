"""
Módulo de Gerenciamento de CSV
===============================
Operações de leitura e escrita de arquivos CSV.

Author: Sistema AFN
Date: 2025-12-09
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional

from src.config import config
from src.logger import get_logger


logger = get_logger(__name__)


class CSVHandler:
    """Gerenciador de operações com arquivos CSV."""
    
    def __init__(self, csv_path: Path = None):
        """
        Inicializa handler CSV.
        
        Args:
            csv_path: Caminho do arquivo CSV (usa config se não fornecido)
        """
        self.csv_path = csv_path or Path(config.output_posts_csv)
        logger.info(f"CSVHandler inicializado: {self.csv_path}")
    
    def load_posts(self) -> List[Dict[str, str]]:
        """
        Carrega posts do arquivo CSV.
        
        Returns:
            Lista de dicionários com posts
        """
        if not self.csv_path.exists():
            logger.warning(f"Arquivo CSV nao encontrado: {self.csv_path}")
            return []
        
        try:
            df = pd.read_csv(self.csv_path, encoding='utf-8')
            
            # Garante colunas necessárias
            if 'resumo' not in df.columns:
                df['resumo'] = ''
            if 'data_resumo' not in df.columns:
                df['data_resumo'] = ''
            
            posts = df.to_dict('records')
            logger.info(f"Carregados {len(posts)} posts do CSV")
            
            return posts
            
        except Exception as exc:
            logger.error(f"Erro ao carregar CSV: {str(exc)}")
            return []
    
    def save_posts(self, posts: List[Dict[str, str]], remove_duplicates: bool = True) -> bool:
        """
        Salva posts no arquivo CSV.
        
        Args:
            posts: Lista de posts
            remove_duplicates: Se deve remover duplicatas por link
            
        Returns:
            True se sucesso
        """
        if not posts:
            logger.warning("Nenhum post para salvar")
            return False
        
        try:
            df = pd.DataFrame(posts)
            
            # Remove duplicatas se solicitado
            if remove_duplicates and 'link' in df.columns:
                original_count = len(df)
                df = df.drop_duplicates(subset=['link'], keep='last')
                removed = original_count - len(df)
                
                if removed > 0:
                    logger.info(f"Removidas {removed} duplicatas do CSV")
            
            # Salva CSV
            df.to_csv(self.csv_path, index=False, encoding='utf-8')
            logger.info(f"Salvos {len(df)} posts no CSV: {self.csv_path}")
            
            return True
            
        except Exception as exc:
            logger.error(f"Erro ao salvar CSV: {str(exc)}")
            return False
    
    def append_post(self, post: Dict[str, str]) -> bool:
        """
        Adiciona post ao CSV existente.
        
        Args:
            post: Dicionário com dados do post
            
        Returns:
            True se sucesso
        """
        existing_posts = self.load_posts()
        existing_posts.append(post)
        return self.save_posts(existing_posts)
    
    def update_posts(self, posts: List[Dict[str, str]]) -> bool:
        """
        Atualiza posts existentes no CSV baseado no link.
        
        Args:
            posts: Lista de posts com dados atualizados
            
        Returns:
            True se sucesso
        """
        existing_posts = self.load_posts()
        
        # Cria mapa de links para índices
        link_map = {post.get('link'): idx for idx, post in enumerate(existing_posts)}
        
        # Atualiza posts existentes
        updated_count = 0
        for post in posts:
            link = post.get('link')
            if link in link_map:
                idx = link_map[link]
                existing_posts[idx].update(post)
                updated_count += 1
            else:
                existing_posts.append(post)
        
        logger.info(f"Atualizados {updated_count} posts existentes")
        
        return self.save_posts(existing_posts)
    
    def get_posts_without_summaries(self) -> List[Dict[str, str]]:
        """
        Retorna posts que não possuem resumo.
        
        Returns:
            Lista de posts sem resumo
        """
        posts = self.load_posts()
        
        posts_without_summary = [
            post for post in posts
            if not post.get('resumo') or post.get('resumo').strip() == ''
        ]
        
        logger.info(
            f"Encontrados {len(posts_without_summary)} posts sem resumo "
            f"de {len(posts)} totais"
        )
        
        return posts_without_summary
    
    def validate_csv_structure(self) -> bool:
        """
        Valida estrutura do CSV.
        
        Returns:
            True se estrutura válida
        """
        if not self.csv_path.exists():
            return False
        
        try:
            df = pd.read_csv(self.csv_path, nrows=1)
            required_columns = ['post_type', 'title', 'cover_image', 'link']
            
            has_all_columns = all(col in df.columns for col in required_columns)
            
            if has_all_columns:
                logger.info("Estrutura do CSV validada com sucesso")
            else:
                missing = [col for col in required_columns if col not in df.columns]
                logger.error(f"Colunas faltando no CSV: {missing}")
            
            return has_all_columns
            
        except Exception as exc:
            logger.error(f"Erro ao validar estrutura do CSV: {str(exc)}")
            return False
    
    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas do CSV.
        
        Returns:
            Dicionário com estatísticas
        """
        posts = self.load_posts()
        
        total = len(posts)
        with_summary = sum(1 for p in posts if p.get('resumo'))
        without_summary = total - with_summary
        
        post_types = {}
        for post in posts:
            post_type = post.get('post_type', 'Unknown')
            post_types[post_type] = post_types.get(post_type, 0) + 1
        
        return {
            'total_posts': total,
            'posts_with_summary': with_summary,
            'posts_without_summary': without_summary,
            'post_types': post_types
        }

