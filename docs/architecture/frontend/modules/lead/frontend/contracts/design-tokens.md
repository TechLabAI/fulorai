# Design Tokens — LEAD · Frontend

> Tokens específicos do LEAD, sobre `@journeyos/shared/ui-tokens`. Foco: faixas de score e dimensões
> do Maturity Score, com **acessibilidade** (cor nunca é o único canal — sempre rótulo + número).

## Faixas de score (`Faixa`)

| Token | Faixa | Uso | Nota a11y |
|---|---|---|---|
| `--lead-score-frio` | `FRIO` (0–39) | chip/realce de score baixo | sempre acompanhado do rótulo "Frio" + número |
| `--lead-score-morno` | `MORNO` (40–69) | score intermediário | rótulo "Morno" + número |
| `--lead-score-quente` | `QUENTE` (70–100) | score alto | rótulo "Quente" + número |

> Faixas (limiares) são **ilustrativas** — os cortes reais vêm da regra ativa (BE). A UI lê a faixa do
> backend quando disponível; não hardcoda a classificação de negócio.

## Dimensões (radar 6D)

| Token | Dimensão |
|---|---|
| `--lead-dim-perfil` | PERFIL |
| `--lead-dim-engajamento` | ENGAJAMENTO |
| `--lead-dim-intencao` | INTENCAO |
| `--lead-dim-capacidade` | CAPACIDADE |
| `--lead-dim-urgencia` | URGENCIA |
| `--lead-dim-aderencia` | ADERENCIA |

- Paleta com **contraste AA** sobre o fundo do radar; cada eixo do radar tem rótulo textual.
- Estados: `assistIa=true` → badge `--lead-assist-ia` (neutro/positivo); `assistIa=false` → badge
  `--lead-assist-deterministico` (neutro, **nunca** vermelho/erro).

## Notas

- Tokens vivem em `libs/lead/styles` e referenciam variáveis de `@journeyos/shared/ui-tokens`
  (não duplicar paleta base).
- Componentes de visualização (`ScoreRadarComponent`, `DimensionBarComponent`) consomem estes tokens;
  candidatos a promoção a shared (asset-driven-ui) preservam os nomes.

## Referências
- `04-frontend-architecture-direction.md` · ADR-005 (visualização do Maturity Score)
- `@journeyos/shared/ui-tokens`
