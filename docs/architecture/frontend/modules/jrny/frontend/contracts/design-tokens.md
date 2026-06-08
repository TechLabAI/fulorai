# Design Tokens — JRNY · Frontend

> Tokens **específicos** do JRNY. Base herdada de `@journeyos/shared/ui-tokens` (cores, espaçamento,
> tipografia, raios). Aqui só o que é próprio do domínio de jornada/roteamento. **Sem cores
> hardcoded**; faixas/estados sempre com rótulo textual (a11y, ADR-005).

## Estado da jornada (`JourneyStateChip`)

| Estado | Token semântico | Rótulo (sempre textual) |
|---|---|---|
| `RASCUNHO` | `--jos-color-state-neutral` | "Rascunho" |
| `PUBLICADA` | `--jos-color-state-success` | "Publicada" |
| `ARQUIVADA` | `--jos-color-state-muted` | "Arquivada" |

## Tipo de estágio (`StageTypeBadge`)

Cada `tipoEstagio` tem um token de cor + ícone, **sempre acompanhado do rótulo textual** (nunca só
cor). Sequência do funil: `CAPTURA → NUTRICAO → QUALIFICACAO → OFERTA → FECHAMENTO → POS_VENDA`.

| Tipo | Token | Ícone (Material) |
|---|---|---|
| `CAPTURA` | `--jos-jrny-stage-capture` | `download` |
| `NUTRICAO` | `--jos-jrny-stage-nurture` | `eco` |
| `QUALIFICACAO` | `--jos-jrny-stage-qualify` | `verified` |
| `OFERTA` | `--jos-jrny-stage-offer` | `local_offer` |
| `FECHAMENTO` | `--jos-jrny-stage-close` | `handshake` |
| `POS_VENDA` | `--jos-jrny-stage-postsale` | `loyalty` |

## Selo de assist IA (`AssistBadge`)

| `assistIa` | Token | Rótulo |
|---|---|---|
| `USADO` | `--jos-color-accent-ai` | "IA ✓" |
| `IGNORADO` / `INDISPONIVEL` | `--jos-color-state-neutral` | "Roteamento determinístico" |

> O selo neutro **nunca** usa cor de erro/alerta — a degradação é graciosa, não um problema.

## Funil (`FunnelChart`)

SVG/CSS leve (sem lib de chart pesada — ADR-005). Usa a escala de tokens dos tipos de estágio acima
para as barras do funil; valores numéricos sempre visíveis (não só altura da barra).

## Acessibilidade

- Contraste AA em todos os pares texto/fundo dos tokens acima.
- Tipo/estado/assist nunca dependem só de cor — rótulo textual obrigatório.
- Reordenação de estágios operável por teclado (foco visível com `--jos-focus-ring`).

## Referências
- `@journeyos/shared/ui-tokens` · `adr/ADR-005-canvas-builder-rendering.md` · `SPEC-02-component-hierarchy.md`
