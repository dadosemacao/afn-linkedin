# Implementação Docker e Agendamento Automático

**Autor**: Sistema AFN  
**Data**: 2025-12-09  
**Versão**: 1.0.0  
**Tipo**: Implementação Técnica

---

## 1. Contexto e Motivação

### 1.1. Objetivo

Implementar containerização da aplicação **Databricks Post Processor** com agendamento automático para execução toda segunda-feira às 08:00, garantindo:

- **Portabilidade**: Execução consistente em qualquer ambiente
- **Isolamento**: Dependências encapsuladas
- **Automação**: Agendamento sem intervenção manual
- **Rastreabilidade**: Logs e monitoramento centralizados

### 1.2. Requisitos Atendidos

- ✅ Containerização completa da aplicação
- ✅ Agendamento via cron (segunda-feira 08:00)
- ✅ Persistência de dados (logs, database, CSV)
- ✅ Configuração via variáveis de ambiente
- ✅ Monitoramento e healthcheck
- ✅ Documentação completa

---

## 2. Arquitetura da Solução

### 2.1. Componentes Implementados

```
┌─────────────────────────────────────────────┐
│         Docker Compose Orchestration        │
└─────────────────────────────────────────────┘
                    │
    ┌───────────────┴───────────────┐
    │                               │
    ▼                               ▼
┌─────────────┐              ┌─────────────┐
│  Container  │              │   Volumes   │
│   Python    │◄─────────────┤ Persistentes│
│   3.11      │              │             │
└──────┬──────┘              └─────────────┘
       │
       ├─► Scheduler (scheduler.py)
       │   └─► Cron Logic
       │
       ├─► Application (run.py)
       │   ├─► Scraper
       │   ├─► AI Processor
       │   └─► N8N Integration
       │
       └─► Selenium + Chromium
```

### 2.2. Fluxo de Execução

```
1. Container Start
   └─► scheduler.py inicia

2. Scheduler Loop
   ├─► Verifica expressão cron a cada 30s
   ├─► Aguarda momento configurado
   └─► Dispara execução

3. Execução Agendada
   ├─► Log: "INICIANDO EXECUCAO AGENDADA"
   ├─► Executa: python run.py
   ├─► Captura stdout/stderr
   ├─► Registra resultado
   └─► Retorna ao loop

4. Pipeline da Aplicação
   ├─► Fase 1: Scraping
   ├─► Fase 2: Processamento IA
   ├─► Fase 3: Integração n8n
   └─► Estatísticas finais
```

---

## 3. Arquivos Criados

### 3.1. Dockerfile

**Localização**: `./Dockerfile`

**Principais Features**:
- Base: `python:3.11-slim`
- Instalação de Chromium e ChromeDriver para Selenium
- Cron para agendamento
- Usuário não-root (`afnuser`) para segurança
- Healthcheck configurado

**Estrutura de Camadas**:
```dockerfile
Layer 1: Sistema base Python 3.11
Layer 2: Dependências do sistema (Chrome, cron)
Layer 3: Dependências Python (requirements.txt)
Layer 4: Estrutura de diretórios
Layer 5: Código da aplicação
Layer 6: Scheduler e configurações
Layer 7: Permissões e usuário
```

### 3.2. docker-compose.yml

**Localização**: `./docker-compose.yml`

**Configurações Principais**:

```yaml
services:
  afn-linkedin-processor:
    - restart: unless-stopped
    - environment: Variáveis via .env
    - volumes: Persistência de dados
    - networks: Rede isolada
    - logging: Rotação automática
    - healthcheck: Verificação periódica
```

**Volumes Mapeados**:
- `./logs` → Logs da aplicação
- `./database` → SQLite database
- `./graphics` → Gráficos gerados
- `./reports` → Relatórios
- `./dados` → Datasets

### 3.3. scheduler.py

**Localização**: `./scheduler.py`

**Classe Principal**: `ApplicationScheduler`

