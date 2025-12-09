# Arquitetura do Sistema

## Visão Geral

O Databricks Post Processor é uma aplicação modular desenvolvida seguindo princípios SOLID e padrões de design profissionais.

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                       │
│                        (main.py)                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Application Orchestrator                            │  │
│  │  - run_scraping()                                    │  │
│  │  - run_ai_processing()                              │  │
│  │  - run_n8n_integration()                            │  │
│  │  - run_full_pipeline()                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ├─────────────────────────┐
                           │                         │
                           ▼                         ▼
┌─────────────────────────────────┐  ┌──────────────────────────────┐
│    SCRAPING LAYER               │  │   PROCESSING LAYER           │
│    (scraper.py)                 │  │   (ai_processor.py)          │
│                                 │  │                              │
│  ┌──────────────────────────┐  │  │  ┌────────────────────────┐ │
│  │  DatabricksScraper       │  │  │  │  AIPostProcessor       │ │
│  │  - scrape_posts()        │  │  │  │  - process_posts()     │ │
│  └──────────────────────────┘  │  │  └────────────────────────┘ │
│  ┌──────────────────────────┐  │  │  ┌────────────────────────┐ │
│  │  SeleniumDriver          │  │  │  │  OpenAIClient          │ │
│  │  - WebDriver management  │  │  │  │  - API communication   │ │
│  └──────────────────────────┘  │  │  └────────────────────────┘ │
│  ┌──────────────────────────┐  │  │  ┌────────────────────────┐ │
│  │  PostExtractor           │  │  │  │  SummaryGenerator      │ │
│  │  - Extract post data     │  │  │  │  - Generate summaries  │ │
│  └──────────────────────────┘  │  │  └────────────────────────┘ │
└─────────────────────────────────┘  │  ┌────────────────────────┐ │
                                     │  │  SummaryStorage        │ │
                                     │  │  - JSON persistence    │ │
                                     │  └────────────────────────┘ │
                                     └──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              INTEGRATION LAYER                               │
│              (n8n_integration.py)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  N8NIntegration                                      │  │
│  │  - send_posts()                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  N8NWebhookClient                                    │  │
│  │  - HTTP communication                                │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  PostFormatter                                       │  │
│  │  - Format data for n8n                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 INFRASTRUCTURE LAYER                         │
├─────────────────────────────────────────────────────────────┤
│  Config (config.py)         │  Logger (logger.py)           │
│  - Singleton pattern        │  - Factory pattern            │
│  - Centralized config       │  - Structured logging         │
├─────────────────────────────────────────────────────────────┤
│  CSVHandler (csv_handler.py) │ Database (database.py)      │
│  - CSV operations            │  - SQLite persistence        │
│  - Pandas integration        │  - Context managers          │
├─────────────────────────────────────────────────────────────┤
│  Utils (utils.py)                                           │
│  - ImageHandler, TextCleaner, HTMLParser, URLNormalizer     │
└─────────────────────────────────────────────────────────────┘
```

## Camadas e Responsabilidades

### 1. Application Layer
**Arquivo**: `main.py`

Responsável por:
- Orquestração do fluxo de execução
- Coordenação entre módulos
- Tratamento de erros em alto nível
- Estatísticas e relatórios

**Classes principais**:
- `Application`: Orquestrador principal

### 2. Scraping Layer
**Arquivo**: `scraper.py`

Responsável por:
- Web scraping com Selenium
- Navegação e extração de dados
- Gerenciamento do WebDriver
- Limpeza e normalização de dados

**Classes principais**:
- `DatabricksScraper`: Coordenador de scraping
- `SeleniumDriver`: Gerenciamento do Selenium
- `PostExtractor`: Extração de dados de posts

### 3. Processing Layer
**Arquivo**: `ai_processor.py`

Responsável por:
- Integração com OpenAI API
- Geração de resumos
- Persistência de resumos
- Controle de processamento

**Classes principais**:
- `AIPostProcessor`: Coordenador de processamento
- `OpenAIClient`: Cliente OpenAI
- `SummaryGenerator`: Gerador de resumos
- `SummaryStorage`: Armazenamento JSON

### 4. Integration Layer
**Arquivo**: `n8n_integration.py`

Responsável por:
- Comunicação HTTP com n8n
- Formatação de dados para webhook
- Tratamento de imagens binárias
- Testes de integração

**Classes principais**:
- `N8NIntegration`: Coordenador de integração
- `N8NWebhookClient`: Cliente HTTP
- `PostFormatter`: Formatador de dados

### 5. Infrastructure Layer
**Arquivos**: `config.py`, `logger.py`, `csv_handler.py`, `database.py`, `utils.py`

Responsável por:
- Configurações centralizadas
- Sistema de logging
- Operações de I/O
- Persistência de dados
- Utilitários gerais

**Classes principais**:
- `Config`: Gerenciamento de configurações (Singleton)
- `LoggerFactory`: Criação de loggers (Factory)
- `CSVHandler`: Operações CSV
- `DatabaseManager`: Persistência SQLite
- `ImageHandler`, `TextCleaner`, etc: Utilitários

## Fluxo de Dados

```
1. SCRAPING
   ┌──────────────┐
   │ Web Page     │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Selenium     │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ PostExtractor│
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ CSV Handler  │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ posts.csv    │
   └──────────────┘

