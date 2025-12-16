"""
Módulo de Processamento com IA
===============================
Gerencia geração de resumos usando OpenAI GPT.

Author: Sistema AFN
Date: 2025-12-09
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import openai
from openai import OpenAIError

from src.config import config
from src.logger import get_logger
from src.database import DatabaseManager


logger = get_logger(__name__)


class OpenAIClient:
    """Cliente gerenciado para API OpenAI."""
    
    def __init__(self):
        """Inicializa cliente OpenAI."""
        openai.api_key = config.openai_api_key
        self.client = openai.Client(api_key=config.openai_api_key)
        self.model = config.openai_model
        self.timeout = config.openai_timeout
        logger.info(f"Cliente OpenAI inicializado - Modelo: {self.model}")
    
    def generate_completion(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """
        Gera completion usando API OpenAI.
        
        Args:
            messages: Lista de mensagens no formato OpenAI
            
        Returns:
            Texto da resposta ou None em caso de erro
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                timeout=self.timeout
            )
            
            content = response.choices[0].message.content
            logger.debug(f"Completion gerado com sucesso - {len(content)} caracteres")
            return content
            
        except OpenAIError as exc:
            logger.error(f"Erro na API OpenAI: {str(exc)}")
            return None
        except Exception as exc:
            logger.error(f"Erro inesperado ao gerar completion: {str(exc)}")
            return None


class SummaryGenerator:
    """Gerador de resumos de posts usando IA."""
    
    SYSTEM_PROMPT = (
        "Voce e Silvia, especialista senior em Engenharia de Dados e Arquitetura Lakehouse. "
        "Produza resumos CONCISOS e tecnicos. "
        "Regras: linguagem direta, sem marketing, sem emojis, sem introducoes genericas. "
        "Foco em: problema abordado, conceitos-chave e impacto pratico. "
        "IMPORTANTE: Seja breve e objetivo. Priorize qualidade sobre quantidade."
    )
    
    def __init__(self, openai_client: OpenAIClient):
        """
        Inicializa gerador de resumos.
        
        Args:
            openai_client: Cliente OpenAI configurado
        """
        self.client = openai_client
        self.max_chars = config.max_summary_chars
        logger.info("SummaryGenerator inicializado")
    
    def generate_summary(self, link: str) -> Optional[str]:
        """
        Gera resumo de post a partir do link.
        
        Args:
            link: URL do post
            
        Returns:
            Texto do resumo ou None em caso de erro
        """
        messages = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": (
                    f"Leia o post: {link}\n\n"
                    f"Gere um resumo CONCISO com MAXIMO {self.max_chars} caracteres (OBRIGATORIO respeitar este limite).\n\n"
                    "Estrutura:\n"
                    "1. Contexto (1-2 frases): Qual problema o post aborda?\n"
                    "2. Pontos-chave (3-5 bullets curtos): Conceitos e boas praticas principais\n"
                    "3. Impacto (1-2 frases): Implicacoes praticas para projetos de dados\n\n"
                    "Regras: Seja direto, sem introducoes, sem marketing, sem emojis. "
                    "Priorize densidade de informacao. Cada frase deve agregar valor."
                )
            }
        ]
        
        logger.info(f"Gerando resumo para: {link}")
        summary = self.client.generate_completion(messages)
        
        if summary:
            logger.info(f"Resumo gerado com sucesso - {len(summary)} caracteres")
        else:
            logger.warning(f"Falha ao gerar resumo para: {link}")
        
        return summary
    
    def validate_summary(self, summary: str) -> bool:
        """
        Valida se resumo atende aos critérios.
        
        Args:
            summary: Texto do resumo
            
        Returns:
            True se válido
        """
        if not summary or not summary.strip():
            return False
        
        if len(summary) > self.max_chars:
            logger.warning(
                f"Resumo excede limite de caracteres: "
                f"{len(summary)}/{self.max_chars}"
            )
            return False
        
        return True


