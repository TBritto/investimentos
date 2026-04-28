# Terminal de Investimentos

MVP em Streamlit para consulta, organizacao e analise educacional de dados financeiros em portugues do Brasil. O projeto combina dados publicos, OpenBB, uploads locais e calculos analiticos para apoiar investigacao e acompanhamento de investimentos.

> Ferramenta de apoio a decisao. Este projeto nao faz recomendacao de compra, venda ou manutencao de ativos.

## Funcionalidades do MVP

- Terminal de comandos com parser, registry e historico de sessao.
- Consulta macroeconomica via Banco Central SGS: Selic, IPCA e dolar.
- Camada isolada para OpenBB, incluindo cotacao, historico e comparacao de ativos.
- Upload de carteira via CSV e composicao por ativo/classe.
- Metricas de risco e retorno: retornos, acumulado, volatilidade, drawdown, correlacao e Sharpe.
- Simulador educacional de renda fixa: prefixado, IPCA+ e percentual CDI.
- Analise local de documentos financeiros sem API externa.
- Visual escuro e denso inspirado em terminais financeiros modernos, sem copiar marca ou layout proprietario.
- CI com pytest em push e pull request.

## Instalacao

Requisitos:

- Python 3.11+
- pip

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

Crie o `.env` a partir do exemplo:

```bash
cp .env.example .env
```

Variaveis atuais:

```env
FMP_API_KEY=
OPENBB_PROVIDER=
FIREFLY_BASE_URL=
FIREFLY_ACCESS_TOKEN=
PLUGGY_CLIENT_ID=
PLUGGY_CLIENT_SECRET=
PLUGGY_BASE_URL=
```

Nao coloque chaves ou segredos no codigo.

## Execucao

Aplicacao principal:

```bash
streamlit run app.py
```

Versao multipage:

```bash
streamlit run app/streamlit_app.py
```

Por padrao, o Streamlit abre em `http://localhost:8501`.

## Estrutura

```text
.
├── app.py
├── app/
│   ├── streamlit_app.py
│   ├── styles.py
│   └── pages/
├── docs/
│   ├── architecture.md
│   ├── commands.md
│   └── data_sources.md
├── src/
│   ├── ai/
│   ├── analytics/
│   ├── commands/
│   ├── data/
│   ├── storage/
│   └── terminal/
├── tests/
├── pyproject.toml
└── requirements.txt
```

## Comandos

Comandos reconhecidos no terminal:

```text
help
macro selic
macro ipca
macro dolar
quote AAPL
compare AAPL MSFT
fund 00.000.000/0001-91
finance accounts
finance transactions
finance categories
finance summary
portfolio risco
```

Veja detalhes em [docs/commands.md](docs/commands.md).

## Fontes de Dados

- Banco Central SGS para Selic, IPCA e dolar.
- OpenBB para cotacoes, historicos e fundamentos quando providers estiverem configurados.
- CVM para cadastro e informe diario de fundos.
- Tesouro Direto para precos e taxas de titulos publicos.
- Firefly III para financas pessoais quando configurado.
- CSV local para composicao de carteira.
- Arquivos PDF/TXT/Markdown enviados pelo usuario para analise local.

Veja detalhes em [docs/data_sources.md](docs/data_sources.md).

## Limites Conhecidos

- Resultados sao informativos e educacionais.
- Renda fixa usa aproximacoes simplificadas.
- Analise de documentos e heuristica, sem LLM por padrao.
- PDF depende de `pypdf` quando usado.
- Algumas fontes OpenBB podem exigir provider/API key.
- Testes evitam internet; chamadas externas devem ser mockadas.

## Roadmap

- Expandir dashboard de carteira com risco, drawdown e comparativos.
- Adicionar conectores de CVM, Tesouro Direto e B3 quando as fontes forem definidas.
- Melhorar relatorios com LLM opcional via variavel de ambiente.
- Adicionar lint/type-check ao CI.
- Criar fluxo de deploy para ambiente Streamlit.

## Testes

```bash
pytest
```

O CI em `.github/workflows/tests.yml` executa `pytest` em push e pull request.

## Arquitetura

Veja [docs/architecture.md](docs/architecture.md).
