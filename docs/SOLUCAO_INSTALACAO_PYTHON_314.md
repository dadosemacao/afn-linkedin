# Solução: Problema de Instalação com Python 3.14

**Data**: 09 de Dezembro de 2025  
**Problema**: Erro de compilação ao instalar pandas com Python 3.14

---

## Problema Identificado

### Erro Reportado

```
pandas/_libs/tslibs/base.pyx.c:5399:70: error: too few arguments to function call, expected 6, have 5
    int ret = _PyLong_AsByteArray((PyLongObject *)v,
                                  bytes, sizeof(val),
                                  is_little, !is_unsigned);
```

### Causa Raiz

Python 3.14 é uma versão muito recente (ainda em desenvolvimento/alpha) e muitos pacotes com extensões C, especialmente pandas, ainda não têm suporte completo. O erro ocorre porque:

1. A API interna do Python (`_PyLong_AsByteArray`) mudou em Python 3.14
2. O pandas 2.1.4 foi compilado para versões anteriores do Python
3. A assinatura da função mudou, exigindo um parâmetro adicional (`with_exceptions`)

---

## Soluções Disponíveis

### Solução 1: Usar Python 3.11 ou 3.12 (Recomendado)

Python 3.11 e 3.12 são versões estáveis e amplamente suportadas por todos os pacotes do projeto.

#### Instalação com pyenv (Mac/Linux)

```bash
# Instalar pyenv (se não tiver)
brew install pyenv  # Mac
# ou
curl https://pyenv.run | bash  # Linux

# Instalar Python 3.12
pyenv install 3.12.7

# Definir como versão local do projeto
cd /Users/emerson.antonio/Developar/afirmanet/afn-linkedin
pyenv local 3.12.7

# Verificar versão
python --version  # Deve mostrar Python 3.12.7

# Recriar ambiente virtual
rm -rf venv
python -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

#### Instalação com Homebrew (Mac)

```bash
# Instalar Python 3.12
brew install python@3.12

# Usar Python 3.12 para criar venv
python3.12 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### Solução 2: Atualizar Versões dos Pacotes

O arquivo `requirements.txt` foi atualizado para usar versões mais recentes de pandas e numpy que podem ter melhor suporte para Python 3.14:

```txt
pandas>=2.2.0
numpy>=1.26.4
```

**Tentar instalação novamente:**

```bash
# Atualizar pip primeiro
pip install --upgrade pip setuptools wheel

# Instalar dependências
pip install -r requirements.txt
```

**Nota**: Mesmo com versões atualizadas, Python 3.14 pode ainda apresentar problemas. A Solução 1 é mais confiável.

### Solução 3: Usar Docker (Mais Confiável)

O Dockerfile já está configurado com Python 3.11, que é totalmente compatível:

```bash
# Construir e executar
docker-compose up -d

# Ver logs
docker-compose logs -f
```

Esta é a opção mais confiável e isola completamente o ambiente Python.

---

## Verificação da Solução

Após aplicar uma das soluções, verifique:

```bash
# Verificar versão do Python
python --version

# Verificar instalação dos pacotes críticos
python -c "import pandas; print(f'pandas {pandas.__version__}')"
python -c "import numpy; print(f'numpy {numpy.__version__}')"
python -c "import selenium; print(f'selenium {selenium.__version__}')"

# Testar importação completa
python -c "from src.config import config; print('Config OK')"
```

---

## Recomendações Finais

1. **Para desenvolvimento local**: Use Python 3.11 ou 3.12 com pyenv
2. **Para produção**: Use Docker (já configurado com Python 3.11)
3. **Para testes rápidos**: Tente atualizar pandas/numpy primeiro (Solução 2)

---

## Referências

- Python 3.14 ainda está em desenvolvimento: https://www.python.org/downloads/
- Pandas compatibility: https://pandas.pydata.org/docs/getting_started/install.html
- Docker setup: Ver `docs/GUIA_DOCKER.md`

---

**Status**: Resolvido com atualização de requirements.txt e documentação de alternativas.

