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
        # Garante diretório pai para caminhos do tipo dados/arquivo.csv
        try:
            self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Se o path for relativo sem pai (ex.: "arquivo.csv"), parent é "." e não precisa mkdir.
            pass
        logger.info(f"CSVHandler inicializado: {self.csv_path}")
    
    def load_posts(self) -> List[Dict[str, str]]:
        """
        Carrega posts do arquivo CSV.
        
        Returns:
            Lista de dicionários com posts
        """
        if self.csv_path.exists() and self.csv_path.is_dir():
            logger.error(
                f"Caminho do CSV aponta para um diretorio (nao arquivo): {self.csv_path}. "
                "Em Docker isso geralmente acontece por bind mount de um arquivo inexistente."
            )
            return []

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

            # Normaliza NaN (float) para string vazia para evitar erros
            # como: AttributeError: 'float' object has no attribute 'strip'
            df['resumo'] = df['resumo'].fillna('').astype(str)
            df['data_resumo'] = df['data_resumo'].fillna('').astype(str)
            
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

            # Preserva resumos já existentes quando o scraping roda novamente.
            # Sem isso, um novo scraping sobrescreve o CSV e "apaga" resumo/data_resumo.
            if self.csv_path.exists() and self.csv_path.is_file() and 'link' in df.columns:
                try:
                    existing_df = pd.read_csv(self.csv_path, encoding='utf-8')
                    if 'link' in existing_df.columns:
                        for col in ['resumo', 'data_resumo']:
                            if col not in df.columns:
                                df[col] = ''
                            if col in existing_df.columns:
                                # Normaliza NaN para facilitar fill.
                                existing_df[col] = existing_df[col].fillna('').astype(str)

                        # Junta para obter resumo/data_resumo existentes.
                        existing_subset = existing_df[['link', 'resumo', 'data_resumo']].drop_duplicates(subset=['link'])
                        merged = df.merge(existing_subset, on='link', how='left', suffixes=('', '_old'))

                        for col in ['resumo', 'data_resumo']:
                            merged[col] = merged[col].fillna('').astype(str)
                            merged[f'{col}_old'] = merged[f'{col}_old'].fillna('').astype(str)
                            merged[col] = merged[col].where(merged[col].str.strip() != '', merged[f'{col}_old'])
                            merged.drop(columns=[f'{col}_old'], inplace=True)

                        df = merged
                except Exception as exc:
                    logger.warning(f"Falha ao preservar resumos do CSV existente: {str(exc)}")
            
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

