# Docker Quick Start Guide

**Execução Rápida** | **5 Minutos para Começar**

---

## Início Rápido - Linux/Mac

```bash
# 1. Setup automático
chmod +x setup_docker.sh
./setup_docker.sh

# 2. Configurar API Key
nano .env
# Adicione: OPENAI_API_KEY=sk-sua-chave-aqui

# 3. Iniciar
docker-compose up -d

# 4. Monitorar
docker-compose logs -f
```

---

## Início Rápido - Windows (PowerShell)

```powershell
# 1. Setup automático
.\setup_docker.ps1

# 2. Configurar API Key
notepad .env
# Adicione: OPENAI_API_KEY=sk-sua-chave-aqui

# 3. Iniciar
docker-compose up -d

# 4. Monitorar
docker-compose logs -f
```

---

## Comandos Essenciais

| Ação | Comando |
|------|---------|
| Iniciar | `docker-compose up -d` |
| Parar | `docker-compose down` |
| Ver logs | `docker-compose logs -f` |
| Status | `docker-compose ps` |
| Executar agora | `docker-compose exec afn-linkedin-processor python run.py` |
| Reiniciar | `docker-compose restart` |

---

## Agendamento Padrão

- **Quando**: Toda segunda-feira às 08:00
- **Timezone**: America/Sao_Paulo
- **Customização**: Edite `SCHEDULE_CRON` no `.env`

---

## Estrutura de Dados

```
📁 Projeto
├── 📄 docker-compose.yml    → Configuração principal
├── 📄 .env                  → Variáveis de ambiente
├── 📁 logs/                 → Logs da aplicação
├── 📁 database/             → Banco de dados
├── 📁 graphics/             → Gráficos gerados
└── 📁 reports/              → Relatórios
```

---

## Personalizar Agendamento

Edite `.env`:

```bash
# Segunda-feira 08:00 (padrão)
SCHEDULE_CRON=0 8 * * 1

# Segunda a Sexta 09:00
SCHEDULE_CRON=0 9 * * 1-5

# Todos os dias 10:00
SCHEDULE_CRON=0 10 * * *

# A cada 6 horas
SCHEDULE_CRON=0 */6 * * *
```

---

## Solução de Problemas

### Container não inicia

```bash
docker-compose logs
docker-compose config
```

### API Key inválida

```bash
cat .env | grep OPENAI_API_KEY
# Verifique se está correto
```

### Scraping falha

```bash
docker-compose build --no-cache
docker-compose up -d
```

---

## Documentação Completa

- **Guia Detalhado**: `docs/GUIA_DOCKER.md`
- **Implementação Técnica**: `docs/IMPLEMENTACAO_DOCKER_2025-12-09.md`
- **Arquitetura**: `docs/ARQUITETURA.md`

---

## Suporte

1. Verificar logs: `docker-compose logs -f`
2. Consultar documentação em `/docs`
3. Revisar issues conhecidos
4. Contatar equipe de desenvolvimento

---

**Última Atualização**: 2025-12-09  
**Versão**: 1.0.0