class SummaryStorage:
    """Gerenciador de armazenamento de resumos."""
    
    SEPARATOR = "\n" + ("-" * 50) + "\n"
    
    def __init__(self, storage_path: Path = None):
        """
        Inicializa gerenciador de armazenamento.
        
        Args:
            storage_path: Caminho do arquivo JSON (usa config se não fornecido)
        """
        self.storage_path = storage_path or Path(config.output_summaries_json)
        self._ensure_storage_exists()
        logger.info(f"SummaryStorage inicializado: {self.storage_path}")
    
    def _ensure_storage_exists(self) -> None:
        """Garante que arquivo de armazenamento existe."""
        if not self.storage_path.exists():
            self._save_summaries([])
            logger.info("Arquivo de armazenamento criado")
    
    def load_summaries(self) -> List[Dict]:
        """
        Carrega resumos do arquivo JSON.
        
        Returns:
            Lista de dicionários com resumos
        """
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                summaries = json.load(f)
            
            logger.debug(f"Carregados {len(summaries)} resumos do storage")
            return summaries
            
        except json.JSONDecodeError as exc:
            logger.error(f"Erro ao decodificar JSON: {str(exc)}")
            return []
        except Exception as exc:
            logger.error(f"Erro ao carregar resumos: {str(exc)}")
            return []
    
    def _save_summaries(self, summaries: List[Dict]) -> bool:
        """
        Salva resumos no arquivo JSON.
        
        Args:
            summaries: Lista de resumos
            
        Returns:
            True se sucesso
        """
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(summaries, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Salvos {len(summaries)} resumos no storage")
            return True
            
        except Exception as exc:
            logger.error(f"Erro ao salvar resumos: {str(exc)}")
            return False
    
    def save_summary(self, summary_data: Dict) -> bool:
        """
        Adiciona novo resumo ao storage.
        
        Args:
            summary_data: Dicionário com dados do resumo
            
        Returns:
            True se sucesso
        """
        summaries = self.load_summaries()
        summaries.append(summary_data)
        return self._save_summaries(summaries)
    
    def get_processed_links(self) -> set:
        """
        Retorna conjunto de links que já possuem resumo.
        
        Returns:
            Set de URLs
        """
        summaries = self.load_summaries()
        return {item.get("link") for item in summaries if item.get("link")}


class AIPostProcessor:
    """Processador principal de posts com IA."""
    
    def __init__(self):
        """Inicializa processador de IA."""
        self.openai_client = OpenAIClient()
        self.summary_generator = SummaryGenerator(self.openai_client)
        self.summary_storage = SummaryStorage()
        self.database = DatabaseManager()
        logger.info("AIPostProcessor inicializado")
    
    def process_posts(self, posts: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Processa lista de posts gerando resumos.
        
        Args:
            posts: Lista de posts a processar
            
        Returns:
            Lista de posts com resumos adicionados
        """
        if not posts:
            logger.warning("Nenhum post para processar")
            return []
        
        logger.info(f"Iniciando processamento de {len(posts)} posts")
        
        processed_count = 0
        skipped_count = 0
        
        for idx, post in enumerate(posts, 1):
            link = post.get("link", "")
            
            # Verifica se já foi processado
            if self.database.is_processed(link):
                logger.info(f"[{idx}/{len(posts)}] Post ja processado - pulando: {link}")
                skipped_count += 1
                continue
            
            logger.info(f"[{idx}/{len(posts)}] Processando post: {link}")
            
            # Gera resumo
            summary = self.summary_generator.generate_summary(link)
            
            if not summary or not self.summary_generator.validate_summary(summary):
                logger.warning(f"Resumo invalido para: {link}")
                continue
            
            # Adiciona resumo ao post
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
            post["resumo"] = self.summary_storage.SEPARATOR + summary
            post["data_resumo"] = timestamp
            
            # Salva resumo
            summary_record = {
                "titulo": post.get("title", ""),
                "link": link,
                "data": timestamp,
                "conteudo": summary
            }
            
            self.summary_storage.save_summary(summary_record)
            
            # Marca como processado no banco
            self.database.mark_as_processed(link)
            
            processed_count += 1
            logger.info(f"[{idx}/{len(posts)}] Resumo salvo com sucesso")
        
        logger.info(
            f"Processamento concluido - "
            f"Processados: {processed_count}, "
            f"Pulados: {skipped_count}"
        )
        
        return posts
    
    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas de processamento.
        
        Returns:
            Dicionário com estatísticas
        """
        db_stats = self.database.get_statistics()
        storage_summaries = len(self.summary_storage.load_summaries())
        
        return {
            **db_stats,
            'total_summaries_stored': storage_summaries
        }

