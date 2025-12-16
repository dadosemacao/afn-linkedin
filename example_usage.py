"""
Exemplos de Uso - Databricks Post Processor
============================================
Demonstra diferentes formas de usar a aplicação.

Author: Sistema AFN
Date: 2025-12-09
"""

from src.main import Application
from src.scraper import DatabricksScraper
from src.csv_handler import CSVHandler
from src.ai_processor import AIPostProcessor
from src.n8n_integration import N8NIntegration
from src.database import DatabaseManager
from src.logger import get_logger


logger = get_logger(__name__)


def exemplo_1_pipeline_completo():
    """Exemplo 1: Executar pipeline completo."""
    print("\n" + "=" * 70)
    print("EXEMPLO 1: Pipeline Completo")
    print("=" * 70)
    
    app = Application()
    success = app.run_full_pipeline()
    
    if success:
        print("\nPipeline executado com sucesso!")
        app.show_statistics()
    else:
        print("\nErro ao executar pipeline. Verifique os logs.")


def exemplo_2_scraping_apenas():
    """Exemplo 2: Executar apenas scraping."""
    print("\n" + "=" * 70)
    print("EXEMPLO 2: Apenas Scraping")
    print("=" * 70)
    
    app = Application()
    success = app.run_scraping()
    
    if success:
        print("\nScraping concluido!")
        
        # Ver resultados
        csv_handler = CSVHandler()
        posts = csv_handler.load_posts()
        print(f"Total de posts extraidos: {len(posts)}")


def exemplo_3_processar_posts_existentes():
    """Exemplo 3: Processar posts de CSV existente."""
    print("\n" + "=" * 70)
    print("EXEMPLO 3: Processar Posts Existentes")
    print("=" * 70)
    
    app = Application()
    success = app.run_ai_processing()
    
    if success:
        print("\nProcessamento concluido!")
        stats = app.ai_processor.get_statistics()
        print(f"Total processados: {stats['total_processed']}")


def exemplo_4_enviar_para_n8n():
    """Exemplo 4: Enviar posts para n8n."""
    print("\n" + "=" * 70)
    print("EXEMPLO 4: Enviar para n8n")
    print("=" * 70)
    
    app = Application()
    success = app.run_n8n_integration()
    
    if success:
        print("\nEnvio concluido!")


def exemplo_5_uso_direto_componentes():
    """Exemplo 5: Usar componentes diretamente."""
    print("\n" + "=" * 70)
    print("EXEMPLO 5: Uso Direto de Componentes")
    print("=" * 70)
    
    # Scraping
    print("\n1. Executando scraping...")
    scraper = DatabricksScraper()
    posts = scraper.scrape_posts()
    scraper.cleanup()
    print(f"   Posts extraidos: {len(posts)}")
    
    # Salvar CSV
    print("\n2. Salvando em CSV...")
    csv_handler = CSVHandler()
    csv_handler.save_posts(posts)
    print("   CSV salvo com sucesso")
    
    # Processar com IA
    print("\n3. Processando com IA...")
    ai_processor = AIPostProcessor()
    processed_posts = ai_processor.process_posts(posts)
    print(f"   Posts processados: {len(processed_posts)}")
    
    # Atualizar CSV
    print("\n4. Atualizando CSV...")
    csv_handler.update_posts(processed_posts)
    print("   CSV atualizado")
    
    # Enviar para n8n
    print("\n5. Enviando para n8n...")
    n8n = N8NIntegration()
    n8n.send_posts(processed_posts)
    print("   Envio concluido")


def exemplo_6_estatisticas_detalhadas():
    """Exemplo 6: Obter estatísticas detalhadas."""
    print("\n" + "=" * 70)
    print("EXEMPLO 6: Estatisticas Detalhadas")
    print("=" * 70)
    
    # Estatísticas CSV
    csv_handler = CSVHandler()
    csv_stats = csv_handler.get_statistics()
    
    print("\nEstatisticas CSV:")
    print(f"  Total de posts: {csv_stats['total_posts']}")
    print(f"  Com resumo: {csv_stats['posts_with_summary']}")
    print(f"  Sem resumo: {csv_stats['posts_without_summary']}")
    print("\n  Distribuicao por tipo:")
    for post_type, count in csv_stats['post_types'].items():
        print(f"    - {post_type}: {count}")
    
    # Estatísticas Banco de Dados
    db = DatabaseManager()
    db_stats = db.get_statistics()
    
    print("\nEstatisticas Banco de Dados:")
    print(f"  Total processados: {db_stats['total_processed']}")
    print(f"  Processados hoje: {db_stats['processed_today']}")


