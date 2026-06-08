# Design Tokens — INTL (Frontend)

> Tokens específicos do INTL, sobre `@journeyos/shared/ui-tokens`. INTL não introduz paleta nova;
> reusa os tokens globais e define apenas **semânticos de domínio** (estados de resposta do copiloto).

## Tokens semânticos (estado de resposta do Copilot)

| Token | Mapeia para (global) | Uso |
|---|---|---|
| `--intl-answer-grounded` | `--color-success` | badge `RESPONDIDA` (fundamentada) |
| `--intl-answer-ungrounded` | `--color-warning` | badge `NAO_FUNDAMENTADA` |
| `--intl-answer-degraded` | `--color-neutral-500` | badge `DEGRADADA` (modo recuperação) |
| `--intl-answer-error` | `--color-danger` | badge `ERRO` |
| `--intl-citation-chip-bg` | `--color-info-100` | fundo do chip de citação |

## Notas

- A distinção visual entre `RESPONDIDA` × `NAO_FUNDAMENTADA` × `DEGRADADA` é **requisito de
  correção** (INV-FE-1), não estética — cores + ícone + label, nunca cor isolada (acessibilidade).
- Layout do chat (largura de coluna, espaçamento de bolhas) usa o grid e o spacing scale globais.
- Dashboards de Analytics usam os tokens de chart globais; INTL não define paleta de gráfico própria.

> Se nenhum token de domínio for necessário na implementação, este arquivo pode ser absorvido pelos
> estilos de `libs/intl/styles` sem virar contrato — é um guia, não um bloqueio.
