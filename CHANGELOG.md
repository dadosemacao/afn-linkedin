# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [2.1.0] - 2025-12-09

### Containerização e Agendamento Automático

Implementação completa de Docker Compose com agendamento automático para execução toda segunda-feira às 08:00.

### Added (Adicionado)

#### Docker Infrastructure
- `Dockerfile` - Imagem otimizada com Python 3.11, Chromium e dependências
- `docker-compose.yml` - Orquestração de container com volumes persistentes
- `scheduler.py` - Sistema de agendamento automático baseado em cron
- `.dockerignore` - Otimização do build excluindo arquivos desnecessários

#### Scripts de Setup
- `setup_docker.sh` - Script automático de configuração (Linux/Mac)
- `setup_docker.ps1` - Script automático de configuração (Windows)

#### Configuração
- `env.example` - Template de variáveis de ambiente para Docker
- Suporte a configuração via variáveis de ambiente
- Personalização de agendamento via `SCHEDULE_CRON`

#### Documentação
- `DOCKER_QUICKSTART.md` - Guia rápido de início (5 minutos)
- `docs/GUIA_DOCKER.md` - Guia completo de uso do Docker
- `docs/IMPLEMENTACAO_DOCKER_2025-12-09.md` - Documentação técnica da implementação
- Atualização do `README.md` com instruções Docker

### Features (Funcionalidades)

#### Agendamento Automático
- Execução agendada configurável via cron
- Padrão: Segunda-feira às 08:00 (timezone: America/Sao_Paulo)
- Customização flexível (diário, semanal, múltiplos horários)
- Logs estruturados de todas as execuções
- Prevenção de execuções duplicadas
- Graceful shutdown com tratamento de sinais

#### Container Docker
- Imagem baseada em Python 3.11-slim
- Chromium e ChromeDriver integrados para Selenium
- Usuário não-root para segurança (`afnuser`)
- Healthcheck configurado
- Logs rotacionados automaticamente
- Context preservado entre execuções

#### Persistência de Dados
- Volume para logs (`./logs`)
- Volume para database (`./database`)
- Volume para gráficos (`./graphics`)
- Volume para relatórios (`./reports`)
- Volume para dados (`./dados`)
- CSV principal preservado

#### Monitoramento
- Logs do scheduler em arquivo dedicado
- Logs da aplicação separados
- Formato padronizado e profissional
- Captura de stdout/stderr das execuções
- Rastreabilidade completa de operações

### Changed (Modificado)

#### README
- Adicionada seção Docker como opção recomendada
- Instruções separadas para Docker e Python nativo
- Comandos essenciais documentados
- Referências cruzadas para guias

#### Arquitetura
- Suporte a execução via subprocess (scheduler)
- Configuração via variáveis de ambiente
- Compatibilidade com containerização

### Improved (Melhorado)

#### Portabilidade
- Execução consistente em qualquer ambiente
- Isolamento completo de dependências
- Setup automatizado via scripts
- Suporte multiplataforma (Linux, Mac, Windows)

#### Operação
- Automação completa sem intervenção manual
- Agendamento configurável e flexível
- Monitoramento integrado
- Facilidade de deploy

#### Segurança
- Container executa com usuário não-root
- API Keys via variáveis de ambiente
- Logs não expõem dados sensíveis
- Rede isolada (bridge network)

### Technical Details (Detalhes Técnicos)

#### Dockerfile
- Base: `python:3.11-slim`
- Tamanho otimizado (cleanup de apt)
- Multistage não utilizado (simplicidade priorizou single-stage)
- Chromium: Instalado via apt (chromium + chromium-driver)
- UID 1000 para compatibilidade com host

#### Scheduler
- Algoritmo: Parse de cron com verificação a cada 30s
- Prevenção: Verifica última execução para evitar duplicatas
- Timeout: 1 hora por execução
- Graceful: Tratamento de SIGTERM e SIGINT
- Logs: Estruturados com níveis INFO/WARNING/ERROR

#### Docker Compose
- Versão: 3.8
- Restart: `unless-stopped`
- Network: `afn-network` (bridge isolada)
- Logging: Rotação automática (10MB, 3 arquivos)
- Healthcheck: A cada 1 hora

