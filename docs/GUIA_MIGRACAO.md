# Guia de Migração - Versão 1.0 para 2.0

**Data**: 09 de Dezembro de 2025  
**Versão**: 2.0.0

---

## Visão Geral

Este guia auxilia na migração do código legado (`DataBricks.py`) para a nova arquitetura modular (v2.0).

---

## Backup

O arquivo original foi preservado como `src/DataBricks.py.backup` e pode ser restaurado se necessário.

---

## Mudanças de Estrutura

### Antes (v1.0)
```
src/
└── DataBricks.py  (479 linhas - tudo em um arquivo)
```

### Depois (v2.0)
```
src/
├── __init__.py
├── main.py
├── config.py
├── logger.py
├── scraper.py
├── ai_processor.py
├── n8n_integration.py
├── csv_handler.py
├── database.py
└── utils.py
```

---

## Mudanças de Configuração

### API Keys

**Antes**: Carregada diretamente
```python
load_dotenv()
client = openai.Client()
```

**Depois**: Centralizada em config
```python
# No arquivo .env
OPENAI_API_KEY=sua_chave_aqui

# No código
from src.config import config
# config.openai_api_key já está disponível
```

### URLs e Paths

**Antes**: Hardcoded no código
```python
BASE = "https://www.databricks.com"
CATEGORY_URL = "https://www.databricks.com/blog/category/platform"
OUTPUT_CSV = "databricks_platform_posts.csv"
```

**Depois**: Externalizadas em config.ini
```ini
[scraper]
base_url = https://www.databricks.com
category_url = https://www.databricks.com/blog/category/platform

[files]
output_posts_csv = databricks_platform_posts.csv
```

---

## Mudanças de Código

### 1. Scraping

**Antes**:
```python
driver = webdriver.Chrome(service=service, options=options)
driver.get(CATEGORY_URL)
# ... código inline ...
driver.quit()
```

**Depois**:
```python
from src.scraper import DatabricksScraper

scraper = DatabricksScraper()
posts = scraper.scrape_posts()
scraper.cleanup()
```

### 2. Processamento com IA

**Antes**:
```python
def gerar_resumo_do_link(link):
    mensagens = [...]
    resposta = client.chat.completions.create(...)
    return resposta.choices[0].message.content

# Loop manual pelos posts
for index, row in df.iterrows():
    resumo = gerar_resumo_do_link(link)
    # ... salvar ...
```

**Depois**:
```python
from src.ai_processor import AIPostProcessor

processor = AIPostProcessor()
processed_posts = processor.process_posts(posts)
```

### 3. Integração n8n

**Antes**:
```python
def enviar_para_n8n(posts):
    response = requests.post(WEBHOOK_URL, json=posts)
    print("Status:", response.status_code)

posts = carregar_posts(csv_path)
enviar_para_n8n(posts)
```

**Depois**:
```python
from src.n8n_integration import N8NIntegration

integration = N8NIntegration()
success = integration.send_posts(posts)
```

### 4. Logging

**Antes**:
```python
print("📄 Lendo CSV de posts...")
print(f"🔎 {len(df)} posts encontrados.\n")
```

**Depois**:
```python
from src.logger import get_logger

logger = get_logger(__name__)
logger.info("Lendo CSV de posts")
logger.info(f"Encontrados {len(df)} posts")
```

### 5. CSV Operations

**Antes**:
```python
df = pd.read_csv(INPUT_CSV)
# ... manipulações ...
df.to_csv(OUTPUT_CSV, index=False)
```

**Depois**:
```python
from src.csv_handler import CSVHandler

csv_handler = CSVHandler()
posts = csv_handler.load_posts()
# ... manipulações ...
csv_handler.save_posts(posts)
```

---

## Execução

### Antes (v1.0)

```bash
python src/DataBricks.py
```

O script executava tudo sequencialmente:
1. Scraping
2. Processamento
3. Integração n8n

### Depois (v2.0)

```bash
# Pipeline completo
python src/main.py

# Ou import programático
from src.main import Application

app = Application()
app.run_full_pipeline()

# Ou fases individuais
app.run_scraping()
app.run_ai_processing()
app.run_n8n_integration()
```

---

## Compatibilidade

### Dados