**Funcionalidades**:
1. **Parse de Expressão Cron**: Interpreta formato cron
2. **Verificação Temporal**: Compara com datetime atual
3. **Execução Controlada**: Evita duplicações
4. **Logging Estruturado**: Registra todas as operações
5. **Graceful Shutdown**: Trata sinais de encerramento

**Algoritmo de Agendamento**:
```python
Loop Principal:
  1. Obter datetime.now()
  2. Parse expressão cron
  3. Comparar componentes (minuto, hora, dia, mês, dia-semana)
  4. Se match completo:
     a. Verificar última execução (evitar duplicação)
     b. Executar subprocess: python run.py
     c. Capturar output
     d. Registrar resultado
  5. Sleep 30 segundos
  6. Repetir
```

### 3.4. env.example

**Localização**: `./env.example`

**Variáveis Obrigatórias**:
- `OPENAI_API_KEY`: Chave da API OpenAI

**Variáveis Opcionais**:
- `SCHEDULE_ENABLED`: Ativar/desativar agendamento
- `SCHEDULE_CRON`: Expressão cron personalizada
- `LOG_LEVEL`: Nível de logging
- `TZ`: Fuso horário

### 3.5. .dockerignore

**Localização**: `./.dockerignore`

**Exclusões**:
- Arquivos Python compilados (`__pycache__`, `.pyc`)
- Ambientes virtuais (`venv/`, `env/`)
- Git e IDEs (`.git`, `.vscode`)
- Logs e databases locais
- Documentação desnecessária

### 3.6. Scripts de Setup

**Localização**: 
- `./setup_docker.sh` (Linux/Mac)
- `./setup_docker.ps1` (Windows)

**Funcionalidades**:
1. Verificação de pré-requisitos (Docker, Docker Compose)
2. Criação de arquivo `.env`
3. Configuração interativa de API Key
4. Criação de estrutura de diretórios
5. Build inicial da imagem
6. Instruções de uso

---

## 4. Configuração de Agendamento

### 4.1. Formato Cron

**Estrutura**: `minuto hora dia mês dia-da-semana`

**Componentes**:
- `minuto`: 0-59
- `hora`: 0-23
- `dia`: 1-31
- `mês`: 1-12
- `dia-da-semana`: 0-7 (0 e 7 = domingo, 1 = segunda)

### 4.2. Exemplos Práticos

| Caso de Uso | Expressão Cron | Descrição |
|-------------|----------------|-----------|
| **Padrão** | `0 8 * * 1` | Segunda-feira às 08:00 |
| Dias úteis | `0 8 * * 1-5` | Segunda a Sexta às 08:00 |
| Múltiplos horários | `0 9,15 * * *` | 09:00 e 15:00 diariamente |
| A cada 30min | `*/30 * * * *` | A cada 30 minutos |
| Semanal | `0 8 * * 1` | Toda semana (segunda) |
| Mensal | `0 8 1 * *` | Todo dia 1º às 08:00 |

### 4.3. Validação de Cron

