# Arquitetura

O projeto separa interface, dados, analytics e recursos de IA para manter o MVP simples de evoluir.

## Camadas

```text
app/
```

Entradas Streamlit, paginas e estilo visual.

```text
src/data/
```

Clientes de dados externos e normalizacao de fontes.

```text
src/analytics/
```

Funcoes puras de calculo: carteira, retornos, risco, renda fixa e apoio macro.

```text
src/terminal/
```

Parser, modelos de comando e registry.

```text
src/commands/
```

Comandos que conectam terminal a fontes especificas quando aplicavel.

```text
src/ai/
```

Analise local de documentos e preparacao para futura integracao LLM.

```text
tests/
```

Testes unitarios sem dependencia de internet.

## Principios

- UI nao deve espalhar chamadas diretas a APIs externas.
- Funcoes de analytics devem ser puras sempre que possivel.
- Dados externos precisam de erros amigaveis.
- Nenhuma funcionalidade deve virar recomendacao financeira absoluta.
- Testes devem mockar internet e providers.

## Fluxo Geral

```text
Streamlit page
  -> command/parser ou formulario
  -> src/data ou src/analytics
  -> resultado normalizado
  -> renderizacao na UI
```

## CI

O GitHub Actions executa:

```text
pytest
```

em push e pull request.

## Evolucao Planejada

- Integrar comandos com todos os conectores.
- Adicionar persistencia local quando necessario.
- Expandir relatorios com LLM opcional.
- Adicionar checagens de lint e tipos.