def exemplo_7_processar_apenas_novos():
    """Exemplo 7: Processar apenas posts novos."""
    print("\n" + "=" * 70)
    print("EXEMPLO 7: Processar Apenas Novos Posts")
    print("=" * 70)
    
    # Carregar posts do CSV
    csv_handler = CSVHandler()
    all_posts = csv_handler.load_posts()
    print(f"Total de posts no CSV: {len(all_posts)}")
    
    # Filtrar apenas posts sem resumo
    posts_sem_resumo = csv_handler.get_posts_without_summaries()
    print(f"Posts sem resumo: {len(posts_sem_resumo)}")
    
    if posts_sem_resumo:
        # Processar apenas os novos
        ai_processor = AIPostProcessor()
        processed = ai_processor.process_posts(posts_sem_resumo)
        
        # Atualizar CSV
        csv_handler.update_posts(processed)
        print("Posts processados e CSV atualizado!")
    else:
        print("Todos os posts ja possuem resumo!")


def exemplo_8_filtrar_por_tipo():
    """Exemplo 8: Scraping com filtro de tipo."""
    print("\n" + "=" * 70)
    print("EXEMPLO 8: Scraping com Filtro")
    print("=" * 70)
    
    scraper = DatabricksScraper()
    
    # Filtrar apenas posts do tipo "Product"
    posts = scraper.scrape_posts(filter_types=["product"])
    print(f"Posts 'Product' extraidos: {len(posts)}")
    
    scraper.cleanup()


def exemplo_9_testar_n8n():
    """Exemplo 9: Testar conexão com n8n."""
    print("\n" + "=" * 70)
    print("EXEMPLO 9: Testar Conexao n8n")
    print("=" * 70)
    
    n8n = N8NIntegration()
    
    if n8n.test_integration():
        print("\nConexao n8n: OK")
    else:
        print("\nConexao n8n: FALHA")
        print("Verifique a URL do webhook em config.ini")


def exemplo_10_reprocessar_tudo():
    """Exemplo 10: Reprocessar todos os posts (limpar banco)."""
    print("\n" + "=" * 70)
    print("EXEMPLO 10: Reprocessar Todos os Posts")
    print("=" * 70)
    
    print("\nAVISO: Isso reprocessara todos os posts!")
    resposta = input("Tem certeza? (s/n): ")
    
    if resposta.lower() != 's':
        print("Operacao cancelada.")
        return
    
    # Limpar banco de dados
    import os
    from src.config import config
    
    db_path = config.get_database_path()
    if db_path.exists():
        os.remove(db_path)
        print("Banco de dados limpo.")
    
    # Reprocessar
    app = Application()
    app.run_ai_processing()
    print("\nReprocessamento concluido!")


def menu_interativo():
    """Menu interativo para escolher exemplos."""
    print("\n" + "=" * 70)
    print("EXEMPLOS DE USO - Databricks Post Processor")
    print("=" * 70)
    print("\nEscolha um exemplo:")
    print("1.  Pipeline Completo")
    print("2.  Apenas Scraping")
    print("3.  Processar Posts Existentes")
    print("4.  Enviar para n8n")
    print("5.  Uso Direto de Componentes")
    print("6.  Estatisticas Detalhadas")
    print("7.  Processar Apenas Novos Posts")
    print("8.  Scraping com Filtro")
    print("9.  Testar Conexao n8n")
    print("10. Reprocessar Todos os Posts")
    print("0.  Sair")
    print("=" * 70)
    
    escolha = input("\nDigite o numero do exemplo: ")
    
    exemplos = {
        '1': exemplo_1_pipeline_completo,
        '2': exemplo_2_scraping_apenas,
        '3': exemplo_3_processar_posts_existentes,
        '4': exemplo_4_enviar_para_n8n,
        '5': exemplo_5_uso_direto_componentes,
        '6': exemplo_6_estatisticas_detalhadas,
        '7': exemplo_7_processar_apenas_novos,
        '8': exemplo_8_filtrar_por_tipo,
        '9': exemplo_9_testar_n8n,
        '10': exemplo_10_reprocessar_tudo,
    }
    
    if escolha in exemplos:
        try:
            exemplos[escolha]()
        except Exception as exc:
            logger.error(f"Erro ao executar exemplo: {str(exc)}", exc_info=True)
            print(f"\nErro: {str(exc)}")
            print("Verifique os logs em logs/application.log")
    elif escolha == '0':
        print("\nAte logo!")
    else:
        print("\nOpcao invalida!")


if __name__ == "__main__":
    # Executar menu interativo
    menu_interativo()
    
    # Ou descomente para executar exemplo específico:
    # exemplo_1_pipeline_completo()
    # exemplo_6_estatisticas_detalhadas()
    # exemplo_9_testar_n8n()