✅ **Compatível**: Todos os dados existentes continuam funcionando

- CSV: Mesma estrutura, colunas adicionais criadas automaticamente
- JSON: Formato preservado
- Database: Novo (não afeta dados existentes)

### Configuração

⚠️ **Requer Setup**: Novos arquivos de configuração

1. Criar `config.ini` (fornecido)
2. Criar `.env` com `OPENAI_API_KEY`
3. Ajustar configurações conforme necessário

### Comportamento

✅ **Preservado**: Funcionalidade mantida

- Scraping: Mesmos resultados
- Processamento: Mesma lógica de resumos
- Integração: Mesmo formato de envio

### Melhorias Adicionais

🎉 **Novos Recursos**:

- Logs estruturados em arquivo
- Banco de dados para tracking
- Estatísticas detalhadas
- Validações robustas
- Tratamento de erros melhorado

---

## Checklist de Migração

### Preparação

- [ ] Fazer backup do código atual
- [ ] Verificar Python 3.9+ instalado
- [ ] Ter Chrome instalado

### Instalação

- [ ] Criar/ativar ambiente virtual
- [ ] Instalar dependências: `pip install -r requirements.txt`
- [ ] Criar arquivo `.env` com `OPENAI_API_KEY`
- [ ] Verificar `config.ini` presente

### Validação

- [ ] Testar execução: `python src/main.py`
- [ ] Verificar logs em `logs/application.log`
- [ ] Confirmar CSV gerado corretamente
- [ ] Validar resumos no JSON
- [ ] Testar envio para n8n (se aplicável)

### Limpeza

- [ ] Remover código antigo (opcional)
- [ ] Documentar mudanças específicas do projeto
- [ ] Atualizar documentação interna

---

## Solução de Problemas

### Erro: "OPENAI_API_KEY não configurada"

**Solução**: Criar arquivo `.env` com a chave

```env
OPENAI_API_KEY=sk-...
```

### Erro: "Arquivo config.ini não encontrado"

**Solução**: Copiar `config.ini` para raiz do projeto

### Erro: "ModuleNotFoundError: No module named 'src'"

**Solução**: Executar do diretório raiz do projeto

```bash
# Certo
cd d:\Developement\afirmanet\IA-AFN\Linkedin
python src/main.py

# Errado
cd src
python main.py
```

### Posts não sendo processados

**Solução**: Verificar se já foram processados

```python
from src.database import DatabaseManager

db = DatabaseManager()
stats = db.get_statistics()
print(stats)  # Ver quantos já foram processados
```

Para reprocessar, deletar banco: `database/resumos_processados.db`

### Logs não aparecem

**Solução**: Verificar nível de log em `config.ini`

```ini
[logging]
log_level = DEBUG  # Para mais detalhes
```

---

## Rollback

Se necessário reverter para versão anterior:

```bash
# Restaurar arquivo original
Move-Item -Path "src\DataBricks.py.backup" -Destination "src\DataBricks.py" -Force

# Executar versão antiga
python src/DataBricks.py
```

**Nota**: A versão antiga não usa os novos arquivos de configuração.

---

## Melhorias Futuras Sugeridas

1. **Testes Automatizados**
   - Implementar suite de testes com pytest
   - Coverage mínimo de 80%

2. **CI/CD**
   - Pipeline de integração contínua
   - Deploy automatizado

3. **Monitoramento**
   - Dashboard de métricas
   - Alertas automáticos

4. **Performance**
   - Processamento paralelo
   - Cache de resultados

---

## Suporte

Para questões sobre migração:

1. Consulte `docs/REFATORACAO_2025-12-09.md`
2. Revise `docs/ARQUITETURA.md`
3. Leia código fonte (bem documentado)
4. Verifique logs em `logs/application.log`

---

## Conclusão

A migração para v2.0 traz:

- ✅ Código mais limpo e organizado
- ✅ Melhor manutenibilidade
- ✅ Logs profissionais
- ✅ Configurações flexíveis
- ✅ Tratamento robusto de erros
- ✅ Documentação completa

**Tempo estimado de migração**: 15-30 minutos

**Risco**: Baixo (funcionalidade preservada + backup disponível)

**Benefício**: Alto (código profissional e escalável)

---

*Boa migração!*

