"""
Script de Teste - Databricks Post Processor
============================================
Testa todas as funcionalidades da aplicação incluindo banco de dados.

Author: Sistema AFN
Date: 2025-12-09
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Testa se todos os módulos podem ser importados."""
    print("\n" + "=" * 70)
    print("TESTE 1: Importação de Módulos")
    print("=" * 70)
    
    try:
        from src.config import config
        print("✓ config importado")
        
        from src.logger import get_logger
        print("✓ logger importado")
        
        from src.database import DatabaseManager
        print("✓ database importado")
        
        from src.csv_handler import CSVHandler
        print("✓ csv_handler importado")
        
        from src.utils import ImageHandler, TextCleaner
        print("✓ utils importado")
        
        from src.scraper import DatabricksScraper
        print("✓ scraper importado")
        
        from src.ai_processor import AIPostProcessor
        print("✓ ai_processor importado")
        
        from src.n8n_integration import N8NIntegration
        print("✓ n8n_integration importado")
        
        from src.main import Application
        print("✓ main importado")
        
        print("\n✅ Todos os módulos importados com sucesso!")
        return True
        
    except Exception as exc:
        print(f"\n❌ Erro ao importar: {str(exc)}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration():
    """Testa se as configurações estão corretas."""
    print("\n" + "=" * 70)
    print("TESTE 2: Configurações")
    print("=" * 70)
    
    try:
        from src.config import config
        
        print(f"✓ Base URL: {config.base_url}")
        print(f"✓ Category URL: {config.category_url}")
        print(f"✓ Target Post Type: {config.target_post_type}")
        print(f"✓ OpenAI Model: {config.openai_model}")
        print(f"✓ Database Name: {config.database_name}")
        print(f"✓ Log Level: {config.log_level}")
        print(f"✓ Selenium Headless: {config.selenium_headless}")
        
        # Verifica API key (sem mostrar o valor completo)
        if config.openai_api_key:
            key_preview = config.openai_api_key[:10] + "..." + config.openai_api_key[-4:]
            print(f"✓ OpenAI API Key: {key_preview}")
        else:
            print("❌ OpenAI API Key não configurada!")
            return False
        
        print("\n✅ Configurações carregadas corretamente!")
        return True
        
    except Exception as exc:
        print(f"\n❌ Erro nas configurações: {str(exc)}")
        import traceback
        traceback.print_exc()
        return False


def test_logger():
    """Testa o sistema de logging."""
    print("\n" + "=" * 70)
    print("TESTE 3: Sistema de Logging")
    print("=" * 70)
    
    try:
        from src.logger import get_logger
        
        logger = get_logger("test_application")
        
        logger.debug("Teste de log DEBUG")
        logger.info("Teste de log INFO")
        logger.warning("Teste de log WARNING")
        
        # Verifica se o arquivo de log foi criado
        if Path("logs/application.log").exists():
            print("✓ Arquivo de log criado")
        else:
            print("⚠ Arquivo de log não encontrado (será criado na primeira execução)")
        
        print("\n✅ Sistema de logging funcionando!")
        return True
        
    except Exception as exc:
        print(f"\n❌ Erro no logging: {str(exc)}")
        import traceback
        traceback.print_exc()
        return False


def test_database():
    """Testa operações do banco de dados."""
    print("\n" + "=" * 70)
    print("TESTE 4: Banco de Dados SQLite")
    print("=" * 70)
    
    try:
        from src.database import DatabaseManager
        from src.config import config
        
        # Inicializa banco
        db = DatabaseManager()
        print("✓ DatabaseManager inicializado")
        
        # Verifica se o banco foi criado
        db_path = config.get_database_path()
        if db_path.exists():
            print(f"✓ Banco de dados existe em: {db_path}")
        else:
            print(f"✓ Banco de dados será criado em: {db_path}")
        
        # Testa operações
        test_link = "https://www.databricks.com/blog/test-post-12345"
        
        # 1. Verifica se não existe
        is_processed = db.is_processed(test_link)
        print(f"✓ is_processed(test_link): {is_processed}")
        
        # 2. Marca como processado
        success = db.mark_as_processed(test_link)
        print(f"✓ mark_as_processed(test_link): {success}")
        
        # 3. Verifica se agora existe
        is_processed_now = db.is_processed(test_link)
        print(f"✓ is_processed(test_link) após marcar: {is_processed_now}")
        
        if not is_processed_now:
            print("❌ Falha ao marcar como processado!")
            return False
        
        # 4. Obtém estatísticas
        stats = db.get_statistics()
        print(f"✓ Total processados: {stats['total_processed']}")
        print(f"✓ Processados hoje: {stats['processed_today']}")
        
        # 5. Testa filter_unprocessed
        test_links = [
            "https://www.databricks.com/blog/test-1",
            "https://www.databricks.com/blog/test-2",
            test_link  # Este já foi processado
        ]
        unprocessed = db.filter_unprocessed(test_links)
        print(f"✓ Links não processados: {len(unprocessed)} de {len(test_links)}")
        
        print("\n✅ Banco de dados funcionando corretamente!")
        print(f"   Localização: {db_path}")
        return True
        
    except Exception as exc:
        print(f"\n❌ Erro no banco de dados: {str(exc)}")
        import traceback
        traceback.print_exc()
        return False


def test_csv_handler():
    """Testa operações com CSV."""
    print("\n" + "=" * 70)
    print("TESTE 5: CSV Handler")
    print("=" * 70)
    
    try:
        from src.csv_handler import CSVHandler
        
        csv_handler = CSVHandler()
        print("✓ CSVHandler inicializado")
        
        # Verifica se CSV existe
        if csv_handler.csv_path.exists():
            print(f"✓ CSV existe: {csv_handler.csv_path}")
            
            # Carrega posts
            posts = csv_handler.load_posts()
            print(f"✓ Posts carregados: {len(posts)}")
            
            # Valida estrutura
            if csv_handler.validate_csv_structure():
                print("✓ Estrutura do CSV válida")
            else:
                print("⚠ Estrutura do CSV pode estar incompleta")
            
            # Estatísticas
            stats = csv_handler.get_statistics()
            print(f"✓ Total de posts: {stats['total_posts']}")
            print(f"✓ Posts com resumo: {stats['posts_with_summary']}")
            print(f"✓ Posts sem resumo: {stats['posts_without_summary']}")
            
            if stats['post_types']:
                print("✓ Distribuição por tipo:")
                for post_type, count in stats['post_types'].items():
                    print(f"    - {post_type}: {count}")
        else:
            print(f"⚠ CSV não encontrado: {csv_handler.csv_path}")
            print("  (Será criado na primeira execução do scraping)")
        
        print("\n✅ CSV Handler funcionando!")
        return True
        
    except Exception as exc:
        print(f"\n❌ Erro no CSV Handler: {str(exc)}")
        import traceback
        traceback.print_exc()
        return False


def test_utils():
    """Testa utilitários."""
    print("\n" + "=" * 70)
    print("TESTE 6: Utilitários")
    print("=" * 70)
    
    try:
        from src.utils import TextCleaner, URLNormalizer
        
        # Testa TextCleaner
        title = "Product/2025/12/New Feature Release"
        cleaned = TextCleaner.clean_title(title)
        print(f"✓ TextCleaner.clean_title()")
        print(f"    Entrada: {title}")
        print(f"    Saída: {cleaned}")
        
        # Testa URLNormalizer
        relative_url = "/blog/test-post"
        base_url = "https://www.databricks.com"
        normalized = URLNormalizer.normalize_url(relative_url, base_url)
        print(f"✓ URLNormalizer.normalize_url()")
        print(f"    Entrada: {relative_url}")
        print(f"    Saída: {normalized}")
        
        print("\n✅ Utilitários funcionando!")
        return True
        
    except Exception as exc:
        print(f"\n❌ Erro nos utilitários: {str(exc)}")
        import traceback
        traceback.print_exc()
        return False


def test_n8n_connection():
    """Testa conexão com n8n."""
    print("\n" + "=" * 70)
    print("TESTE 7: Conexão n8n")
    print("=" * 70)
    
    try:
        from src.n8n_integration import N8NIntegration
        from src.config import config
        
        print(f"✓ Webhook URL: {config.webhook_url[:50]}...")
        
        n8n = N8NIntegration()
        print("✓ N8NIntegration inicializada")
        
        print("\nTestando conexão com webhook...")
        if n8n.test_integration():
            print("✅ Conexão n8n: OK")
            return True
        else:
            print("⚠ Conexão n8n: FALHA")
            print("  (Isso é esperado se o webhook estiver offline)")
            return True  # Não falhamos o teste por isso
        
    except Exception as exc:
        print(f"\n⚠ Erro ao testar n8n: {str(exc)}")
        print("  (Não crítico - webhook pode estar offline)")
        return True


def test_full_flow_simulation():
    """Simula fluxo completo sem executar scraping real."""
    print("\n" + "=" * 70)
    print("TESTE 8: Simulação de Fluxo Completo")
    print("=" * 70)
    
    try:
        from src.database import DatabaseManager
        from src.csv_handler import CSVHandler
        from src.ai_processor import AIPostProcessor
        
        print("\n1. Inicializando componentes...")
        db = DatabaseManager()
        csv_handler = CSVHandler()
        ai_processor = AIPostProcessor()
        print("   ✓ Todos os componentes inicializados")
        
        print("\n2. Verificando dados existentes...")
        
        # CSV
        if csv_handler.csv_path.exists():
            posts = csv_handler.load_posts()
            print(f"   ✓ Posts no CSV: {len(posts)}")
        else:
            print("   ⚠ CSV não existe ainda")
        
        # Banco de dados
        db_stats = db.get_statistics()
        print(f"   ✓ Posts processados (banco): {db_stats['total_processed']}")
        
        # Estatísticas AI
        ai_stats = ai_processor.get_statistics()
        print(f"   ✓ Total processados: {ai_stats['total_processed']}")
        print(f"   ✓ Processados hoje: {ai_stats['processed_today']}")
        
        print("\n✅ Fluxo simulado com sucesso!")
        return True
        
    except Exception as exc:
        print(f"\n❌ Erro na simulação: {str(exc)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes."""
    print("\n" + "=" * 70)
    print("TESTE COMPLETO DA APLICAÇÃO")
    print("Databricks Post Processor v2.0")
    print("=" * 70)
    
    tests = [
        ("Importação de Módulos", test_imports),
        ("Configurações", test_configuration),
        ("Sistema de Logging", test_logger),
        ("Banco de Dados", test_database),
        ("CSV Handler", test_csv_handler),
        ("Utilitários", test_utils),
        ("Conexão n8n", test_n8n_connection),
        ("Simulação de Fluxo", test_full_flow_simulation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as exc:
            print(f"\n❌ Erro crítico no teste '{test_name}': {str(exc)}")
            results.append((test_name, False))
    
    # Relatório final
    print("\n" + "=" * 70)
    print("RELATÓRIO FINAL")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nTestes executados: {total}")
    print(f"Testes passados: {passed}")
    print(f"Testes falhados: {total - passed}")
    
    print("\nDetalhes:")
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"  {status} - {test_name}")
    
    print("\n" + "=" * 70)
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("\nA aplicação está pronta para uso.")
        print("Execute: python src/main.py")
        return 0
    else:
        print(f"⚠️  {total - passed} teste(s) falharam.")
        print("\nRevise os erros acima antes de executar a aplicação.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