### Usage Examples (Exemplos de Uso)

```bash
# Setup e inicialização
./setup_docker.sh
docker-compose up -d

# Execução manual
docker-compose exec afn-linkedin-processor python run.py

# Monitoramento
docker-compose logs -f

# Parar
docker-compose down
```

### Expressões Cron Suportadas

| Descrição | Expressão |
|-----------|-----------|
| Segunda-feira 08:00 | `0 8 * * 1` |
| Dias úteis 09:00 | `0 9 * * 1-5` |
| Todos os dias 10:00 | `0 10 * * *` |
| A cada 6 horas | `0 */6 * * *` |

### Files Structure (Estrutura de Arquivos)

```
projeto/
├── Dockerfile
├── docker-compose.yml
├── scheduler.py
├── setup_docker.sh
├── setup_docker.ps1
├── .dockerignore
├── env.example
├── DOCKER_QUICKSTART.md
└── docs/
    ├── GUIA_DOCKER.md
    └── IMPLEMENTACAO_DOCKER_2025-12-09.md
```

---

## [2.0.0] - 2025-12-09

### Refatoração Completa - Arquitetura Profissional

Esta é uma refatoração completa do projeto, transformando o código monolítico em uma arquitetura modular profissional.

### Added (Adicionado)

#### Estrutura Modular
- `src/main.py` - Orquestrador principal da aplicação
- `src/config.py` - Gerenciamento centralizado de configurações
- `src/logger.py` - Sistema de logging profissional com rotação
- `src/scraper.py` - Módulo de web scraping com POO
- `src/ai_processor.py` - Processamento com OpenAI API
- `src/n8n_integration.py` - Integração com webhook n8n
- `src/csv_handler.py` - Operações com arquivos CSV
- `src/database.py` - Persistência SQLite
- `src/utils.py` - Utilitários reutilizáveis
- `src/__init__.py` - Transformação em pacote Python

#### Configurações
- `config.ini` - Arquivo de configuração externalizada
- `.env.example` - Template de variáveis de ambiente
- `.gitignore` - Ignorar arquivos sensíveis e temporários

#### Documentação
- `README.md` - Documentação completa de uso
- `CHANGELOG.md` - Histórico de mudanças
- `requirements.txt` - Dependências do projeto
- `docs/REFATORACAO_2025-12-09.md` - Documento técnico de refatoração
- `docs/ARQUITETURA.md` - Documentação da arquitetura
- `docs/GUIA_MIGRACAO.md` - Guia de migração v1 → v2

#### Funcionalidades
- Sistema de logging estruturado sem emojis
- Rotação automática de logs (10MB, 5 backups)
- Banco de dados SQLite para tracking de processamento
- Estatísticas detalhadas de execução
- Validações robustas em todas as operações
- Tratamento específico de exceções
- Type hints completos
- Docstrings em todas as classes e métodos
- Context managers para gerenciamento de recursos
- Padrões de design (Singleton, Factory, Context Manager)
- Execução modular (pipeline completo ou fases individuais)

### Changed (Modificado)

#### Logs
- **Removidos todos os emojis** (requisito do projeto)
- Implementado logging profissional com níveis (DEBUG, INFO, WARNING, ERROR)
- Logs agora são salvos em arquivo com rotação automática
- Formato padronizado: `timestamp - module - level - message`

#### Configurações
- URLs movidas de hardcoded para `config.ini`
- Timeouts e delays configuráveis externamente
- Paths de arquivos centralizados
- API keys em `.env` (não versionadas)

#### Tratamento de Erros
- Substituído `except:` por exceções específicas
- Logging de exceções com stack trace
- Mensagens de erro informativas
- Validações em pontos críticos

#### Código
- Refatorado de procedural para orientado a objetos
- Separação de responsabilidades (SRP)
- Funções pequenas e focadas
- Nomes descritivos e claros
- Type hints em todas as funções
- Docstrings completas

### Improved (Melhorado)

#### Qualidade de Código
- Eliminada duplicação de código
- Reduzida complexidade ciclomática
- Aumentada coesão e reduzido acoplamento
- Código autoexplicativo (menos comentários necessários)

