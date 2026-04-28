# Terminal de Investimentos

MVP em Streamlit para consulta e analise de ativos usando OpenBB. A base foi reorganizada a partir de um projeto de referencia para separar entrada da aplicacao, acesso a dados, calculos analiticos, armazenamento/configuracao e futuros recursos de IA.

## Escopo do MVP

- Consulta de historico de precos via OpenBB.
- Indicadores tecnicos basicos: medias moveis, Bandas de Bollinger e RSI.
- Visualizacao de demonstrativos e indicadores fundamentalistas quando o provedor configurado estiver disponivel.
- Simulacao simples de carteira com retorno acumulado, retorno anualizado, volatilidade anualizada e Sharpe.
- Interface em portugues do Brasil.

Este projeto nao implementa recomendacao automatica de compra, venda ou manutencao de ativos. O conteudo exibido e informativo e educacional.

## Estrutura

```text
.
├── app.py                  # Entrada do Streamlit
├── app/
│   ├── streamlit_app.py    # Entrada multipage do Streamlit
│   └── pages/              # Paginas placeholder do MVP
├── pyproject.toml          # Metadados e configuracao de testes
├── src/
│   ├── ai/                 # Reservado para recursos futuros de IA
│   ├── analytics/          # Indicadores, carteira e metricas
│   ├── commands/           # Comandos do terminal
│   ├── data/               # Clientes de dados externos
│   ├── storage/            # Configuracao e persistencia local
│   └── terminal/           # Interface Streamlit
└── tests/                  # Testes automatizados
```

## Requisitos

- Python 3.11+
- Streamlit, Pandas, Plotly, DuckDB, PyArrow, Requests, Pydantic, Pytest, Python-dotenv e OpenBB
- Uma chave FMP opcional para endpoints fundamentalistas do OpenBB

## Configuracao

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependencias:

```bash
pip install -r requirements.txt
```

Crie um arquivo `.env` a partir de `.env.example`:

```bash
cp .env.example .env
```

Preencha apenas as chaves que voce for usar:

```env
FMP_API_KEY=
```

Nao coloque chaves no codigo-fonte.

## Executando

```bash
streamlit run app.py
```

Para abrir a versao multipage com placeholders da Issue 1:

```bash
streamlit run app/streamlit_app.py
```

A aplicacao abre por padrao em `http://localhost:8501`.

## Comandos macro e mercado

A pagina `Terminal` aceita os comandos iniciais:

```text
macro selic
macro ipca
macro dolar
quote AAPL
compare AAPL MSFT
```

Os comandos macro usam series publicas do Banco Central SGS via `src/data/bcb.py`.
As respostas sao normalizadas para as colunas `date`, `value` e `code`, com cache local em `data/raw/bcb/`.

Esses comandos usam `src/data/openbb_client.py`, que encapsula as chamadas ao OpenBB.
Para endpoints que exigem provider, configure as variaveis no `.env`, por exemplo:

```env
FMP_API_KEY=
```

Falhas de provider ou API sao convertidas em mensagens amigaveis pela excecao `OpenBBClientError`.

## Carteira CSV

A pagina `Carteira` permite upload de um CSV com as colunas:

```text
ativo, quantidade, preco_medio, classe, data_compra
```

`data_compra` e opcional. A pagina calcula `valor_investido`, percentual por ativo, percentual por classe e total investido. Esta etapa nao busca preco atual e nao faz recomendacao de compra ou venda.

## Testes

```bash
pytest
```
