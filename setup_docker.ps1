# ================================================================
# Setup Script - Docker Environment (PowerShell)
# ================================================================
# Script auxiliar para configuração inicial do ambiente Docker
# Windows PowerShell version
# ================================================================

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Databricks Post Processor - Setup Docker" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Função de erro
function Write-Error-Exit {
    param($Message)
    Write-Host "[ERRO] $Message" -ForegroundColor Red
    exit 1
}

# Função de sucesso
function Write-Success {
    param($Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

# Função de aviso
function Write-Warning-Custom {
    param($Message)
    Write-Host "[AVISO] $Message" -ForegroundColor Yellow
}

# 1. Verificar Docker
Write-Host "1. Verificando instalacao do Docker..."
try {
    $dockerVersion = docker --version
    Write-Success "Docker encontrado: $dockerVersion"
} catch {
    Write-Error-Exit "Docker nao encontrado. Instale em: https://docs.docker.com/desktop/windows/install/"
}

# 2. Verificar Docker Compose
Write-Host ""
Write-Host "2. Verificando Docker Compose..."
try {
    $composeVersion = docker-compose --version
    Write-Success "Docker Compose encontrado: $composeVersion"
} catch {
    Write-Error-Exit "Docker Compose nao encontrado. Instale Docker Desktop"
}

# 3. Criar arquivo .env se não existir
Write-Host ""
Write-Host "3. Configurando variaveis de ambiente..."
if (-not (Test-Path .env)) {
    if (Test-Path env.example) {
        Copy-Item env.example .env
        Write-Success "Arquivo .env criado a partir de env.example"
        Write-Warning-Custom "IMPORTANTE: Edite o arquivo .env e adicione sua OPENAI_API_KEY"
    } else {
        Write-Error-Exit "Arquivo env.example nao encontrado"
    }
} else {
    Write-Warning-Custom "Arquivo .env ja existe. Pulando..."
}

# 4. Verificar OPENAI_API_KEY
Write-Host ""
Write-Host "4. Verificando configuracao da API Key..."
if (Test-Path .env) {
    $envContent = Get-Content .env -Raw
    if ($envContent -match "sk-your-api-key-here") {
        Write-Warning-Custom "OPENAI_API_KEY ainda nao foi configurada!"
        Write-Host ""
        $response = Read-Host "Deseja configurar agora? (s/n)"
        if ($response -eq "s" -or $response -eq "S") {
            $apiKey = Read-Host "Digite sua OpenAI API Key"
            (Get-Content .env) -replace "sk-your-api-key-here", $apiKey | Set-Content .env
            Write-Success "API Key configurada"
        } else {
            Write-Warning-Custom "Lembre-se de configurar a API Key antes de iniciar: notepad .env"
        }
    } else {
        Write-Success "OPENAI_API_KEY configurada"
    }
}

# 5. Criar diretórios necessários
Write-Host ""
Write-Host "5. Criando estrutura de diretorios..."
$dirs = @("logs", "database", "graphics", "reports", "dados")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
    }
}
Write-Success "Diretorios criados"

# 6. Build da imagem
Write-Host ""
Write-Host "6. Construindo imagem Docker..."
Write-Host "   (Isso pode levar alguns minutos na primeira vez...)"
try {
    docker-compose build
    Write-Success "Imagem construida com sucesso"
} catch {
    Write-Error-Exit "Falha ao construir imagem"
}

# 7. Informações finais
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "Setup concluido com sucesso!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos passos:"
Write-Host ""
Write-Host "1. Verificar configuracao:" -ForegroundColor White
Write-Host "   " -NoNewline; Write-Host "type .env" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Iniciar a aplicacao:" -ForegroundColor White
Write-Host "   " -NoNewline; Write-Host "docker-compose up -d" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Ver logs:" -ForegroundColor White
Write-Host "   " -NoNewline; Write-Host "docker-compose logs -f" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Executar manualmente (teste):" -ForegroundColor White
Write-Host "   " -NoNewline; Write-Host "docker-compose exec afn-linkedin-processor python run.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "5. Parar a aplicacao:" -ForegroundColor White
Write-Host "   " -NoNewline; Write-Host "docker-compose down" -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Para mais informacoes, consulte: docs\GUIA_DOCKER.md" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

