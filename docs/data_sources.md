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