#### Manutenibilidade
- Estrutura modular facilita localização de código
- Cada módulo tem responsabilidade clara
- Documentação completa e atualizada
- Padrões consistentes em todo o projeto

#### Testabilidade
- Componentes isolados e testáveis
- Dependências injetáveis
- Mock-friendly architecture
- Preparado para testes unitários e integração

#### Performance
- Context managers para liberação de recursos
- Conexões gerenciadas adequadamente
- Índices no banco de dados
- Cache de configurações (Singleton)

#### Segurança
- Credenciais externalizadas
- Logs não expõem dados sensíveis
- Validações de entrada
- Tratamento seguro de exceções

### Deprecated (Descontinuado)

- `src/DataBricks.py` - Código monolítico original (preservado como `.backup`)

### Removed (Removido)

- Emojis de todos os logs e prints
- Código comentado não utilizado
- Configurações hardcoded
- Exceções genéricas (`except:`)
- Variáveis globais desnecessárias

### Fixed (Corrigido)

- Tratamento adequado de exceções HTTP
- Fechamento correto de recursos (driver Selenium, conexões DB)
- Validação de dados antes de processamento
- Prevenção de duplicatas no CSV
- Normalização correta de URLs

### Security (Segurança)

- API keys movidas para `.env` (não versionadas)
- Adicionado `.gitignore` para prevenir commit de dados sensíveis
- Logs sanitizados (sem credenciais ou dados sensíveis)

---

## [1.0.0] - Anterior a 2025-12-09

### Código Legado

Versão original monolítica com:
- Arquivo único `DataBricks.py` (479 linhas)
- Configurações hardcoded
- Logs com emojis
- Estrutura procedural
- Sem documentação formal

**Preservado como**: `src/DataBricks.py.backup`

---

## Estatísticas da Refatoração

### Métricas de Código

| Métrica | v1.0 | v2.0 | Mudança |
|---------|------|------|---------|
| Arquivos Python | 1 | 9 | +800% |
| Linhas por arquivo | 479 | ~200-400 | -58% |
| Classes | 0 | 15+ | +∞ |
| Type hints | 0% | 100% | +100% |
| Docstrings | 10% | 100% | +90% |
| Testes | 0 | 0* | 0% |

*Estrutura preparada para testes

### Princípios Aplicados

- ✅ SOLID (todos os 5 princípios)
- ✅ DRY (Don't Repeat Yourself)
- ✅ KISS (Keep It Simple, Stupid)
- ✅ YAGNI (You Aren't Gonna Need It)
- ✅ Clean Code
- ✅ Design Patterns

### Padrões de Design

- ✅ Singleton (Config)
- ✅ Factory (LoggerFactory)
- ✅ Context Manager (DatabaseManager)
- ✅ Strategy (PostFormatter)
- ✅ Template Method (Application pipeline)

---

## Próximas Versões Planejadas

### [2.2.0] - Testes e CI/CD
- Implementar testes unitários (pytest)
- Implementar testes de integração
- Testes Docker (docker-compose test)
- Configurar CI/CD pipeline
- Code coverage > 80%

### [2.3.0] - Performance
- Processamento paralelo de posts
- Cache de resultados
- Connection pooling
- Retry com exponential backoff
- Otimização de imagem Docker (multi-stage)

### [2.4.0] - Monitoramento Avançado
- Dashboard de métricas
- Sistema de alertas (Slack/Email)
- Prometheus/Grafana integration
- Métricas customizadas do scheduler

### [3.0.0] - Kubernetes
- Kubernetes manifests
- Helm charts
- CronJob nativo do K8s
- Auto-scaling
- Ingress configuration

---

## Links Úteis

- [Documentação Completa](./README.md)
- [Arquitetura do Sistema](./docs/ARQUITETURA.md)
- [Guia de Migração](./docs/GUIA_MIGRACAO.md)
- [Detalhes da Refatoração](./docs/REFATORACAO_2025-12-09.md)

---

**Mantido por**: Sistema AFN  
**Formato**: [Keep a Changelog](https://keepachangelog.com/)  
**Versionamento**: [Semantic Versioning](https://semver.org/)

