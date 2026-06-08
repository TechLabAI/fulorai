# Design Tokens — ASST · Frontend

> Tokens visuais específicos do ASST. O módulo consome `@journeyos/shared/ui-tokens` como base; aqui
> só os **semânticos de domínio** (estados de asset, tipos, origem de versão) que mapeiam para tokens
> compartilhados. Nenhuma cor hardcoded — sempre via token.

## Estados de asset (chip de estado)

| Estado | Token semântico (base) | Uso |
|---|---|---|
| `RASCUNHO` | `--jos-color-neutral` | cinza — em edição |
| `EM_REVISAO` | `--jos-color-warning` | âmbar — aguardando aprovação |
| `APROVADO` | `--jos-color-info` | azul — aprovado, pronto para publicar |
| `PUBLICADO` | `--jos-color-success` | verde — versão vigente disponível |
| `REJEITADO` | `--jos-color-danger` | vermelho — rejeitado |
| `ARQUIVADO` | `--jos-color-neutral-muted` | cinza esmaecido — soft-delete |

## Origem da versão (badge)

| Origem | Token | Uso |
|---|---|---|
| `MANUAL` | `--jos-color-neutral` | badge neutro |
| `ASSET_STUDIO` | `--jos-color-accent` (IA) | badge de destaque — proveniência IA |

## Tipos de asset (ícone)

| `tipoAsset` | Ícone (Material) |
|---|---|
| `LANDING_PAGE` | `web` |
| `EMAIL` | `mail` |
| `CRIATIVO` | `image` |
| `ROTEIRO` | `movie` |
| `DOCUMENTO` | `description` |
| `SCRIPT_SDR` | `record_voice_over` |

## Notas
- Todos os tokens semânticos resolvem para `@journeyos/shared/ui-tokens` (sem valores fixos no ASST).
- SCSS isolado em `libs/asst/styles`; componentes nunca declaram cor literal.
- Caso a base `ui-tokens` não exponha um semântico (ex.: `--jos-color-accent`), criar alias no
  `libs/asst/styles` apontando para o token base mais próximo e registrar como dívida de design.

## Referências
- `@journeyos/shared/ui-tokens` · `docs/architecture/frontend/standards/asset-driven-ui.md`
- SPEC-02 (componentes que consomem os chips/badges)
