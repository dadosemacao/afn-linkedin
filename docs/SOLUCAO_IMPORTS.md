# Solução de Problema: Imports do Módulo src

**Data**: 09 de Dezembro de 2025  
**Problema**: `ModuleNotFoundError: No module named 'src'`

---

## 🔍 Problema Identificado

### Erro Reportado

```bash
PS D:\Developement\afirmanet\IA-AFN\Linkedin> python .\src\main.py

Traceback (most recent call last):
  File "D:\Developement\afirmanet\IA-AFN\Linkedin\src\main.py", line 15, in <module>
    from src.config import config
ModuleNotFoundError: No module named 'src'
```

### Causa Raiz

Quando você executa `python .\src\main.py` diretamente, o Python:

1. Define o diretório atual (`src/`) como base
2. Tenta importar `from src.config` 
3. Não encontra o módulo `src` porque está **dentro** dele

É um problema clássico de imports absolutos vs relativos.

---

## ✅ Solução Implementada

### Opção 1: Script de Entrada (Recomendado) ⭐

Criado arquivo `run.py` na raiz do projeto:

```python
"""
Script de Entrada Principal
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Importa e executa
from src.main import main

if __name__ == "__main__":
    sys.exit(main())
```

**Como usar**:
```bash
python run.py
```

**Vantagens**:
- ✅ Funciona sempre
- ✅ Não precisa configurar nada
- ✅ Portável entre sistemas
- ✅ Padrão profissional

---

### Opção 2: Executar Como Módulo Python

```bash
python -m src.main
```

**Como funciona**:
- Flag `-m` executa como módulo
- Python adiciona diretório atual ao path automaticamente
- Imports absolutos funcionam

**Vantagens**:
- ✅ Sem arquivos extras
- ✅ Padrão Python

**Desvantagens**:
- ⚠️ Precisa lembrar do `-m`

---

### Opção 3: Configurar PYTHONPATH (Avançado)

**Windows PowerShell**:
```powershell
$env:PYTHONPATH = "D:\Developement\afirmanet\IA-AFN\Linkedin"
python .\src\main.py
```

**Windows CMD**:
```cmd
set PYTHONPATH=D:\Developement\afirmanet\IA-AFN\Linkedin
python .\src\main.py
```

**Linux/Mac**:
```bash
export PYTHONPATH=/caminho/para/Linkedin
python ./src/main.py
```

**Vantagens**:
- ✅ Funciona para qualquer script

**Desvantagens**:
- ⚠️ Precisa configurar toda vez
- ⚠️ Específico do sistema

---

### Opção 4: Imports Relativos (Não Recomendado)

Modificar `src/main.py` para usar imports relativos:

```python
# De:
from src.config import config
from src.logger import get_logger

# Para:
from .config import config
from .logger import get_logger
```

**Problema**: Então não pode mais executar `main.py` diretamente!

**Não recomendado** para este projeto.

---

## 📊 Comparação das Opções

| Opção | Facilidade | Portabilidade | Profissional |
|-------|------------|---------------|--------------|
| `run.py` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| `python -m` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| PYTHONPATH | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Imports relativos | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |

---

## 🎯 Recomendação Final

### Use: `python run.py` ⭐

**Por quê?**:

1. ✅ **Mais simples**: Um comando curto e claro
2. ✅ **Sempre funciona**: Não depende de configuração
3. ✅ **Profissional**: Padrão em projetos Python
4. ✅ **Portável**: Funciona em Windows, Linux, Mac
5. ✅ **Documentado**: Já está no README.md

---

## 📝 Exemplos de Uso

### Executar Aplicação

```bash
# Recomendado
python run.py

# Alternativa
python -m src.main
```

### Executar Testes

```bash
python test_application.py
```

### Executar Exemplos

```bash
python example_usage.py
```

### Inspecionar Banco

```bash
python inspect_database.py
```

**Todos esses scripts estão na raiz e funcionam diretamente!**

---

## 🔧 Estrutura Correta do Projeto

```
Linkedin/                    ← Você deve estar AQUI
├── run.py                   ← Execute este arquivo! ⭐
├── test_application.py
├── example_usage.py
├── inspect_database.py
├── config.ini
├── .env
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   └── ...
└── ...
```

**Sempre execute scripts da raiz do projeto!**

---

## ⚠️ Erros Comuns

### ❌ Erro 1: Executar de Dentro do src/

```bash
# ERRADO
cd src
python main.py
```

**Solução**: Execute da raiz
```bash
cd ..
python run.py
```

---

### ❌ Erro 2: Executar main.py diretamente

```bash
# PROBLEMÁTICO
python .\src\main.py
```

**Solução**: Use run.py ou -m
```bash
python run.py
# ou
python -m src.main
```

---

### ❌ Erro 3: Imports não encontrados

```
ModuleNotFoundError: No module named 'src'
```

**Solução**: Verifique se está na raiz do projeto
```bash
# Verificar diretório atual
pwd         # Linux/Mac
cd          # Windows

# Deve mostrar: .../Linkedin/
```

---

## ✅ Checklist de Solução

Quando encontrar `ModuleNotFoundError`:

- [ ] Estou no diretório raiz do projeto?
- [ ] Existe o arquivo `run.py`?
- [ ] Estou usando `python run.py`?
- [ ] O diretório `src/` existe?
- [ ] Existe `src/__init__.py`?

Se todas as respostas forem SIM, deve funcionar!

---

## 🎓 Entendendo Python Imports

### Imports Absolutos (Nosso Caso)

```python
from src.config import config
```

**Precisa**: Diretório raiz no PYTHONPATH

**Vantagem**: Claro de onde vem cada módulo

---

### Imports Relativos

```python
from .config import config
```

**Precisa**: Executar como pacote (`-m`)

**Vantagem**: Independente de estrutura externa

---

### Nossa Escolha: Absolutos + run.py

**Melhor de dois mundos**:
- Imports claros
- Execução simples
- Funciona sempre

---

## 📚 Referências

- [Python Packaging User Guide](https://packaging.python.org/)
- [Real Python - Python Imports](https://realpython.com/absolute-vs-relative-python-imports/)
- [PEP 328 - Imports: Multi-Line and Absolute/Relative](https://peps.python.org/pep-0328/)

---

## ✅ Status

**Problema**: Resolvido  
**Solução**: `run.py` criado  
**Como usar**: `python run.py`  
**Status**: ✅ Funcionando

---

**Documentado em**: 09/12/2025  
**Versão**: 2.0.0

