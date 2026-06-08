# Design Tokens — SALE · Frontend

> Tokens **específicos** do SALE. Base herdada de `@journeyos/shared/ui-tokens` (cores, espaçamento,
> tipografia, raios). Aqui só o que é próprio do domínio de pipeline/receita/atribuição. **Sem cores
> hardcoded**; estados sempre com rótulo textual (a11y, ADR-005).

## Estado da oportunidade (`OpportunityStateChip`)

| Estado | Token semântico | Rótulo (sempre textual) |
|---|---|---|
| `NOVA` | `--jos-color-state-neutral` | "Nova" |
| `EM_ANDAMENTO` | `--jos-color-state-info` | "Em andamento" |
| `GANHA` | `--jos-color-state-success` | "Ganha" |
| `PERDIDA` | `--jos-color-state-danger` | "Perdida" |
| `DESCARTADA` | `--jos-color-state-muted` | "Descartada" |

## Status da compra (`PurchaseStatusChip`)

| Status | Token | Rótulo |
|---|---|---|
| `CONFIRMADA` | `--jos-color-state-success` | "Confirmada" |
| `ESTORNADA` | `--jos-color-state-warning` | "Estornada" |
| `CANCELADA` | `--jos-color-state-muted` | "Cancelada" |

## Tipo de touchpoint da atribuição (`AttributionTypeBadge`)

Cada `tipo_touchpoint` tem token de cor + ícone, **sempre** com rótulo textual (nunca só cor).

| Tipo | Token | Ícone (Material) | Rótulo |
|---|---|---|---|
| `ORIGEM_LEAD` | `--jos-sale-touch-lead` | `person_search` | "Origem do lead" |
| `JORNADA` | `--jos-sale-touch-journey` | `account_tree` | "Jornada" |
| `CAMPANHA` | `--jos-sale-touch-campaign` | `campaign` | "Campanha" |
| `DIRETO` | `--jos-sale-touch-direct` | `bolt` | "Direto" |

## Kanban (`KanbanBoard` / `KanbanColumn` / `OpportunityCard`)

- Colunas (estágios) usam a escala neutra de superfície (`--jos-surface-*`); o **header da coluna**
  mostra contagem + soma de valor (sempre numérica, não só visual).
- Card em **move otimista** (`movingCardId`) usa `--jos-sale-card-moving` (estado transitório) + indicador
  textual "movendo…"; em **rollback**, retorna à coluna de origem com toast (sem cor de erro permanente no card).
- Foco de drag/teclado visível com `--jos-focus-ring` (CDK DragDrop + fallback de teclado, ADR-005).

## Funil de receita (`RevenueFunnelChart`)

SVG/CSS leve (sem lib de chart pesada). Barras por **origem**; valores monetários sempre visíveis
(formatados via `MoneyComponent`, `NUMERIC(15,2)` + `moeda`), não só altura da barra.

## Acessibilidade

- Contraste AA em todos os pares texto/fundo dos tokens acima.
- Estado/status/touchpoint nunca dependem só de cor — rótulo textual obrigatório.
- Drag do Kanban operável por teclado (fallback de lista/menu para mover estágio).

## Referências
- `@journeyos/shared/ui-tokens` · `adr/ADR-005-kanban-pipeline-rendering.md` · `SPEC-02-component-hierarchy.md`
