# Design Tokens — COMM · Frontend

> Tokens específicos do COMM (estados de entrega/template e badges de canal). Consomem
> `@journeyos/shared/ui-tokens`; não redefinem a paleta base — apenas mapeiam semântica COMM → tokens.

## Estados de entrega (mensagem) → cor/ícone semântico

| Estado | Token semântico | Ícone (Material) | Intenção |
|---|---|---|---|
| `PENDENTE` | `--jos-state-neutral` | `schedule` | aguardando |
| `ENFILEIRADA` | `--jos-state-info` | `outbox` | na fila |
| `ENVIADA` | `--jos-state-info-strong` | `send` | enviado ao provedor |
| `ENTREGUE` | `--jos-state-success` | `done` | entregue |
| `LIDA` | `--jos-state-success-strong` | `done_all` | lida (terminal) |
| `FALHADA` | `--jos-state-danger` | `error` | falha (terminal) |

## Estados de template → cor/ícone

| Estado | Token semântico | Ícone |
|---|---|---|
| `RASCUNHO` | `--jos-state-neutral` | `edit_note` |
| `ATIVO` | `--jos-state-success` | `check_circle` |
| `ARQUIVADO` | `--jos-state-muted` | `inventory_2` |

## Badge de canal

| Canal | Token de marca | Ícone |
|---|---|---|
| `WHATSAPP` | `--jos-channel-whatsapp` | `chat` |
| `EMAIL` | `--jos-channel-email` | `mail` |
| `TELEGRAM` | `--jos-channel-telegram` | `send` |
| `SMS` | `--jos-channel-sms` | `sms` |

> Os tokens `--jos-state-*` já existem em `@journeyos/shared/ui-tokens`. Os `--jos-channel-*` são
> **propostas** a promover ao shared se reutilizados por outros módulos; até lá ficam em
> `libs/comm/styles`. Estados de entrega/template usam **cor + ícone + rótulo** (nunca cor sozinha —
> acessibilidade).

## Referências

- `@journeyos/shared/ui-tokens` · `libs/comm/styles` · `libs/comm/ui` (`StateChipComponent`, `CanalBadgeComponent`)
- `docs/architecture/frontend/standards/asset-driven-ui.md`
