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

## Pluggy Open Finance

Usado para preparar conexao com contas bancarias reais via Open Finance/Pluggy.

Modulo principal:

```text
src/data/pluggy.py
```

Variaveis obrigatorias para ambiente real:

```env
PLUGGY_CLIENT_ID=
PLUGGY_CLIENT_SECRET=
```

Variavel opcional para sandbox/testes:

```env
PLUGGY_BASE_URL=
PLUGGY_CONNECT_URL=
```

Funcoes principais:

```text
create_api_key()
create_connect_token(client_user_id=None, item_id=None, oauth_redirect_url=None, webhook_url=None)
get_items()
get_accounts(item_id=None)
get_transactions(account_id, from_date=None, to_date=None, page_size=100)
get_connect_widget_url(connect_token)
```

Comandos no terminal:

```text
openfinance connect-token
openfinance items
openfinance accounts
openfinance accounts ITEM_ID
openfinance transactions ACCOUNT_ID
```

Credenciais Pluggy devem ficar apenas no `.env`. O fluxo de conexao bancaria exige consentimento do usuario via Pluggy Connect Widget; o projeto nao guarda senha de banco.

A pagina `Open Finance` permite:

- verificar se a configuracao esta pronta;
- gerar connect token de curta duracao;
- abrir o Pluggy Connect Widget;
- listar conexoes, contas e transacoes apos consentimento.

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
