# Guia de Comandos

O terminal do MVP fica em `app/pages/1_Terminal.py` e usa:

- `src/terminal/parser.py` para transformar texto em `CommandRequest`;
- `src/terminal/registry.py` para selecionar o handler;
- `src/terminal/commands.py` para devolver `CommandResult`.

## Modelo de Entrada

```text
CommandRequest
- raw: comando original
- command: primeiro token normalizado
- args: demais tokens
```

## Modelo de Saida

```text
CommandResult
- title
- message
- dataframe
- chart
```

## Comandos Disponiveis

### help

Mostra a lista de comandos reconhecidos.

```text
help
```

### macro

Reconhece indicadores macroeconomicos.

```text
macro selic
macro ipca
macro dolar
```

Os dados vêm do Banco Central SGS quando o conector está integrado.

### quote

Consulta cotacao de um ticker via camada OpenBB.

```text
quote AAPL
```

### compare

Compara historico de dois ou mais tickers via camada OpenBB.

```text
compare AAPL MSFT
```

### finance

Consulta dados de financas pessoais via Firefly III, quando `FIREFLY_BASE_URL` e `FIREFLY_ACCESS_TOKEN` estiverem configurados.

```text
finance accounts
finance transactions
finance categories
finance summary
```

### openfinance

Prepara consultas via Pluggy/Open Finance, quando `PLUGGY_CLIENT_ID` e `PLUGGY_CLIENT_SECRET` estiverem configurados.

```text
openfinance connect-token
openfinance items
openfinance accounts
openfinance accounts ITEM_ID
openfinance transactions ACCOUNT_ID
```

O comando `connect-token` gera um token de curta duracao para uso no Pluggy Connect Widget. O consentimento do usuario acontece fora do terminal.

### portfolio risco

Reservado para consolidar metricas de risco da carteira.

```text
portfolio risco
```

## Comandos Ainda Pendentes

Quando um comando reconhecido depender de um conector ainda nao mergeado, o terminal deve responder com mensagem amigavel. Ele nao deve inventar dados.

## Regra de Produto

Nenhum comando deve emitir recomendacao de compra, venda ou manutencao de ativos.
