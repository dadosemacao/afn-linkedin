# Setup e Inicialização do Projeto

**Guia rápido de configuração inicial**

---

## 1. Pré-requisitos

Certifique-se de ter instalado:

- [ ] Python 3.9 ou superior
- [ ] Google Chrome (para Selenium)
- [ ] Git (para versionamento)
- [ ] Editor de código (VS Code, PyCharm, etc)

Verificar versões:
```bash
python --version    # Deve ser 3.9+
git --version       # Qualquer versão recente
```

---

## 2. Ambiente Virtual

### Criar ambiente virtual

```bash
# Navegar para o diretório do projeto
cd d:\Developement\afirmanet\IA-AFN\Linkedin

# Criar ambiente virtual
python -m venv venv
```

### Ativar ambiente virtual

**Windows (PowerShell)**:
```powershell
venv\Scripts\Activate.ps1
```

**Windows (CMD)**:
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac**:
```bash
source venv/bin/activate
```

### Verificar ativação

Você deve ver `(venv)` no início da linha do terminal:
```
(venv) PS D:\Developement\afirmanet\IA-AFN\Linkedin>
```

---

## 3. Instalar Dependências

```bash
# Com ambiente virtual ativado
pip install -r requirements.txt
```

Aguarde a instalação de todos os pacotes:
- selenium
- beautifulsoup4
- pandas
- requests
- openai
- python-dotenv
- webdriver-manager

---

## 4. Configurar Variáveis de Ambiente

### Criar arquivo .env

Crie um arquivo `.env` na raiz do projeto com:

```env
# OpenAI API Key
OPENAI_API_KEY=sk-proj-seu_token_aqui

# Ambiente
ENVIRONMENT=production
```

**IMPORTANTE**: 
- Substitua `sk-proj-seu_token_aqui` pela sua chave real da OpenAI
- Nunca compartilhe este arquivo
- O `.gitignore` já está configurado para ignorá-lo

### Obter API Key OpenAI

1. Acesse: https://platform.openai.com/api-keys
2. Faça login ou crie uma conta
3. Clique em "Create new secret key"
4. Copie a chave (você não poderá vê-la novamente)
5. Cole no arquivo `.env`

---

## 5. Verificar Configurações

### Revisar config.ini

O arquivo `config.ini` já está configurado, mas você pode ajustar:

```ini
[scraper]
base_url = https://www.databricks.com
category_url = https://www.databricks.com/blog/category/platform
target_post_type = product

[n8n]
webhook_url_production = sua_url_webhook_aqui
use_production = true
```

Ajuste o `webhook_url_production` se você tiver um webhook n8n personalizado.

---

## 6. Inicializar Git (Versionamento)

### Inicializar repositório

```bash
# Inicializar Git
git init

# Configurar usuário (se necessário)
git config user.name "Seu Nome"
git config user.email "seu.email@exemplo.com"

# Adicionar todos os arquivos
git add .

# Verificar o que será commitado
git status
```

### Primeiro Commit

```bash
git commit -m "feat: Refatoracao completa v2.0.0 - Arquitetura profissional modular

- Refatorado codigo monolitico para arquitetura modular
- Implementado 9 modulos especializados com POO
- Removido todos os emojis dos logs (requisito do projeto)
- Adicionado logging profissional com rotacao
- Externalizadas configuracoes (config.ini)
- Implementado SOLID e design patterns
- Documentacao tecnica completa
- Type hints 100% e docstrings completas

BREAKING CHANGE: Nova estrutura de codigo e arquivos de configuracao
Ver docs/GUIA_MIGRACAO.md para detalhes de migracao"
```

### Criar Tag de Versão

```bash
git tag -a v2.0.0 -m "Release 2.0.0 - Refatoracao completa"
```

### Conectar a Repositório Remoto (Opcional)

```bash
# Adicionar repositório remoto (GitHub, GitLab, etc)
git remote add origin https://github.com/seu-usuario/seu-repo.git

# Enviar para remoto
git push -u origin main
git push --tags
```

---

## 7. Estrutura de Diretórios

Os seguintes diretórios serão criados automaticamente na primeira execução:

```
Linkedin/
├── logs/          # Logs da aplicação (criado automaticamente)
├── database/      # Banco SQLite (criado automaticamente)
├── dados/         # Datasets (criado automaticamente)
├── reports/       # Relatórios (criado automaticamente)
└── graphics/      # Gráficos (criado automaticamente)
```

Você pode criá-los manualmente se preferir:

```bash
mkdir logs database dados reports graphics
```

---

## 8. Testar Instalação

### Teste rápido

```python
# Executar Python interativo
python

# Testar imports
>>> from src.config import config
>>> from src.logger import get_logger
>>> print(config.base_url)
>>> print("Configuracao OK!")
```

