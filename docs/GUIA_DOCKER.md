# Guia de Uso - Docker Compose

**Autor**: Sistema AFN  
**Data**: 2025-12-09  
**Versão**: 1.0.0

---

## 1. Visão Geral

Este documento descreve como utilizar a aplicação **Databricks Post Processor** via Docker Compose, incluindo agendamento automático para execução toda segunda-feira às 08:00.

---

## 2. Arquitetura Docker

### 2.1. Componentes

- **Dockerfile**: Define a imagem da aplicação com todas as dependências
- **docker-compose.yml**: Orquestra o container e configurações
- **scheduler.py**: Gerencia o agendamento automático via cron
- **Volumes persistentes**: Para logs, database, gráficos e relatórios

### 2.2. Fluxo de Execução

```
Container Inicia
    ↓
Scheduler Ativo
    ↓
Aguarda Horário Agendado
    ↓
Segunda-feira 08:00
    ↓
Executa Pipeline Completo
    ↓
Registra Logs e Resultados
    ↓
Retorna ao Estado de Espera
```

---

## 3. Pré-requisitos

### 3.1. Instalações Necessárias

- Docker Engine 20.10+
- Docker Compose 2.0+

### 3.2. Verificação

```bash
docker --version
docker-compose --version
```

---

## 4. Configuração Inicial

### 4.1. Variáveis de Ambiente

1. Copie o arquivo de exemplo:

```bash
cp env.example .env
```

2. Edite o arquivo `.env` e configure:

```env
# OBRIGATÓRIO
OPENAI_API_KEY=sk-sua-chave-aqui

# OPCIONAL - Agendamento
SCHEDULE_ENABLED=true
SCHEDULE_CRON=0 8 * * 1
TZ=America/Sao_Paulo
```

### 4.2. Configuração do Cron

O formato do cron é: `minuto hora dia mês dia-da-semana`

**Exemplos de Agendamento:**

| Expressão Cron | Descrição |
|----------------|-----------|
| `0 8 * * 1` | Segunda-feira às 08:00 (padrão) |
| `0 8 * * 1-5` | Segunda a Sexta às 08:00 |
| `0 9,15 * * *` | Todos os dias às 09:00 e 15:00 |
| `*/30 * * * *` | A cada 30 minutos |
| `0 0 * * 0` | Domingos à meia-noite |

**Dias da Semana:**
- 0 ou 7 = Domingo
- 1 = Segunda-feira
- 2 = Terça-feira
- 3 = Quarta-feira
- 4 = Quinta-feira
- 5 = Sexta-feira
- 6 = Sábado

---

## 5. Comandos Principais

### 5.1. Iniciar a Aplicação

```bash
# Primeira vez (com build)
docker-compose up -d --build

# Execuções subsequentes
docker-compose up -d
```

### 5.2. Verificar Status

```bash
# Ver status dos containers
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f

# Ver logs do scheduler
docker-compose logs -f afn-linkedin-processor
```

### 5.3. Parar a Aplicação

```bash
# Parar containers
docker-compose stop

# Parar e remover containers
docker-compose down

# Parar e remover volumes (CUIDADO: apaga dados)
docker-compose down -v
```

### 5.4. Executar Manualmente

```bash
# Executar fora do agendamento
docker-compose exec afn-linkedin-processor python run.py

# Entrar no container
docker-compose exec afn-linkedin-processor bash
```

### 5.5. Reconstruir Imagem

```bash
# Após mudanças no código
docker-compose up -d --build --force-recreate
```

---

## 6. Monitoramento

### 6.1. Verificar Logs do Scheduler

```bash
# Logs do scheduler
docker-compose exec afn-linkedin-processor cat /app/logs/scheduler.log

# Logs da aplicação
docker-compose exec afn-linkedin-processor cat /app/logs/application.log
```

### 6.2. Verificar Última Execução

```bash
# Ver últimas linhas do log
docker-compose logs --tail=100 afn-linkedin-processor
```

### 6.3. Healthcheck

```bash
# Status de saúde do container
docker inspect --format='{{.State.Health.Status}}' afn-linkedin-processor
```

---

## 7. Estrutura de Dados Persistentes

### 7.1. Volumes Montados

Os seguintes diretórios são persistidos no host:

```
./logs/              → Logs da aplicação e scheduler
./database/          → Banco de dados SQLite
./graphics/          → Gráficos gerados
./reports/           → Relatórios
./dados/             → Dados brutos
./databricks_platform_posts.csv → CSV principal
```

