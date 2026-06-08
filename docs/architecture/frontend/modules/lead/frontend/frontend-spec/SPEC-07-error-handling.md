# SPEC-07 — Error Handling — LEAD · Frontend

> Mapeamento `ProblemDetail` (RFC 7807, BE) → `AppError` (`@journeyos/shared/error-model`) →
> apresentação via `@journeyos/shared/ui-feedback`. Critério toast/banner/modal + retry.

## Mapa de erros

| BE `error.code` | HTTP | `AppError.kind` | Apresentação | Ação FE |
|---|---|---|---|---|
| `lead.lead.nao-encontrado` | 404 | `not_found` | estado de página "lead não encontrado" | CTA voltar à fila |
| `lead.lead.anonimizado` | 409 | `conflict` | **banner** no detalhe | desabilita editar/requalificar |
| `lead.lead.base-legal-invalida` | 422 | `validation` | **erro de campo** (base legal) | foca o campo |
| `lead.qualification.sem-regra-ativa` | 409 | `business_rule` | **banner** + CTA | desabilita "Requalificar"; link p/ `/lead/qualification` |
| `lead.qualification.regra-nao-encontrada` | 404 | `not_found` | **toast** | mantém lista de versões |
| `lead.segment.predicado-invalido` | 422 | `validation` | **erro de campo** (predicado) | mantém editor aberto |
| `lead.survey.pergunta-invalida` | 422 | `validation` | **erro de campo** (resposta) | mantém diálogo aberto |
| `lead.ia.indisponivel` | 200 | — (não-erro) | **badge neutro** "score determinístico" | nenhuma; fluxo segue |
| `iam.*` (JWT) | 401/403 | — | tratado na Access Layer | redirect login / acesso negado |
| genérico 5xx | 5xx | `server` | **banner** "erro inesperado" | botão "tentar novamente" |

## Critério de apresentação

- **Toast** — falha transitória/ação pontual (ex.: ativação de regra falhou; refetch).
- **Banner** — estado persistente que muda o que a página oferece (lead anonimizado; sem regra ativa).
- **Modal** — apenas confirmação de ações destrutivas (anonimizar/expurgar), **antes** da chamada.
- **Erro de campo** — validações `422` mapeadas ao campo do formulário correspondente.

## Retry

- **Manual** (botão "tentar novamente") para list/get (idempotentes).
- **Sem auto-retry** para `qualify`/`activate`/ações LGPD (efeitos no BE) — evita duplicação.
- O assist de IA **não** é retried pelo FE (é responsabilidade do BE); `lead.ia.indisponivel` nunca
  vira retry/erro na UI.

## Critérios de aceite (EARS)

- `WHEN the BE returns a ProblemDetail, THE SYSTEM SHALL map it to an AppError via @journeyos/shared/error-model before display.`
- `IF the BE returns lead.ia.indisponivel, THEN THE SYSTEM SHALL show the neutral "score determinístico" badge and SHALL NOT show an error toast.`
- `WHILE a lead is in estado ANONIMIZADO, THE SYSTEM SHALL show a banner and SHALL disable profile edit and requalify actions.`
- `IF a destructive LGPD action is requested, THEN THE SYSTEM SHALL require an explicit confirmation modal before calling the BE.`
- `WHEN a list or get request fails with a 5xx, THE SYSTEM SHALL offer a manual retry and SHALL NOT auto-retry mutating operations.`

## Referências
- BE: `lead-service/contracts/api-contract.md` (error catalogue) · `05-state-and-data-flow.md` §5
- `docs/architecture/frontend/standards/access-layer-contracts.md`