Pressione `Ctrl+D` (Linux/Mac) ou `Ctrl+Z` + Enter (Windows) para sair.

### Teste de componentes

```bash
# Teste de configuração
python -c "from src.config import config; print('Config OK')"

# Teste de logger
python -c "from src.logger import get_logger; logger = get_logger(__name__); logger.info('Logger OK')"
```

Se não houver erros, está tudo certo!

---

## 9. Primeira Execução

### Execução completa

```bash
python src/main.py
```

Isso executará:
1. Scraping de posts do Databricks
2. Processamento com IA (geração de resumos)
3. Integração com n8n (envio dos dados)

### Execução parcial

Se quiser executar apenas uma fase, edite `src/main.py`:

```python
if __name__ == "__main__":
    app = Application()
    
    # Escolha uma das opções:
    
    # Apenas scraping
    app.run_scraping()
    
    # Apenas processamento IA
    # app.run_ai_processing()
    
    # Apenas integração n8n
    # app.run_n8n_integration()
    
    # Pipeline completo (padrão)
    # app.run_full_pipeline()
    
    app.show_statistics()
```

---

## 10. Verificar Resultados

### Logs

```bash
# Ver últimas linhas do log
tail -n 50 logs/application.log   # Linux/Mac
Get-Content logs/application.log -Tail 50  # PowerShell
```

### Arquivos gerados

- `databricks_platform_posts.csv` - Posts extraídos
- `resumos_emma.json` - Resumos gerados
- `database/resumos_processados.db` - Banco de dados

### Estatísticas

As estatísticas são exibidas ao final da execução:

```
======================================================================
ESTATISTICAS DO SISTEMA
======================================================================
Total de posts: 15
Posts com resumo: 12
Posts sem resumo: 3

Distribuicao por tipo:
  - Product: 15

Total processados (banco): 12
Processados hoje: 5
Resumos armazenados: 12
======================================================================
```

---

## 11. Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'src'"

**Solução**: Execute do diretório raiz do projeto

```bash
# Certo
cd d:\Developement\afirmanet\IA-AFN\Linkedin
python src/main.py

# Errado
cd src
python main.py
```

### Erro: "OPENAI_API_KEY não configurada"

**Solução**: Verifique o arquivo `.env`

```bash
# Verificar se arquivo existe
dir .env     # Windows
ls -la .env  # Linux/Mac

# Conteúdo deve ter:
OPENAI_API_KEY=sk-proj-...
```

### Erro: "Arquivo config.ini não encontrado"

**Solução**: Verifique se `config.ini` está na raiz

```bash
# Deve estar em:
d:\Developement\afirmanet\IA-AFN\Linkedin\config.ini
```

### Chrome Driver não encontrado

**Solução**: O webdriver-manager baixa automaticamente

Se persistir:
```bash
pip install --upgrade webdriver-manager
```

### Erro de permissão nos logs

**Solução**: Verifique permissões da pasta logs

```bash
# Windows (PowerShell - como Admin)
icacls logs /grant Users:F

# Linux/Mac
chmod -R 755 logs
```

---

## 12. Manutenção

### Atualizar dependências

```bash
pip install --upgrade -r requirements.txt
```

### Limpar logs antigos

```bash
# Logs são rotacionados automaticamente
# Mas você pode limpar manualmente:
rm logs/*.log.1 logs/*.log.2  # etc
```

### Resetar banco de dados

```bash
# Para reprocessar posts
rm database/resumos_processados.db
```

### Backup de dados

```bash
# Criar backup
mkdir backup
cp databricks_platform_posts.csv backup/
cp resumos_emma.json backup/
cp -r database backup/
```

---

## 13. Próximos Passos

Após setup completo:

1. ✅ Ler `README.md` - Documentação completa
2. ✅ Explorar `docs/ARQUITETURA.md` - Entender a arquitetura
3. ✅ Revisar `docs/REFATORACAO_2025-12-09.md` - Detalhes técnicos
4. ✅ Configurar IDE para desenvolvimento
5. ✅ Implementar testes unitários (próxima versão)

---

## Checklist de Setup

- [ ] Python 3.9+ instalado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (`requirements.txt`)
- [ ] Arquivo `.env` criado com `OPENAI_API_KEY`
- [ ] Arquivo `config.ini` revisado
- [ ] Git inicializado
- [ ] Primeiro commit realizado
- [ ] Tag v2.0.0 criada
- [ ] Teste de execução bem-sucedido
- [ ] Logs verificados
- [ ] Resultados validados

---

## Suporte

### Documentação
- `README.md` - Guia de uso
- `docs/` - Documentação técnica completa

### Logs
- `logs/application.log` - Log principal
- Formato estruturado para análise

### Código
- Bem documentado com docstrings
- Type hints em todas as funções

---

**Boa sorte!** 🚀

*Setup preparado para garantir inicialização suave e profissional.*

