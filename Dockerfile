# ================================================================
# Databricks Post Processor - Docker Image
# ================================================================
# Multi-stage build para otimização de tamanho
# ================================================================

FROM python:3.11-slim

# Metadados da imagem
LABEL maintainer="Sistema AFN"
LABEL description="Databricks Post Processor - Sistema de Scraping e Processamento"
LABEL version="2.0.0"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias para Selenium e Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    chromium \
    chromium-driver \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivo de dependências
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Cria estrutura de diretórios
RUN mkdir -p \
    /app/src \
    /app/dados \
    /app/database \
    /app/docs \
    /app/graphics \
    /app/logs \
    /app/reports

# Copia código da aplicação
COPY src/ /app/src/
COPY run.py /app/
COPY config.ini /app/

# Copia script do scheduler
COPY scheduler.py /app/

# Configuração de permissões
RUN chmod +x /app/run.py && \
    chmod +x /app/scheduler.py && \
    chmod -R 777 /app/logs /app/database /app/graphics /app/reports

# Cria usuário não-root para segurança
RUN useradd -m -u 1000 afnuser && \
    chown -R afnuser:afnuser /app

# Muda para usuário não-root
USER afnuser

# Healthcheck
HEALTHCHECK --interval=1h --timeout=30s --start-period=10s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Comando padrão: inicia o scheduler
CMD ["python", "-u", "scheduler.py"]

