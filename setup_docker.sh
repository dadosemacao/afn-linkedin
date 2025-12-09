#!/bin/bash
# ================================================================
# Setup Script - Docker Environment
# ================================================================
# Script auxiliar para configuração inicial do ambiente Docker
# ================================================================

set -e

echo "============================================================"
echo "Databricks Post Processor - Setup Docker"
echo "============================================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função de erro
error_exit() {
    echo -e "${RED}[ERRO]${NC} $1" >&2
    exit 1
}

# Função de sucesso
success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

# Função de aviso
warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

# 1. Verificar Docker
echo "1. Verificando instalacao do Docker..."
if ! command -v docker &> /dev/null; then
    error_exit "Docker nao encontrado. Instale em: https://docs.docker.com/get-docker/"
fi
success "Docker encontrado: $(docker --version)"

# 2. Verificar Docker Compose
echo ""
echo "2. Verificando Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    error_exit "Docker Compose nao encontrado. Instale em: https://docs.docker.com/compose/install/"
fi
success "Docker Compose encontrado: $(docker-compose --version)"

# 3. Criar arquivo .env se não existir
echo ""
echo "3. Configurando variaveis de ambiente..."
if [ ! -f .env ]; then
    if [ -f env.example ]; then
        cp env.example .env
        success "Arquivo .env criado a partir de env.example"
        warning "IMPORTANTE: Edite o arquivo .env e adicione sua OPENAI_API_KEY"
    else
        error_exit "Arquivo env.example nao encontrado"
    fi
else
    warning "Arquivo .env ja existe. Pulando..."
fi

# 4. Verificar OPENAI_API_KEY
echo ""
echo "4. Verificando configuracao da API Key..."
if [ -f .env ]; then
    if grep -q "sk-your-api-key-here" .env; then
        warning "OPENAI_API_KEY ainda nao foi configurada!"
        echo ""
        read -p "Deseja configurar agora? (s/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            read -p "Digite sua OpenAI API Key: " api_key
            sed -i "s/sk-your-api-key-here/$api_key/" .env
            success "API Key configurada"
        else
            warning "Lembre-se de configurar a API Key antes de iniciar: nano .env"
        fi
    else
        success "OPENAI_API_KEY configurada"
    fi
fi

# 5. Criar diretórios necessários
echo ""
echo "5. Criando estrutura de diretorios..."
mkdir -p logs database graphics reports dados
success "Diretorios criados"

# 6. Build da imagem
echo ""
echo "6. Construindo imagem Docker..."
echo "   (Isso pode levar alguns minutos na primeira vez...)"
if docker-compose build; then
    success "Imagem construida com sucesso"
else
    error_exit "Falha ao construir imagem"
fi

# 7. Informações finais
echo ""
echo "============================================================"
echo -e "${GREEN}Setup concluido com sucesso!${NC}"
echo "============================================================"
echo ""
echo "Proximos passos:"
echo ""
echo "1. Verificar configuracao:"
echo "   ${YELLOW}cat .env${NC}"
echo ""
echo "2. Iniciar a aplicacao:"
echo "   ${YELLOW}docker-compose up -d${NC}"
echo ""
echo "3. Ver logs:"
echo "   ${YELLOW}docker-compose logs -f${NC}"
echo ""
echo "4. Executar manualmente (teste):"
echo "   ${YELLOW}docker-compose exec afn-linkedin-processor python run.py${NC}"
echo ""
echo "5. Parar a aplicacao:"
echo "   ${YELLOW}docker-compose down${NC}"
echo ""
echo "============================================================"
echo "Para mais informacoes, consulte: docs/GUIA_DOCKER.md"
echo "============================================================"

