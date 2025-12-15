"""
Módulo de Web Scraping
======================
Realiza scraping de posts do blog Databricks usando Selenium.

Author: Sistema AFN
Date: 2025-12-09
"""

import time
import os
import shutil
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

from src.config import config
from src.logger import get_logger
from src.utils import HTMLParser, TextCleaner, URLNormalizer


logger = get_logger(__name__)


class SeleniumDriver:
    """Gerenciador de driver Selenium com configurações otimizadas."""
    
    def __init__(self):
        """Inicializa configurações do Selenium."""
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self._setup_driver()
    
    def _setup_driver(self) -> None:
        """Configura e inicializa driver Chrome."""
        try:
            options = Options()
            
            if config.selenium_headless:
                options.add_argument("--headless=new")
            
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument(f"user-agent={config.user_agent}")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Define binário do browser quando disponível (Docker geralmente usa Chromium).
            chrome_bin = (
                os.getenv("CHROME_BIN")
                or shutil.which("google-chrome")
                or shutil.which("google-chrome-stable")
                or shutil.which("chromium")
                or shutil.which("chromium-browser")
            )
            if chrome_bin:
                options.binary_location = chrome_bin

            # Prioriza chromedriver do sistema (ex.: pacote chromium-driver no Docker).
            chromedriver_path = os.getenv("CHROMEDRIVER_PATH") or shutil.which("chromedriver")
            if chromedriver_path:
                service = Service(chromedriver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                # Fallback: Selenium Manager (Selenium 4.6+) tenta resolver o driver automaticamente.
                self.driver = webdriver.Chrome(options=options)

            self.wait = WebDriverWait(self.driver, config.selenium_timeout)
            
            logger.info("Driver Selenium inicializado com sucesso")
            
        except Exception as exc:
            msg = str(exc)
            lower = msg.lower()
            if (
                "google-chrome" in lower
                or "chrome binary" in lower
                or "chromium" in lower and "not found" in lower
                or "cannot find" in lower and "chrome" in lower
            ):
                raise RuntimeError(
                    "Falha ao inicializar o Selenium: browser (Chrome/Chromium) nao encontrado no ambiente. "
                    "Em Docker, instale chromium + chromium-driver (ou google-chrome) e garanta que o binario "
                    "esteja no PATH. Opcionalmente defina CHROME_BIN e CHROMEDRIVER_PATH."
                ) from exc

            logger.error(f"Erro ao inicializar Selenium: {msg}")
            raise
    
    def get(self, url: str) -> None:
        """
        Navega para URL especificada.
        
        Args:
            url: URL de destino
        """
        if not self.driver:
            raise RuntimeError("Driver não inicializado")
        
        try:
            self.driver.get(url)
            logger.debug(f"Navegado para: {url}")
        except WebDriverException as exc:
            logger.error(f"Erro ao navegar para {url}: {str(exc)}")
            raise
    
    def get_page_source(self) -> str:
        """Retorna código fonte da página atual."""
        if not self.driver:
            raise RuntimeError("Driver não inicializado")
        return self.driver.page_source
    
    def scroll_to_bottom(self, delay: float = None) -> None:
        """
        Rola página até o final.
        
        Args:
            delay: Tempo de espera após scroll (usa config se não fornecido)
        """
        if not self.driver:
            raise RuntimeError("Driver não inicializado")
        
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay or config.scroll_delay)
        logger.debug("Pagina rolada ate o final")
    
    def wait_for_element(self, selector: str, by: By = By.CSS_SELECTOR) -> bool:
        """
        Aguarda elemento aparecer na página.
        
        Args:
            selector: Seletor do elemento
            by: Tipo de seletor (padrão: CSS_SELECTOR)
            
        Returns:
            True se elemento apareceu, False se timeout
        """
        if not self.wait:
            raise RuntimeError("WebDriverWait não inicializado")
        
        try:
            self.wait.until(EC.presence_of_element_located((by, selector)))
            return True
        except TimeoutException:
            logger.warning(f"Timeout aguardando elemento: {selector}")
            return False
    
    def open_new_tab(self, url: str) -> bool:
        """
        Abre nova aba e navega para URL.
        
        Args:
            url: URL a abrir
            
        Returns:
            True se sucesso
        """
        if not self.driver:
            raise RuntimeError("Driver não inicializado")
        
        try:
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.get(url)
            time.sleep(config.page_load_delay)
            return True
        except WebDriverException as exc:
            logger.warning(f"Erro ao abrir nova aba: {str(exc)}")
            return False
    
    def close_current_tab(self) -> None:
        """Fecha aba atual e retorna para primeira."""
        if not self.driver:
            return
        
        try:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
        except WebDriverException as exc:
            logger.warning(f"Erro ao fechar aba: {str(exc)}")
    
    def quit(self) -> None:
        """Encerra driver Selenium."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver Selenium encerrado")
            except WebDriverException as exc:
                logger.warning(f"Erro ao encerrar driver: {str(exc)}")


class PostExtractor:
    """Extrator de informações de posts do blog."""
    
    # Seletores CSS para diferentes elementos
    POST_TYPE_SELECTORS = [
        ".tag", ".post-type", ".kicker", 
        ".eyebrow", ".meta .type", ".post-kicker"
    ]
    
    CARD_CLASSES = [
        "category-results-wrapper", "blog-grid-card",
        "post-card", "card", "article", "card__content"
    ]
    
    POST_TYPE_KEYWORDS = [
        "Product", "Engineering", "Article", "Announcement",
        "Solutions", "Customer", "Research", "Data", 
        "Security", "Announcements"
    ]
    
    def __init__(self, driver: SeleniumDriver):
        """
        Inicializa extrator.
        
        Args:
            driver: Instância do driver Selenium
        """
        self.driver = driver
    
    def extract_posts_from_page(self, html: str) -> List[Dict[str, str]]:
        """
        Extrai posts da página HTML.
        
        Args:
            html: Código HTML da página
            
        Returns:
            Lista de dicionários com dados dos posts
        """
        soup = BeautifulSoup(html, "html.parser")
        anchors = soup.select("a[href*='/blog/']")
        
        seen_links: Set[str] = set()
        results: List[Dict[str, str]] = []
        
        logger.info(f"Encontrados {len(anchors)} links de blog na pagina")
        
        for anchor in anchors:
            post_data = self._extract_post_data(anchor, seen_links)
            if post_data:
                results.append(post_data)
        
        logger.info(f"Extraidos {len(results)} posts unicos")
        return results
    
    def _extract_post_data(self, anchor, seen_links: Set[str]) -> Optional[Dict[str, str]]:
        """
        Extrai dados de um único post.
        
        Args:
            anchor: Tag <a> do BeautifulSoup
            seen_links: Set de links já processados
            
        Returns:
            Dicionário com dados do post ou None
        """
        href = anchor.get("href")
        if not href:
            return None
        
        # Normaliza URL
        link = URLNormalizer.normalize_url(href, config.base_url)
        
        if "/blog/" not in link or link in seen_links:
            return None
        
        seen_links.add(link)
        
        # Extrai dados básicos
        title = anchor.get_text(strip=True)
        card = self._find_parent_card(anchor)
        
        post_type = ""
        cover_image = ""
        
        if card:
            post_type = self._extract_post_type_from_card(card)
            cover_image = self._extract_cover_image_from_card(card)
        
        # Se dados faltando, tenta extrair da página individual
        if not post_type or not cover_image:
            additional_data = self._extract_from_individual_page(link)
            if additional_data:
                post_type = post_type or additional_data.get("post_type", "")
                cover_image = cover_image or additional_data.get("cover_image", "")
                title = title or additional_data.get("title", "")
        
        return {
            "post_type": post_type or "Unknown",
            "title": TextCleaner.clean_title(title),
            "cover_image": cover_image,
            "link": link
        }
    
    def _find_parent_card(self, element) -> Optional[BeautifulSoup]:
        """
        Encontra elemento pai que representa o card do post.
        
        Args:
            element: Elemento filho
            
        Returns:
            Elemento card ou None
        """
        parent = element
        
        for _ in range(4):
            parent = parent.parent
            if parent is None:
                break
            
            classes = parent.get("class") or []
            if any(cls in self.CARD_CLASSES for cls in classes):
                return parent
        
        return None
    
    def _extract_post_type_from_card(self, card) -> str:
        """Extrai tipo de post do card."""
        # Tenta seletores CSS
        for selector in self.POST_TYPE_SELECTORS:
            element = card.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Fallback: busca por palavras-chave
        card_text = card.get_text(" ", strip=True)
        for keyword in self.POST_TYPE_KEYWORDS:
            if keyword in card_text.split():
                return keyword
        
        return ""
    
    def _extract_cover_image_from_card(self, card) -> str:
        """Extrai URL de imagem de capa do card."""
        img = card.select_one("img[data-main-image], img")
        if not img:
            return ""
        
        image_url = (
            img.get("src") or 
            img.get("data-src") or 
            img.get("data-main-image") or 
            ""
        )
        
        return URLNormalizer.normalize_url(image_url, config.base_url)
    
    def _extract_from_individual_page(self, link: str) -> Optional[Dict[str, str]]:
        """
        Extrai dados abrindo página individual do post.
        
        Args:
            link: URL do post
            
        Returns:
            Dicionário com dados extraídos ou None
        """
        try:
            if not self.driver.open_new_tab(link):
                return None
            
            page_html = self.driver.get_page_source()
            soup = BeautifulSoup(page_html, "html.parser")
            
            # Extrai imagem
            cover_image = HTMLParser.extract_meta_image(page_html) or ""
            
            # Extrai tipo de post
            post_type = HTMLParser.extract_post_type(soup, self.POST_TYPE_SELECTORS) or ""
            
            # Extrai título
            title = ""
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text(strip=True)
            
            logger.debug(f"Dados extraidos da pagina individual: {link}")
            
            return {
                "post_type": post_type,
                "cover_image": cover_image,
                "title": title
            }
            
        except Exception as exc:
            logger.warning(f"Erro ao extrair de pagina individual {link}: {str(exc)}")
            return None
            
        finally:
            self.driver.close_current_tab()


class DatabricksScraper:
    """Scraper principal para posts do Databricks."""
    
    def __init__(self):
        """Inicializa scraper."""
        self.driver = SeleniumDriver()
        self.extractor = PostExtractor(self.driver)
        logger.info("DatabricksScraper inicializado")
    
    def scrape_posts(self, filter_type: str = None) -> List[Dict[str, str]]:
        """
        Executa scraping de posts.
        
        Args:
            filter_type: Tipo de post para filtrar (usa config se não fornecido)
            
        Returns:
            Lista de posts extraídos
        """
        filter_type = filter_type or config.target_post_type
        
        try:
            logger.info(f"Iniciando scraping: {config.category_url}")
            
            # Navega para página
            self.driver.get(config.category_url)
            time.sleep(config.scroll_delay)
            
            # Aguarda conteúdo carregar
            self.driver.wait_for_element(
                "main, .blog-archive, .category-results-wrapper"
            )
            
            # Rola página para carregar mais conteúdo
            self.driver.scroll_to_bottom()
            
            # Extrai posts
            html = self.driver.get_page_source()
            posts = self.extractor.extract_posts_from_page(html)
            
            # Filtra por tipo
            if filter_type:
                original_count = len(posts)
                posts = [
                    p for p in posts 
                    if p["post_type"].lower() == filter_type.lower()
                ]
                logger.info(
                    f"Filtrados posts por tipo '{filter_type}': "
                    f"{len(posts)}/{original_count}"
                )
            
            # Remove duplicatas
            unique_posts = self._remove_duplicates(posts)
            
            logger.info(f"Scraping concluido: {len(unique_posts)} posts unicos")
            return unique_posts
            
        except Exception as exc:
            logger.error(f"Erro durante scraping: {str(exc)}", exc_info=True)
            raise
    
    def _remove_duplicates(self, posts: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Remove posts duplicados baseado no link."""
        seen = set()
        unique = []
        
        for post in posts:
            link = post["link"]
            if link not in seen:
                seen.add(link)
                unique.append(post)
        
        if len(unique) < len(posts):
            logger.debug(f"Removidas {len(posts) - len(unique)} duplicatas")
        
        return unique
    
    def cleanup(self) -> None:
        """Limpa recursos do scraper."""
        self.driver.quit()
        logger.info("Recursos do scraper liberados")