**Ferramentas**:
- [Crontab.guru](https://crontab.guru/) - Validador online
- Logs do scheduler - Descrição em linguagem natural

---

## 5. Segurança e Boas Práticas

### 5.1. Segurança Implementada

1. **Usuário Não-Root**
   ```dockerfile
   RUN useradd -m -u 1000 afnuser
   USER afnuser
   ```

2. **Variáveis de Ambiente**
   - API Keys fora do código
   - Arquivo `.env` no `.gitignore`
   - Exemplo fornecido (`env.example`)

3. **Isolamento de Rede**
   ```yaml
   networks:
     afn-network:
       driver: bridge
   ```

4. **Logs Rotacionados**
   ```yaml
   logging:
     options:
       max-size: "10m"
       max-file: "3"
   ```

### 5.2. Boas Práticas Aplicadas

- ✅ **Multi-stage não utilizado** (simplicidade priorizou single-stage)
- ✅ **Camadas otimizadas** (ordem de cópia minimiza rebuilds)
- ✅ **Cache de pip desabilitado** (reduz tamanho)
- ✅ **Cleanup de apt** (remove lixo após instalação)
- ✅ **Healthcheck configurado** (monitoramento automático)
- ✅ **Volumes para persistência** (dados não perdem no restart)

---

## 6. Monitoramento e Logs

### 6.1. Estrutura de Logs

```
logs/
├── application.log      → Logs da aplicação (run.py)
└── scheduler.log        → Logs do scheduler
```

### 6.2. Formato de Log

**Aplicação**:
```
2025-12-09 08:00:00 - src.main - INFO - Databricks Post Processor - Sistema Iniciado
2025-12-09 08:00:05 - src.scraper - INFO - Iniciando scraping de posts
```

**Scheduler**:
```
2025-12-09 08:00:00 - scheduler - INFO - INICIANDO EXECUCAO AGENDADA - 2025-12-09 08:00:00
2025-12-09 08:15:30 - scheduler - INFO - Execucao concluida com SUCESSO
```

### 6.3. Comandos de Monitoramento

```bash
# Logs em tempo real
docker-compose logs -f

# Últimas 100 linhas
docker-compose logs --tail=100

# Logs do scheduler
docker-compose exec afn-linkedin-processor cat /app/logs/scheduler.log

# Logs da aplicação
docker-compose exec afn-linkedin-processor cat /app/logs/application.log
```

---

## 7. Testes Realizados

### 7.1. Testes de Integração

**Não executados neste momento** (ambiente local não disponível)

**Checklist de Testes Recomendados**:

```bash
# 1. Build da imagem
docker-compose build

# 2. Iniciar container
docker-compose up -d

# 3. Verificar logs do scheduler
docker-compose logs scheduler

# 4. Executar manualmente
docker-compose exec afn-linkedin-processor python run.py

# 5. Verificar persistência de dados
ls -la logs/ database/ graphics/

# 6. Testar agendamento (cron a cada minuto)
# Editar .env: SCHEDULE_CRON=* * * * *
docker-compose up -d
docker-compose logs -f

# 7. Verificar healthcheck
docker inspect --format='{{.State.Health.Status}}' afn-linkedin-processor

# 8. Testar restart
docker-compose restart
docker-compose logs -f

# 9. Limpar ambiente
docker-compose down
```

### 7.2. Validações de Segurança

```bash
# Verificar usuário do container
docker-compose exec afn-linkedin-processor whoami
# Esperado: afnuser

# Verificar permissões
docker-compose exec afn-linkedin-processor ls -la /app

# Verificar variáveis de ambiente (sem expor API key)
docker-compose exec afn-linkedin-processor env | grep -v API_KEY
```

---

## 8. Documentação Adicional

### 8.1. Guia de Uso

**Localização**: `docs/GUIA_DOCKER.md`

**Conteúdo**:
- Visão geral da arquitetura
- Pré-requisitos
- Configuração inicial
- Comandos principais
- Monitoramento
- Solução de problemas
- Testes
- Segurança
- Manutenção
- Ambiente de produção

### 8.2. Scripts de Setup

**Linux/Mac**: `setup_docker.sh`
- Verificações automatizadas
- Configuração interativa
- Build da imagem
- Instruções pós-setup

**Windows**: `setup_docker.ps1`
- Equivalente PowerShell
- Compatível com Windows 10/11
- Mesma funcionalidade

---

## 9. Melhorias Futuras

### 9.1. Possíveis Otimizações

1. **Multi-stage Build**
   - Separar build e runtime
   - Reduzir tamanho final da imagem

2. **Healthcheck Avançado**
   - Verificar conectividade com n8n
   - Validar OpenAI API
   - Check de Selenium/Chrome

3. **Monitoramento Externo**
   - Integração com Prometheus
   - Métricas customizadas
   - Alertas via Slack/Email

4. **Backup Automático**
   - Snapshot diário do database
   - Upload para S3/Cloud Storage
   - Rotação de backups

5. **CI/CD**
   - Pipeline GitHub Actions
   - Testes automatizados
   - Deploy automático

### 9.2. Recursos Adicionais

- **Dashboard**: Interface web para monitoramento
- **API REST**: Trigger manual via endpoint
- **Notificações**: Alertas de sucesso/falha
- **Retry Logic**: Tentativas automáticas em caso de falha

---

## 10. Dependências e Requisitos

### 10.1. Requisitos de Sistema

**Mínimos**:
- Docker Engine 20.10+
- Docker Compose 2.0+
- 1GB RAM livre
- 2GB espaço em disco

**Recomendados**:
- Docker Engine 24.0+
- Docker Compose 2.20+
- 2GB RAM livre
- 5GB espaço em disco

### 10.2. Requisitos de Rede

- Acesso à internet (scraping, OpenAI API, n8n webhook)
- Porta 443 (HTTPS) liberada
- DNS funcional

### 10.3. Dependências Python

Todas definidas em `requirements.txt`:
- selenium==4.16.0
- beautifulsoup4==4.12.2
- pandas==2.1.4
- openai>=1.10.0
- requests==2.31.0
- webdriver-manager==4.0.1

---

## 11. Troubleshooting

### 11.1. Problemas Comuns

**1. Selenium Falha ao Iniciar Chrome**

```bash
# Solução: Reconstruir imagem sem cache
docker-compose build --no-cache
docker-compose up -d
```

**2. Agendamento Não Dispara**

```bash
# Verificar timezone
docker-compose exec afn-linkedin-processor date

# Verificar cron configurado
docker-compose exec afn-linkedin-processor printenv SCHEDULE_CRON

# Verificar logs
docker-compose logs -f | grep "INICIANDO EXECUCAO"
```

**3. API Key Inválida**

```bash
# Verificar .env
cat .env | grep OPENAI_API_KEY

# Atualizar e reiniciar
nano .env
docker-compose down
docker-compose up -d
```

**4. Dados Não Persistem**

```bash
# Verificar volumes
docker volume ls

# Verificar bind mounts
docker-compose config | grep volumes -A 10
```

### 11.2. Logs de Debug

```bash
# Modo verbose
docker-compose up

# Logs completos
docker-compose logs --no-truncate

# Entrar no container
docker-compose exec afn-linkedin-processor bash

# Verificar processos
docker-compose exec afn-linkedin-processor ps aux
```

---

## 12. Conclusão

### 12.1. Resultados Alcançados

- ✅ **Containerização completa** da aplicação
- ✅ **Agendamento automático** configurável via cron
- ✅ **Persistência de dados** via volumes
- ✅ **Segurança** com usuário não-root
- ✅ **Monitoramento** via logs estruturados
- ✅ **Documentação completa** e scripts de setup
- ✅ **Portabilidade** entre ambientes

### 12.2. Impacto

**Benefícios Técnicos**:
- Ambiente reproduzível e consistente
- Isolamento de dependências
- Automação sem intervenção manual
- Facilidade de deploy e manutenção

**Benefícios Operacionais**:
- Redução de erros humanos
- Execução confiável e agendada
- Rastreabilidade completa
- Facilidade de troubleshooting

### 12.3. Próximos Passos

1. **Testar** em ambiente real
2. **Validar** agendamento
3. **Monitorar** primeira execução
4. **Ajustar** configurações se necessário
5. **Documentar** lições aprendidas

---

## 13. Referências Técnicas

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Selenium Docker](https://github.com/SeleniumHQ/docker-selenium)
- [Cron Expression Syntax](https://crontab.guru/)
- [Python Subprocess](https://docs.python.org/3/library/subprocess.html)

---

## 14. Histórico de Versões

| Versão | Data | Autor | Descrição |
|--------|------|-------|-----------|
| 1.0.0 | 2025-12-09 | Sistema AFN | Implementação inicial completa |

---

**Assinatura Digital**: Sistema AFN  
**Data de Implementação**: 2025-12-09  
**Status**: Implementado e Documentado  
**Ambiente**: Docker Compose  
**Versão Docker**: 1.0.0  
**Versão Aplicação**: 2.0.0

