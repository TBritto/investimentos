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

## OpenBB

Usado para cotacoes, historico de ativos, comparacao e dados fundamentalistas quando provider estiver configurado.

Modulo principal:

```text
src/data/openbb_client.py
```

Variaveis opcionais:

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

## CVM Dados Abertos

Usado para cadastro e informe diario de fundos de investimento com dados publicos da CVM.

Modulo principal:

```text
src/data/cvm.py
```

Endpoints publicos usados:

```text
https://dados.cvm.gov.br/dados/FI/CAD/DADOS/cad_fi.csv
https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_YYYYMM.zip
```

Funcoes principais:

```text
normalize_cnpj(cnpj)
get_fund_registry(use_cache=True)
search_funds(query)
find_fund_by_cnpj(cnpj)
get_fund_daily_report(year, month, use_cache=True)
```

O cache local fica em:

```text
data/raw/cvm/
```

O informe diario e normalizado para:

```text
cnpj_fundo, data_competencia, valor_cota, patrimonio_liquido, captacao_dia, resgate_dia, numero_cotistas
```

O terminal reconhece `fund CNPJ` para consultar cadastro de um fundo por CNPJ.

## Tesouro Direto

Usado para precos e taxas publicos de titulos do Tesouro Direto.

Modulo principal:

```text
src/data/tesouro.py
```

Fonte publica:

```text
https://www.tesourotransparente.gov.br/ckan/api/3/action/package_show?id=taxas-dos-titulos-ofertados-pelo-tesouro-direto
```

O recurso CSV oficial `precotaxatesourodireto.csv` e baixado a partir dos metadados CKAN e cacheado localmente em:

```text
data/raw/tesouro/
```

Funcoes principais:

```text
get_treasury_bonds(use_cache=True)
get_treasury_price_history(year=None, use_cache=True)
normalize_treasury_bonds(df)
search_treasury_bonds(query)
```

As colunas sao normalizadas, quando disponiveis, para:

```text
nome, tipo, vencimento, taxa_compra, taxa_venda, preco_compra, preco_venda, data_base
```

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
