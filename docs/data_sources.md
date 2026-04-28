# Fontes de Dados

## Camada comum

Integrações externas devem preferir os helpers comuns para padronizar cache, HTTP e erros amigáveis:

```text
src/data/errors.py
src/data/http.py
src/storage/cache.py
```

Exceções comuns:

```text
DataSourceError
DataUnavailableError
DataParsingError
DataValidationError
```

O cache local fica por padrão em `data/raw/<fonte>/`, com nomes de arquivos sanitizados por `get_cache_path`.

## Banco Central SGS

Usado para series publicas macroeconomicas:

- Selic
- IPCA
- dolar

Modulo principal:

```text
src/data/bcb.py
```

Os dados sao normalizados para:

```text
date, value, code
```

O cache local fica em:

```text
data/raw/bcb/
```

Arquivos CSV de cache nao devem ser versionados.

## OpenBB

Usado para cotacoes, historico de ativos, comparacao e dados fundamentalistas quando provider estiver configurado.

Modulo principal:

```text
src/data/openbb_client.py
```

Variavel opcional:

```env
OPENBB_PROVIDER=
FMP_API_KEY=
```

`OPENBB_PROVIDER` define o provider padrao usado pela camada `src/data/openbb_client.py` quando um provider nao for informado explicitamente. Chaves de providers, como `FMP_API_KEY`, devem ficar apenas no `.env` local e nunca no codigo.

As funcoes principais sao:

```text
get_equity_quote(symbol)
get_equity_history(symbol, start_date=None, end_date=None, provider=None)
compare_equities(symbols, start_date=None, end_date=None, provider=None)
```

As respostas sao normalizadas, quando as colunas existirem na fonte, para:

```text
date, symbol, open, high, low, close, volume
```

Falhas de provider/API devem ser convertidas para mensagens amigaveis.

## CSV de Carteira

Upload local na pagina Carteira.

Colunas obrigatorias:

```text
ativo, quantidade, preco_medio, classe
```

Coluna opcional:

```text
data_compra
```

O MVP calcula valor investido e composicao. Nao busca preco atual nessa etapa.

## Documentos Financeiros

Arquivos suportados:

- TXT
- Markdown
- PDF

A analise inicial e local, sem API externa. PDF pode exigir `pypdf`.

## Limites

- Nao usar dados proprietarios sem licenca.
- Nao armazenar chaves no repositorio.
- Testes nao devem depender de internet.
- Fontes externas devem ser mockadas em testes.
