# Databricks Post Processor

Sistema profissional de scraping, processamento com IA e integração de posts do blog Databricks.

## Visão Geral

Esta aplicação realiza três operações principais:

1. **Scraping**: Extrai posts da categoria "Platform" do blog Databricks
2. **Processamento IA**: Gera resumos profissionais usando OpenAI GPT
3. **Integração n8n**: Envia posts processados para webhook n8n

## Arquitetura

```
src/
├── main.py              # Orquestrador principal
├── config.py            # Gerenciamento de configurações
├── logger.py            # Sistema de logging profissional
├── scraper.py           # Web scraping com Selenium
├── ai_processor.py      # Processamento com OpenAI
├── n8n_integration.py   # Integração webhook n8n
├── csv_handler.py       # Operações CSV
├── database.py          # Persistência SQLite
└── utils.py             # Utilitários gerais

config.ini              # Configurações da aplicação
.env                    # Variáveis de ambiente (API keys)
```

## Pré-requisitos

- Python 3.9 ou superior
- Google Chrome instalado
- Chave de API OpenAI
- Acesso ao webhook n8n (opcional)

## Instalação

### 1. Clone o repositório

```bash
git clone <repository-url>
cd Linkedin
```

### 2. Crie ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale dependências

```bash
pip install -r requirements.txt
```

### 4. Configure variáveis de ambiente

Crie arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sua_chave_api_aqui
ENVIRONMENT=production
```

### 5. Ajuste configurações (opcional)

Edite `config.ini` conforme necessário:

- URLs de scraping
- Configurações do Selenium
- Parâmetros OpenAI
- Webhook n8n

## Uso

### Executar Pipeline Completo

```bash
python run.py
```

Executa todas as fases: scraping → processamento → integração

**Alternativas**:
```bash
# Como módulo Python
python -m src.main

# Direto (se PYTHONPATH configurado)
python src/main.py
```

### Executar Fases Individuais

Edite `src/main.py` e escolha o método desejado:

```python
# Apenas scraping
app.run_scraping()

# Apenas processamento IA
app.run_ai_processing()

# Apenas integração n8n
app.run_n8n_integration()

# Pipeline completo
app.run_full_pipeline()
```

## Estrutura de Dados

### Posts CSV

```csv
post_type,title,cover_image,link,resumo,data_resumo
Product,Article Title,https://...,https://...,Resumo do post...,09/12/2025 14:30
```

### Resumos JSON

```json
[
  {
    "titulo": "Article Title",
    "link": "https://...",
    "data": "09/12/2025 14:30",
    "conteudo": "Resumo profissional..."
  }
]
```

## Logs

Os logs são armazenados em `logs/application.log` com rotação automática:

- Nível: INFO (configurável)
- Formato: `timestamp - module - level - message`
- Rotação: 10MB por arquivo, 5 backups
- **Sem emojis** - logs profissionais

## Banco de Dados

SQLite em `database/resumos_processados.db`:

- Rastreia posts já processados
- Previne reprocessamento desnecessário
- Estatísticas de uso

## Melhores Práticas Implementadas

### Código

- ✅ Programação Orientada a Objetos
- ✅ Separação de responsabilidades (SRP)
- ✅ Type hints em todas as funções
- ✅ Documentação completa (docstrings)
- ✅ Tratamento robusto de exceções
- ✅ Logging estruturado e profissional
- ✅ Configurações externalizadas

### Arquitetura

- ✅ Padrão Singleton para configuração
- ✅ Context managers para recursos
- ✅ Factory pattern para loggers
- ✅ Modularização clara
- ✅ Baixo acoplamento

### Operacional

- ✅ Logs sem emojis (requisito do projeto)
- ✅ Versionamento Git adequado
- ✅ Documentação técnica completa
- ✅ Estrutura de diretórios padronizada
- ✅ Rastreabilidade de execuções

## Solução de Problemas

### Erro: "OPENAI_API_KEY não configurada"

Configure a variável de ambiente no arquivo `.env`

### Erro: "Arquivo config.ini não encontrado"

Certifique-se de que `config.ini` está na raiz do projeto

### Chrome Driver não encontrado

O webdriver-manager baixa automaticamente. Verifique conexão internet.

### Posts não sendo processados

Verifique:
1. Posts já foram processados? (banco de dados)
2. Logs em `logs/application.log`
3. CSV existe e está válido?

## Estatísticas

Ao final da execução, o sistema exibe:

- Total de posts extraídos
- Posts com/sem resumo
- Distribuição por tipo
- Posts processados hoje
- Resumos armazenados

## Contribuição

1. Siga as diretrizes do Prompt Base
2. Mantenha logs sem emojis
3. Documente mudanças em `docs/`
4. Faça commits descritivos
5. Teste antes de commitar

## Licença

Copyright © 2025 - Sistema AFN

## Suporte

Para dúvidas ou problemas:
1. Consulte logs em `logs/application.log`
2. Verifique documentação em `docs/`
3. Analise código fonte (bem documentado)

---

**Desenvolvido seguindo os princípios de:**
- Clareza e simplicidade
- Escalabilidade
- Manutenibilidade
- Rastreabilidade
- Excelência técnica

