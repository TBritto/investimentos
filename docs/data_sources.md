# Fontes de Dados

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
FMP_API_KEY=
```

Falhas de provider/API devem ser convertidas para mensagens amigaveis.

## Firefly III

Usado para integrar controle de financas pessoais self-hosted via API REST do Firefly III.

Modulo principal:

```text
src/data/firefly.py
```

Variaveis obrigatorias:

```env
FIREFLY_BASE_URL=
FIREFLY_ACCESS_TOKEN=
```

Funcoes principais:

```text
get_accounts(account_type=None)
get_transactions(start_date=None, end_date=None, limit=50)
get_categories()
get_finance_summary(start_date=None, end_date=None)
```

Comandos no terminal:

```text
finance accounts
finance transactions
finance categories
finance summary
```

O token deve ser gerado no Firefly III como Personal Access Token ou por fluxo OAuth. Nao guarde tokens no repositorio.

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
