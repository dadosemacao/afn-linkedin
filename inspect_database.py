"""
Script de Inspeção do Banco de Dados
=====================================
Inspeciona o conteúdo do banco resumos_processados.db

Author: Sistema AFN
Date: 2025-12-09
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def inspect_database():
    """Inspeciona o banco de dados e mostra informações detalhadas."""
    
    db_path = Path("database/resumos_processados.db")
    
    print("\n" + "=" * 70)
    print("INSPEÇÃO DO BANCO DE DADOS")
    print("=" * 70)
    
    if not db_path.exists():
        print("\n❌ Banco de dados não encontrado!")
        print(f"   Localização esperada: {db_path}")
        return
    
    print(f"\n✓ Banco encontrado: {db_path}")
    print(f"✓ Tamanho: {db_path.stat().st_size:,} bytes")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Schema
    print("\n" + "-" * 70)
    print("1. ESTRUTURA DO BANCO (Schema)")
    print("-" * 70)
    
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    for row in cursor.fetchall():
        print(row[0])
    
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='index';")
    indices = cursor.fetchall()
    if indices:
        print("\nÍndices:")
        for row in indices:
            if row[0]:  # Índice não auto-gerado
                print(row[0])
    
    # 2. Contagem
    print("\n" + "-" * 70)
    print("2. ESTATÍSTICAS GERAIS")
    print("-" * 70)
    
    cursor.execute("SELECT COUNT(*) FROM processados;")
    total = cursor.fetchone()[0]
    print(f"✓ Total de posts processados: {total}")
    
    # 3. Posts processados hoje
    cursor.execute("""
        SELECT COUNT(*) FROM processados 
        WHERE DATE(processed_at) = DATE('now');
    """)
    today = cursor.fetchone()[0]
    print(f"✓ Posts processados hoje: {today}")
    
    # 4. Por data
    print("\n" + "-" * 70)
    print("3. PROCESSAMENTO POR DATA")
    print("-" * 70)
    
    cursor.execute("""
        SELECT DATE(processed_at) as data, COUNT(*) as quantidade
        FROM processados
        GROUP BY DATE(processed_at)
        ORDER BY data DESC;
    """)
    
    results = cursor.fetchall()
    if results:
        print(f"\n{'Data':<12} | {'Quantidade':<10}")
        print("-" * 25)
        for data, qtd in results:
            print(f"{data:<12} | {qtd:<10}")
    else:
        print("Nenhum registro encontrado.")
    
    # 5. Todos os registros
    print("\n" + "-" * 70)
    print("4. TODOS OS REGISTROS")
    print("-" * 70)
    
    cursor.execute("""
        SELECT id, link, processed_at, created_at
        FROM processados
        ORDER BY id;
    """)
    
    records = cursor.fetchall()
    if records:
        print(f"\nTotal: {len(records)} registro(s)\n")
        for id, link, processed, created in records:
            print(f"ID: {id}")
            print(f"Link: {link}")
            print(f"Processado em: {processed}")
            print(f"Criado em: {created}")
            print("-" * 70)
    else:
        print("Nenhum registro encontrado.")
    
    # 6. Últimos 10 processados
    print("\n" + "-" * 70)
    print("5. ÚLTIMOS 10 PROCESSADOS")
    print("-" * 70)
    
    cursor.execute("""
        SELECT id, link, processed_at
        FROM processados
        ORDER BY processed_at DESC
        LIMIT 10;
    """)
    
    recent = cursor.fetchall()
    if recent:
        for id, link, processed in recent:
            # Simplifica o link para exibição
            short_link = link if len(link) <= 60 else link[:57] + "..."
            print(f"{id:3d} | {processed} | {short_link}")
    else:
        print("Nenhum registro encontrado.")
    
    # 7. Integridade
    print("\n" + "-" * 70)
    print("6. VERIFICAÇÃO DE INTEGRIDADE")
    print("-" * 70)
    
    cursor.execute("PRAGMA integrity_check;")
    integrity = cursor.fetchone()[0]
    if integrity == "ok":
        print("✓ Integridade do banco: OK")
    else:
        print(f"⚠ Problema de integridade: {integrity}")
    
    # 8. Links únicos
    cursor.execute("SELECT COUNT(DISTINCT link) FROM processados;")
    unique_links = cursor.fetchone()[0]
    print(f"✓ Links únicos: {unique_links} (deve ser igual ao total: {total})")
    
    if unique_links == total:
        print("✓ Constraint UNIQUE funcionando corretamente!")
    else:
        print("⚠ Existem duplicatas no banco!")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("INSPEÇÃO CONCLUÍDA")
    print("=" * 70)
    print("\n✅ Banco de dados está funcionando corretamente!")
    print(f"✅ Total de {total} post(s) rastreado(s)")
    print(f"✅ Processados hoje: {today}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    inspect_database()

