"""
Aplicação Principal - Databricks Post Processor
================================================
Orquestrador principal do sistema de scraping, processamento e integração.

Author: Sistema AFN
Date: 2025-12-09
Version: 2.0.0
"""

import sys
from pathlib import Path
from typing import Optional

from src.config import config
from src.logger import get_logger, LoggerFactory
from src.scraper import DatabricksScraper
from src.csv_handler import CSVHandler
from src.ai_processor import AIPostProcessor
from src.n8n_integration import N8NIntegration


logger = get_logger(__name__)


class Application:
    """Aplicação principal do sistema."""
    
    def __init__(self):
        """Inicializa aplicação."""
        self.scraper: Optional[DatabricksScraper] = None
        self.csv_handler = CSVHandler()
        self.ai_processor = AIPostProcessor()
        self.n8n_integration = N8NIntegration()
        
        logger.info("=" * 70)
        logger.info("Databricks Post Processor - Sistema Iniciado")
        logger.info(f"Ambiente: {config.environment}")
        logger.info("=" * 70)
    
    def run_scraping(self) -> bool:
        """
        Executa fase de scraping de posts.
        
        Returns:
            True se sucesso
        """
        LoggerFactory.log_operation_start(logger, "Scraping de Posts")
        
        try:
            self.scraper = DatabricksScraper()
            posts = self.scraper.scrape_posts()
            
            if not posts:
                logger.warning("Nenhum post extraido pelo scraper")
                LoggerFactory.log_operation_end(logger, "Scraping de Posts", False)
                return False
            
            # Salva posts no CSV
            success = self.csv_handler.save_posts(posts)
            
            if success:
                logger.info(f"Scraping concluido: {len(posts)} posts salvos")
                LoggerFactory.log_operation_end(logger, "Scraping de Posts", True)
            else:
                logger.error("Falha ao salvar posts no CSV")
                LoggerFactory.log_operation_end(logger, "Scraping de Posts", False)
            
            return success
            
        except Exception as exc:
            LoggerFactory.log_exception(logger, "Erro durante scraping", exc)
            LoggerFactory.log_operation_end(logger, "Scraping de Posts", False)
            return False
        
        finally:
            if self.scraper:
                self.scraper.cleanup()
    
    def run_ai_processing(self) -> bool:
        """
        Executa fase de processamento com IA.
        
        Returns:
            True se sucesso
        """
        LoggerFactory.log_operation_start(logger, "Processamento com IA")
        
        try:
            # Carrega posts do CSV
            posts = self.csv_handler.load_posts()
            
            if not posts:
                logger.warning("Nenhum post encontrado no CSV")
                LoggerFactory.log_operation_end(logger, "Processamento com IA", False)
                return False
            
            # Processa posts com IA
            processed_posts = self.ai_processor.process_posts(posts)
            
            # Atualiza CSV com resumos
            success = self.csv_handler.update_posts(processed_posts)
            
            if success:
                stats = self.ai_processor.get_statistics()
                logger.info(
                    f"Processamento IA concluido - "
                    f"Total processados: {stats.get('total_processed', 0)}"
                )
                LoggerFactory.log_operation_end(logger, "Processamento com IA", True)
            else:
                logger.error("Falha ao atualizar CSV com resumos")
                LoggerFactory.log_operation_end(logger, "Processamento com IA", False)
            
            return success
            
        except Exception as exc:
            LoggerFactory.log_exception(logger, "Erro durante processamento IA", exc)
            LoggerFactory.log_operation_end(logger, "Processamento com IA", False)
            return False
    
    def run_n8n_integration(self) -> bool:
        """
        Executa fase de integração com n8n.
        
        Returns:
            True se sucesso
        """
        LoggerFactory.log_operation_start(logger, "Integracao n8n")
        
        try:
            # Testa conexão
            if not self.n8n_integration.test_integration():
                logger.error("Falha no teste de conexao com n8n")
                LoggerFactory.log_operation_end(logger, "Integracao n8n", False)
                return False
            
            # Carrega posts do CSV
            posts = self.csv_handler.load_posts()
            
            if not posts:
                logger.warning("Nenhum post para enviar")
                LoggerFactory.log_operation_end(logger, "Integracao n8n", False)
                return False
            
            # Filtra posts com resumo
            posts_with_summary = [
                post for post in posts 
                if post.get('resumo') and post.get('resumo').strip()
            ]
            
            if not posts_with_summary:
                logger.warning("Nenhum post com resumo para enviar")
                LoggerFactory.log_operation_end(logger, "Integracao n8n", False)
                return False
            
            # Envia para n8n
            success = self.n8n_integration.send_posts(posts_with_summary)
            
            if success:
                logger.info(f"Enviados {len(posts_with_summary)} posts para n8n")
                LoggerFactory.log_operation_end(logger, "Integracao n8n", True)
            else:
                logger.error("Falha ao enviar posts para n8n")
                LoggerFactory.log_operation_end(logger, "Integracao n8n", False)
            
            return success
            
        except Exception as exc:
            LoggerFactory.log_exception(logger, "Erro durante integracao n8n", exc)
            LoggerFactory.log_operation_end(logger, "Integracao n8n", False)
            return False
    
    def run_full_pipeline(self) -> bool:
        """
        Executa pipeline completo: scraping -> processamento -> integração.
        
        Returns:
            True se todas as fases executaram com sucesso
        """
        logger.info("Iniciando pipeline completo")
        
        # Fase 1: Scraping
        if not self.run_scraping():
            logger.error("Pipeline abortado: falha no scraping")
            return False
        
        # Fase 2: Processamento IA
        if not self.run_ai_processing():
            logger.error("Pipeline abortado: falha no processamento IA")
            return False
        
        # Fase 3: Integração n8n
        if not self.run_n8n_integration():
            logger.error("Pipeline abortado: falha na integracao n8n")
            return False
        
        logger.info("Pipeline completo executado com sucesso")
        return True
    
    def show_statistics(self) -> None:
        """Exibe estatísticas do sistema."""
        logger.info("=" * 70)
        logger.info("ESTATISTICAS DO SISTEMA")
        logger.info("=" * 70)
        
        # Estatísticas CSV
        csv_stats = self.csv_handler.get_statistics()
        logger.info(f"Total de posts: {csv_stats['total_posts']}")
        logger.info(f"Posts com resumo: {csv_stats['posts_with_summary']}")
        logger.info(f"Posts sem resumo: {csv_stats['posts_without_summary']}")
        
        logger.info("\nDistribuicao por tipo:")
        for post_type, count in csv_stats['post_types'].items():
            logger.info(f"  - {post_type}: {count}")
        
        # Estatísticas IA
        ai_stats = self.ai_processor.get_statistics()
        logger.info(f"\nTotal processados (banco): {ai_stats['total_processed']}")
        logger.info(f"Processados hoje: {ai_stats['processed_today']}")
        logger.info(f"Resumos armazenados: {ai_stats['total_summaries_stored']}")
        
        logger.info("=" * 70)


def main():
    """Função principal de entrada."""
    try:
        app = Application()
        
        # Você pode personalizar o comportamento aqui:
        # - Para executar apenas scraping: app.run_scraping()
        # - Para executar apenas processamento: app.run_ai_processing()
        # - Para executar apenas integração: app.run_n8n_integration()
        # - Para executar tudo: app.run_full_pipeline()
        
        # Executa pipeline completo
        success = app.run_full_pipeline()
        
        # Exibe estatísticas
        app.show_statistics()
        
        if success:
            logger.info("Aplicacao finalizada com sucesso")
            return 0
        else:
            logger.error("Aplicacao finalizada com erros")
            return 1
    
    except KeyboardInterrupt:
        logger.warning("Aplicacao interrompida pelo usuario")
        return 130
    
    except Exception as exc:
        LoggerFactory.log_exception(logger, "Erro critico na aplicacao", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())

