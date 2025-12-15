"""
Módulo de Integração com n8n
=============================
Gerencia envio de posts processados para webhook n8n.

Author: Sistema AFN
Date: 2025-12-09
"""

import base64
from typing import List, Dict, Optional
import requests
from requests.exceptions import RequestException

from src.config import config
from src.logger import get_logger
from src.utils import ImageHandler


logger = get_logger(__name__)


class N8NWebhookClient:
    """Cliente para comunicação com webhooks n8n."""
    
    def __init__(self, webhook_url: str = None, timeout: int = None):
        """
        Inicializa cliente n8n.
        
        Args:
            webhook_url: URL do webhook (usa config se não fornecido)
            timeout: Timeout das requisições (usa config se não fornecido)
        """
        self.webhook_url = webhook_url or config.webhook_url
        self.timeout = timeout or config.webhook_timeout
        
        logger.info(f"N8NWebhookClient inicializado - URL: {self.webhook_url}")
    
    def send_data(self, data: dict) -> bool:
        """
        Envia dados para webhook n8n.
        
        Args:
            data: Dados a enviar
            
        Returns:
            True se sucesso
        """
        try:
            response = requests.post(
                self.webhook_url,
                json=data,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            
            logger.info(
                f"Dados enviados com sucesso para n8n - "
                f"Status: {response.status_code}"
            )
            logger.debug(f"Resposta n8n: {response.text[:200]}")
            
            return True
            
        except RequestException as exc:
            logger.error(f"Erro ao enviar dados para n8n: {str(exc)}")
            return False
        except Exception as exc:
            logger.error(f"Erro inesperado ao enviar para n8n: {str(exc)}")
            return False
    
    def test_connection(self) -> bool:
        """
        Testa conexão com webhook.
        
        Returns:
            True se webhook está acessível
        """
        try:
            response = requests.post(
                self.webhook_url,
                json={"test": True},
                timeout=5
            )
            
            is_ok = response.status_code < 500
            
            if is_ok:
                logger.info("Teste de conexao n8n: OK")
            else:
                logger.warning(f"Teste de conexao n8n: FALHA - Status {response.status_code}")
            
            return is_ok
            
        except RequestException as exc:
            logger.error(f"Teste de conexao n8n falhou: {str(exc)}")
            return False


class PostFormatter:
    """Formatador de posts para envio ao n8n."""
    
    @staticmethod
    def format_post(post: Dict[str, str], include_image: bool = True) -> Dict:
        """
        Formata post para formato esperado pelo n8n.
        
        Args:
            post: Dicionário com dados do post
            include_image: Se deve incluir imagem binária
            
        Returns:
            Post formatado
        """
        formatted = {
            "titulo": post.get("title", ""),
            "resumo": post.get("resumo", ""),
            "link": post.get("link", "")
        }
        
        # Adiciona imagem se solicitado
        if include_image:
            image_url = post.get("cover_image", "")
            if image_url:
                binary_data = PostFormatter._create_binary_block(image_url)
                if binary_data:
                    formatted.update(binary_data)
        
        return formatted
    
    @staticmethod
    def _create_binary_block(image_url: str) -> Optional[Dict]:
        """
        Cria bloco binário com imagem para n8n.
        
        Args:
            image_url: URL da imagem
            
        Returns:
            Dicionário com estrutura binary ou None
        """
        image_binary = ImageHandler.download_binary(image_url)
        
        if not image_binary:
            logger.warning(f"Nao foi possivel baixar imagem: {image_url}")
            return None
        
        try:
            encoded = base64.b64encode(image_binary).decode("utf-8")
            
            return {
                "binary": {
                    "imagem": {
                        "data": encoded,
                        "mimeType": "image/jpeg",
                        "fileName": "cover.jpg"
                    }
                }
            }
        except Exception as exc:
            logger.error(f"Erro ao codificar imagem: {str(exc)}")
            return None
    
    @staticmethod
    def format_posts_batch(posts: List[Dict[str, str]], include_images: bool = True) -> List[Dict]:
        """
        Formata lote de posts.
        
        Args:
            posts: Lista de posts
            include_images: Se deve incluir imagens
            
        Returns:
            Lista de posts formatados
        """
        formatted_posts = []
        
        for post in posts:
            formatted = PostFormatter.format_post(post, include_images)
            formatted_posts.append(formatted)
        
        logger.info(f"Formatados {len(formatted_posts)} posts para envio")
        return formatted_posts


class N8NIntegration:
    """Gerenciador principal de integração com n8n."""
    
    def __init__(self):
        """Inicializa integração n8n."""
        self.client = N8NWebhookClient()
        self.formatter = PostFormatter()
        logger.info("N8NIntegration inicializada")
    
    def send_posts(self, posts: List[Dict[str, str]], include_images: bool = True) -> bool:
        """
        Envia posts para n8n.
        
        Args:
            posts: Lista de posts a enviar
            include_images: Se deve incluir imagens
            
        Returns:
            True se sucesso
        """
        if not posts:
            logger.warning("Nenhum post para enviar")
            return False
        
        logger.info(f"Preparando envio de {len(posts)} posts para n8n")
        
        # Formata posts
        formatted_posts = self.formatter.format_posts_batch(posts, include_images)
        
        if not formatted_posts:
            logger.error("Nenhum post foi formatado com sucesso")
            return False
        
        # Envia para n8n (array direto, cada elemento vira um item no workflow)
        # Log de debug para diagnosticar formato do payload
        logger.debug(f"Payload n8n (primeiro item): {str(formatted_posts[0])[:500] if formatted_posts else 'vazio'}")
        logger.info(f"Estrutura do payload: lista com {len(formatted_posts)} items, chaves do primeiro: {list(formatted_posts[0].keys()) if formatted_posts else []}")
        success = self.client.send_data(formatted_posts)
        
        if success:
            logger.info(f"Enviados {len(formatted_posts)} posts com sucesso para n8n")
        else:
            logger.error("Falha ao enviar posts para n8n")
        
        return success
    
    def test_integration(self) -> bool:
        """
        Testa integração com n8n.
        
        Returns:
            True se teste passou
        """
        logger.info("Testando integracao com n8n...")
        return self.client.test_connection()
    
    def send_single_post(self, post: Dict[str, str], include_image: bool = True) -> bool:
        """
        Envia post individual para n8n.
        
        Args:
            post: Post a enviar
            include_image: Se deve incluir imagem
            
        Returns:
            True se sucesso
        """
        formatted = self.formatter.format_post(post, include_image)
        return self.client.send_data([formatted])

