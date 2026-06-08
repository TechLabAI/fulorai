# SPEC-07 — Error Handling — INTL

> `ProblemDetail` (RFC 7807, BE) → `AppError` (`@journeyos/shared/error-model`) → mensagem
> user-facing (`@journeyos/shared/ui-feedback`). A particularidade do INTL: **falha de IA não é
> erro** — é estado de resposta (`DEGRADADA`/`NAO_FUNDAMENTADA`).

## Mapa `type` (BE) → tratamento (FE)

| Status | `type` (sufixo) | Mensagem FE | Apresentação | Retry |
|---|---|---|---|---|
| 400 | `validation-error` | "Verifique os campos destacados." | inline no form (Knowledge) | — |
| 401 | `unauthorized` | (silencioso) | Access Layer re-autentica | auto |
| 403 | `forbidden` | "Você não tem permissão para isso." | banner; guard oculta a rota | — |
| 404 | `not-found` | "Conversa/nó não encontrado nesta empresa." | empty state + voltar à lista | — |
| 409 | `conflict` | "Este nó está sendo indexado. Recarregue." | toast | botão recarregar |
| 503 | `embedding-unavailable` | "Indexação temporariamente indisponível. Tente de novo." | inline na ação Indexar | **botão "tentar de novo"** |
| 503 | `ai-unavailable` | — **não chega ao FE** (BE degrada para `200/DEGRADADA`) | — | — |
| 5xx | (genérico) | "Algo deu errado. Tente novamente." | toast | botão retry |

## Estados de resposta do Copilot (não são erro)

| `status` | Badge | Texto auxiliar | Citações |
|---|---|---|---|
| `RESPONDIDA` | verde "Fundamentada" | — | **sim** (chips clicáveis) |
| `NAO_FUNDAMENTADA` | âmbar "Sem evidência suficiente" | "Não encontrei base para responder com confiança." | **não** |
| `DEGRADADA` | cinza "Modo recuperação" | "A IA está indisponível; mostro o que recuperei, sem síntese." | evidência recuperada se houver, sem síntese |
| `ERRO` (transporte/4xx) | vermelho "Falha" | "Não consegui enviar sua pergunta." | — (com retry; a pergunta do usuário é preservada) |
| status desconhecido | trata como `DEGRADADA` | (defensivo, R6) | não |

## Critério toast × banner × modal × inline

- **Inline** — erros de formulário (Knowledge) e da ação Indexar (503 retry).
- **Toast** — falhas transitórias com retry (`409`, `5xx`).
- **Banner** — `403` em runtime (permissão revogada durante a sessão).
- **Empty state** — `404` (lista/conversa inexistente).
- **Modal** — não usado no MVP.

## Estratégia de retry

- **Manual** (botão) para `503 embedding-unavailable`, `409`, `5xx`.
- **Automático** apenas para `401` (re-auth via Access Layer).
- Perguntas do Copilot **nunca** retêm estado pendente após erro — viram bolha `ERRO` com ação
  "tentar de novo" (re-dispara a mesma pergunta).

## Critérios de aceite (EARS)

- `WHEN the BE returns a ProblemDetail, THE SYSTEM SHALL map it to an AppError via the shared error-model before rendering.`
- `WHILE a copilot answer status is DEGRADADA, THE SYSTEM SHALL render a neutral "Modo recuperação" badge and SHALL NOT render an error.`
- `WHILE a copilot answer status is NAO_FUNDAMENTADA, THE SYSTEM SHALL render an "Sem evidência suficiente" badge and SHALL NOT fabricate citations.`
- `IF a question fails on transport, THEN THE SYSTEM SHALL render an ERRO bubble preserving the question and SHALL offer a retry.`
- `IF a request returns 404, THEN THE SYSTEM SHALL render an empty state with a path back to the list.`
- `IF a permission is revoked at runtime with 403, THEN THE SYSTEM SHALL show a banner.`

## Referências

- `@journeyos/shared/error-model` · `@journeyos/shared/ui-feedback`
- BE: `intl-service/contracts/api-contract.md` §4 (Erros)
