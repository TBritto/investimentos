# Terminal de Investimentos

MVP em Streamlit para consulta e analise de ativos em portugues do Brasil. A base foi reorganizada para separar aplicacao, dados, analytics, terminal, armazenamento e recursos futuros de IA.

Este projeto nao implementa recomendacao automatica de compra, venda ou manutencao de ativos. O conteudo exibido e informativo e educacional.

## Escopo do MVP

- Terminal de comandos com historico de sessao.
- Series macroeconomicas publicas do Banco Central SGS.
- Camada isolada para consultas de mercado via OpenBB.
- Upload de carteira CSV e composicao por ativo/classe.
- Simulador educacional de renda fixa e marcacao a mercado simplificada.
- Metricas basicas de risco e retorno.
- Analise local inicial de documentos financeiros.
- Interface densa em tema escuro inspirada em terminais financeiros modernos, sem copiar marca, logo ou layout proprietario.

## Estrutura

```text
.
├── app.py
├── app/
│   ├── streamlit_app.py
│   ├── styles.py
│   └── pages/
├── src/
│   ├── ai/
│   ├── analytics/
│   ├── commands/
│   ├── data/
│   ├── storage/
│   └── terminal/
└── tests/
```

## Requisitos

- Python 3.11+
- Streamlit, Pandas, Plotly, Requests, Pydantic, Pytest e Python-dotenv
- OpenBB opcional para comandos de mercado

## Configuracao

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
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

Para abrir a versao multipage diretamente:

```bash
streamlit run app/streamlit_app.py
```

## Terminal de comandos

A pagina `Terminal` possui parser, registry e historico de comandos da sessao.

```text
help
macro selic
macro ipca
macro dolar
quote AAPL
compare AAPL MSFT
portfolio risco
```

Os comandos macro usam series publicas do Banco Central SGS via `src/data/bcb.py`, com cache local em `data/raw/bcb/`.

Os comandos `quote` e `compare` usam `src/data/openbb_client.py`, que encapsula as chamadas ao OpenBB e converte falhas de provider/API em mensagens amigaveis.

## Carteira CSV

A pagina `Carteira` permite upload de CSV com as colunas:

```text
ativo, quantidade, preco_medio, classe, data_compra
```

`data_compra` e opcional. A pagina calcula `valor_investido`, percentual por ativo, percentual por classe e total investido.

## Macro

A pagina `Macro` exibe Selic, IPCA e dolar usando as series publicas do Banco Central SGS. Ela permite selecionar periodo de 1 ano, 5 anos ou maximo, mostra cards com a ultima leitura, graficos de linha e tabelas expansivas.

## Renda fixa

A pagina `Renda Fixa` possui simulador educacional para prefixado, IPCA+ simplificado, percentual do CDI, valor presente aproximado e marcacao a mercado simplificada.

## Relatorios IA

A pagina `Relatorios IA` permite upload de PDF, TXT ou Markdown para extracao de texto, chunks, busca por termo, trechos relevantes e resumo heuristico local. Esta versao nao usa API externa e nao inventa informacoes fora do documento.

## Metricas de risco

Os modulos `src/analytics/returns.py` e `src/analytics/risk.py` incluem retornos periodicos, retorno acumulado, volatilidade anualizada, drawdown, matriz de correlacao e Sharpe simplificado.

## Visual terminal

A interface usa `app/styles.py` para aplicar tema escuro, paineis compactos, sidebar com watchlist mockada, barra de comando global e tabelas compactas.

## Testes

```bash
pytest
```
