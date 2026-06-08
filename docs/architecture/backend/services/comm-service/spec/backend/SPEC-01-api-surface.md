# SPEC-01 — API Surface

> EARS guide linkado. Fonte: `contracts/api-contract.md`. Relaciona SPEC-02 (lifecycle), SPEC-06 (security).

## Objetivo

Definir a superfície REST do `comm-service` (`/api/v1/templates`, `/messages`, `/routing-rules`,
`/channels`, `/webhooks/{canal}`), com status codes, erros ProblemDetail e invariantes por endpoint.

## Escopo

- **In:** endpoints de template (CRUD + Studio + ativar/arquivar), disparo de mensagem + status + eventos, regras de roteamento, config de canal, webhook de provedor.
- **Out:** lógica interna da state machine de entrega (SPEC-02), seleção de adapter (SPEC-03), segurança (SPEC-06).

## Decisões técnicas

- Base `/api/v1`; Bearer JWT (WRKS) em todos os endpoints de usuário; webhooks autenticados por assinatura do provedor (SPEC-06), não por JWT.
- `EmpresaContextHolder.require()` fixa o schema a partir do claim; nunca `empresaId` em path/body.
- ProblemDetail RFC 7807 (`shared/contratos/error-model.md`); `error.code` no namespace `comm.*`.
- `Idempotency-Key` em `POST /messages` e Template Studio (SPEC-05).
- Disparo é aceito de forma assíncrona (`202` ENFILEIRADA) — ver ADR-003.

## Implementação

- Controllers: `TemplateController`, `TemplateStudioController`, `MensagemController`, `RoteamentoController`, `CanalController`, `WebhookController`.
- DTO records request/response; `@RestControllerAdvice` (`ApiExceptionHandler`) → ProblemDetail.
- Paginação Spring `Page<>` em listagens.

## Casos de borda

- `POST /messages` sem `canal` explícito → roteamento resolve (SPEC-03); sem canal resolvível → 422 `comm.roteamento.sem-canal`.
- Webhook duplicado (mesmo `provedorMessageId`+tipo) → no-op idempotente, ack 200.
- Template EMAIL sem assunto → 422 `comm.template.assunto-obrigatorio`.

## Critérios de aceite (EARS)

- `WHEN a caller with permission comm.template.criar posts a valid template, THE SYSTEM SHALL create it in RASCUNHO and return 201.`
- `WHEN a valid dispatch is accepted, THE SYSTEM SHALL persist a Mensagem in PENDENTE, enqueue it via outbox, and return 202 with estadoEntrega=ENFILEIRADA.`
- `IF the referenced template is not ATIVO, THEN THE SYSTEM SHALL reject the dispatch with 409 error.code 'comm.template.nao-ativo'.`
- `IF a required {{variavel}} has no value, THEN THE SYSTEM SHALL reject with 422 error.code 'comm.mensagem.variavel-ausente'.`
- `IF an entity does not exist in the caller's tenant schema, THEN THE SYSTEM SHALL respond 404 with the matching comm.*.nao-encontrad* code.`
- `THE SYSTEM SHALL return only resources belonging to the caller's tenant schema.`
- `WHEN a provider webhook with a valid signature is received, THE SYSTEM SHALL ack 200 and advance the delivery state idempotently.`