2. PROCESSING
   ┌──────────────┐
   │ posts.csv    │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ CSVHandler   │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ AIProcessor  │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ OpenAI API   │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Storage      │
   └──────┬───────┘
          │
          ├──────────┐
          ▼          ▼
   ┌──────────┐ ┌──────────┐
   │ JSON     │ │ SQLite   │
   └──────────┘ └──────────┘

3. INTEGRATION
   ┌──────────────┐
   │ posts.csv    │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ CSVHandler   │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Formatter    │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Image DL     │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ n8n Webhook  │
   └──────────────┘
```

## Padrões de Design Utilizados

### 1. Singleton
**Onde**: `Config` (config.py)

Garante única instância de configuração no sistema.

```python
class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 2. Factory
**Onde**: `LoggerFactory` (logger.py)

Centraliza criação de loggers configurados.

```python
class LoggerFactory:
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        # Cria e configura logger
        pass
```

### 3. Context Manager
**Onde**: `DatabaseManager` (database.py)

Gerencia recursos do banco de dados.

```python
@contextmanager
def _get_connection(self):
    conn = sqlite3.connect(self.db_path)
    try:
        yield conn
    finally:
        conn.close()
```

### 4. Strategy
**Onde**: `PostFormatter` (n8n_integration.py)

Permite diferentes estratégias de formatação.

### 5. Template Method
**Onde**: `Application.run_full_pipeline()` (main.py)

Define estrutura de algoritmo com passos customizáveis.

## Princípios SOLID

### Single Responsibility
Cada classe tem uma única responsabilidade:
- `SeleniumDriver`: Apenas gerencia Selenium
- `OpenAIClient`: Apenas comunica com OpenAI
- `CSVHandler`: Apenas opera CSV

### Open/Closed
Sistema extensível sem modificar código existente:
- Novas fontes de scraping: herdar `PostExtractor`
- Novos formatos de saída: implementar interface de formatter
- Novas integrações: criar nova classe de integration

### Liskov Substitution
Subtipos podem substituir tipos base sem quebrar sistema.

### Interface Segregation
Interfaces específicas e focadas.

### Dependency Inversion
Dependência de abstrações, não de implementações concretas.

## Segurança

### Credenciais
- API keys em `.env` (não versionado)
- Configurações sensíveis externalizadas
- Nenhuma credencial no código

### Logs
- Logs não contêm dados sensíveis
- Rotação automática previne crescimento descontrolado
- Níveis adequados de severidade

### Exceções
- Tratamento específico por tipo
- Mensagens informativas sem expor internals
- Logging de stack traces apenas em desenvolvimento

## Performance

### Otimizações
- Context managers para liberação de recursos
- Conexões reutilizáveis
- Lazy loading onde possível
- Índices no banco de dados
- Cache de configurações

### Limitações
- Selenium pode ser lento (headless minimiza)
- API OpenAI tem rate limits
- Processamento sequencial de posts

### Melhorias Futuras
- Processamento paralelo de posts
- Cache de resultados
- Retry com exponential backoff
- Connection pooling

## Testes

### Estratégia
1. **Testes Unitários**: Cada classe isoladamente
2. **Testes de Integração**: Fluxo entre componentes
3. **Testes E2E**: Pipeline completo

### Ferramentas Sugeridas
- `pytest`: Framework de testes
- `pytest-mock`: Mocks
- `pytest-cov`: Coverage
- `black`: Formatação
- `flake8`: Linting
- `mypy`: Type checking

## Deployment

### Requisitos
- Python 3.9+
- Chrome instalado
- Conexão internet
- OpenAI API key
- n8n webhook (opcional)

### Ambientes
- **Desenvolvimento**: Logs DEBUG, modo não-headless
- **Produção**: Logs INFO, modo headless

### Containerização
```dockerfile
FROM python:3.9-slim
RUN apt-get update && apt-get install -y chromium chromium-driver
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/main.py"]
```

## Monitoramento

### Logs
- `logs/application.log`: Log principal
- Rotação: 10MB por arquivo, 5 backups
- Formato estruturado para parsing

### Métricas
- Posts extraídos
- Posts processados
- Resumos gerados
- Envios n8n
- Erros por tipo

### Alertas Sugeridos
- Falhas consecutivas no scraping
- API OpenAI indisponível
- Webhook n8n down
- Disco cheio (logs)

## Manutenção

### Rotinas
1. **Diária**: Verificar logs de erro
2. **Semanal**: Analisar estatísticas
3. **Mensal**: Revisar configurações
4. **Trimestral**: Atualizar dependências

### Troubleshooting
1. Consultar `logs/application.log`
2. Verificar configurações em `config.ini`
3. Validar credenciais em `.env`
4. Testar conectividade (n8n, OpenAI)

---

**Última atualização**: 09/12/2025  
**Versão**: 2.0.0