### 7.2. Backup

```bash
# Backup completo
tar -czf backup_$(date +%Y%m%d).tar.gz logs/ database/ graphics/ reports/ databricks_platform_posts.csv
```

---

## 8. Solução de Problemas

### 8.1. Container Não Inicia

```bash
# Ver logs de erro
docker-compose logs

# Verificar configuração
docker-compose config
```

### 8.2. Scraper Falha

**Problema**: Selenium não consegue iniciar Chrome

**Solução**:
```bash
# Reconstruir com --no-cache
docker-compose build --no-cache
docker-compose up -d
```

### 8.3. OpenAI API Key Inválida

**Problema**: Erro de autenticação OpenAI

**Solução**:
1. Verificar `.env`:
```bash
cat .env | grep OPENAI_API_KEY
```

2. Atualizar e reiniciar:
```bash
docker-compose down
docker-compose up -d
```

### 8.4. Agendamento Não Executa

**Problema**: Scheduler não dispara no horário

**Solução**:
1. Verificar timezone:
```bash
docker-compose exec afn-linkedin-processor date
```

2. Verificar logs do scheduler:
```bash
docker-compose logs afn-linkedin-processor | grep "INICIANDO EXECUCAO"
```

3. Validar expressão cron:
```bash
echo $SCHEDULE_CRON
```

---

## 9. Testes

### 9.1. Teste Rápido (Sem Agendamento)

```bash
# Desabilitar scheduler e executar
docker-compose run --rm \
  -e SCHEDULE_ENABLED=false \
  afn-linkedin-processor \
  python run.py
```

### 9.2. Teste de Agendamento

```bash
# Configurar para executar a cada minuto (teste)
# Editar .env:
SCHEDULE_CRON=* * * * *

# Reiniciar
docker-compose up -d

# Monitorar execuções
docker-compose logs -f
```

### 9.3. Teste de Scraping

```bash
docker-compose exec afn-linkedin-processor python -c "
from src.scraper import DatabricksScraper
scraper = DatabricksScraper()
posts = scraper.scrape_posts()
print(f'Posts encontrados: {len(posts)}')
scraper.cleanup()
"
```

---

## 10. Segurança

### 10.1. Boas Práticas

- ✅ Nunca commitar arquivo `.env` no git
- ✅ Usar usuário não-root no container
- ✅ Manter imagem atualizada
- ✅ Limitar recursos do container
- ✅ Rotacionar logs regularmente

### 10.2. Limitação de Recursos

Adicionar ao `docker-compose.yml`:

```yaml
services:
  afn-linkedin-processor:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          memory: 512M
```

---

## 11. Manutenção

### 11.1. Limpeza de Logs

```bash
# Limpar logs antigos (manter últimos 30 dias)
find ./logs -name "*.log" -mtime +30 -delete
```

### 11.2. Atualização de Dependências

```bash
# Atualizar requirements.txt
# Reconstruir imagem
docker-compose build --no-cache
docker-compose up -d
```

### 11.3. Limpeza de Imagens Antigas

```bash
# Remover imagens não utilizadas
docker image prune -a

# Remover volumes órfãos
docker volume prune
```

---

## 12. Ambiente de Produção

### 12.1. Recomendações

1. **Monitoramento**: Integrar com Prometheus/Grafana
2. **Alertas**: Configurar notificações de falha
3. **Backup**: Automatizar backup diário
4. **Logs**: Enviar para sistema centralizado (ELK, Splunk)
5. **Restart Policy**: Usar `restart: always` em produção

### 12.2. Docker Compose para Produção

```yaml
services:
  afn-linkedin-processor:
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"
    deploy:
      resources:
        limits:
          cpus: '1.5'
          memory: 3G
```

---

## 13. Referências

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Cron Expression Generator](https://crontab.guru/)
- [Selenium Docker Guide](https://github.com/SeleniumHQ/docker-selenium)

---

## 14. Suporte

Para dúvidas ou problemas:

1. Verificar logs: `docker-compose logs`
2. Consultar documentação em `/docs`
3. Revisar issues conhecidos
4. Abrir ticket com equipe de desenvolvimento

---

**Última Atualização**: 2025-12-09  
**Versão do Docker**: 1.0.0  
**Versão da Aplicação**: 2.0.0

