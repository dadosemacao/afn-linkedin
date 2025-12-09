"""
Módulo de Utilidades
====================
Funções auxiliares reutilizáveis para toda a aplicação.

Author: Sistema AFN
Date: 2025-12-09
"""

import base64
import re
import requests
from typing import Optional
from bs4 import BeautifulSoup
from src.logger import get_logger


logger = get_logger(__name__)


class ImageHandler:
    """Gerenciador de operações com imagens."""
    
    @staticmethod
    def download_and_encode(url: str, timeout: int = 10) -> Optional[str]:
        """
        Baixa imagem de URL e retorna em base64.
        
        Args:
            url: URL da imagem
            timeout: Timeout da requisição em segundos
            
        Returns:
            String base64 da imagem ou None em caso de erro
        """
        if not url:
            return None
        
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            encoded = base64.b64encode(response.content).decode("utf-8")
            logger.debug(f"Imagem baixada e codificada: {url}")
            return encoded
            
        except requests.exceptions.RequestException as exc:
            logger.warning(f"Erro ao baixar imagem {url}: {str(exc)}")
            return None
    
    @staticmethod
    def download_binary(url: str, timeout: int = 10) -> Optional[bytes]:
        """
        Baixa imagem de URL e retorna conteúdo binário.
        
        Args:
            url: URL da imagem
            timeout: Timeout da requisição em segundos
            
        Returns:
            Bytes da imagem ou None em caso de erro
        """
        if not url:
            return None
        
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            logger.debug(f"Imagem baixada (binário): {url}")
            return response.content
            
        except requests.exceptions.RequestException as exc:
            logger.warning(f"Erro ao baixar imagem {url}: {str(exc)}")
            return None


class TextCleaner:
    """Utilitários para limpeza e formatação de texto."""
    
    @staticmethod
    def clean_title(title: str) -> str:
        """
        Remove prefixos desnecessários do título.
        Exemplo: 'Product/2025/Title' -> 'Title'
        
        Args:
            title: Título original
            
        Returns:
            Título limpo
        """
        if not title:
            return ""
        
        # Remove estrutura de caminho
        if "/" in title:
            title = title.split("/")[-1].strip()
        
        # Extrai texto começando com maiúscula
        match = re.search(r"[A-Z][a-z]+.*", title)
        if match:
            return match.group(0).strip()
        
        return title.strip()
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normaliza espaços em branco no texto.
        
        Args:
            text: Texto a normalizar
            
        Returns:
            Texto normalizado
        """
        if not text:
            return ""
        
        return " ".join(text.split())


class HTMLParser:
    """Utilitários para parsing de HTML."""
    
    @staticmethod
    def extract_meta_image(html: str) -> Optional[str]:
        """
        Extrai URL de imagem de meta tags Open Graph ou primeira imagem.
        
        Args:
            html: Código HTML da página
            
        Returns:
            URL da imagem ou None
        """
        soup = BeautifulSoup(html, "html.parser")
        
        # Tenta meta tag og:image
        meta = soup.find("meta", property="og:image")
        if meta and meta.get("content"):
            return meta["content"]
        
        # Fallback para primeira imagem
        img = soup.find("img")
        if img and img.get("src"):
            return img.get("src")
        
        return None
    
    @staticmethod
    def extract_post_type(soup: BeautifulSoup, selectors: list) -> Optional[str]:
        """
        Extrai tipo de post usando lista de seletores CSS.
        
        Args:
            soup: Objeto BeautifulSoup
            selectors: Lista de seletores CSS a tentar
            
        Returns:
            Tipo de post ou None
        """
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return None


class URLNormalizer:
    """Utilitários para normalização de URLs."""
    
    @staticmethod
    def normalize_url(url: str, base_url: str) -> str:
        """
        Normaliza URL relativa ou protocolo-relativo para absoluto.
        
        Args:
            url: URL a normalizar
            base_url: URL base do site
            
        Returns:
            URL absoluta normalizada
        """
        if not url:
            return ""
        
        # Protocolo relativo
        if url.startswith("//"):
            return f"https:{url}"
        
        # URL relativa
        if url.startswith("/"):
            from urllib.parse import urljoin
            return urljoin(base_url, url)
        
        # URL absoluta
        if url.startswith("http"):
            return url
        
        # Outro caso
        from urllib.parse import urljoin
        return urljoin(base_url, url)

