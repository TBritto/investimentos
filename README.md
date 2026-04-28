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
├── pyproject.toml          # Metadados e configuracao de testes
├── src/
│   ├── ai/                 # Reservado para recursos futuros de IA
│   ├── analytics/          # Indicadores, carteira e metricas
│   ├── data/               # Clientes de dados externos
│   ├── storage/            # Configuracao e persistencia local
│   └── terminal/           # Interface Streamlit
└── tests/                  # Testes automatizados
```

## Requisitos

- Python 3.11+
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

A aplicacao abre por padrao em `http://localhost:8501`.

## Testes

```bash
pytest
```
