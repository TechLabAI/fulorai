# API Contract — COMM (`/api/v1/{templates,messages,routing-rules,channels,webhooks}`)

> REST surface of `comm-service`. All error responses use `application/problem+json` (RFC 7807,
> `shared/contratos/error-model.md`). EARS invariants per endpoint.
> Guide: `docs/architecture/backend/standards/ears-notation.md`.

## Conventions

- Base path: `/api/v1`.
- Auth: Bearer JWT (RS256) issued by WRKS; validated against WRKS JWKS. No anonymous user endpoints (webhooks are the exception — see §6).
- Mandatory headers: `Authorization`, `X-Correlation-Id` (propagated/generated).
- Tenant: `empresa_id` travels as a JWT claim; `EmpresaContextHolder.require()` fixes the schema.
  No `empresaId` in path/body. `X-Empresa-Id` is debug/log only and never overrides the claim.
- Authorization: `comm.<recurso>.<acao>` permissions resolved via WRKS `AccessDecision`
  (`comm.template.criar|editar|ler|publicar|arquivar`, `comm.studio.compor`,
  `comm.mensagem.enviar|ler`, `comm.roteamento.criar|editar|ler`, `comm.canal.configurar|ler`).
- Idempotency: dispatch (`POST /messages`) and Template Studio accept an `Idempotency-Key` header (SPEC-05).

---

## 1. Templates — `/templates` · perm `comm.template.*`

### POST `/templates`  · perm `comm.template.criar`
Create a template in `RASCUNHO`.
- Request: `{ "nome": "Boas-vindas", "canal": "WHATSAPP", "tipoTemplate": "TRANSACIONAL", "assunto": null, "corpo": "Olá {{nome}}!", "variaveis": ["nome"], "assetOrigemId": null }`
- Response 201: `TemplateResponse { id, nome, canal, tipoTemplate, estado: "RASCUNHO", versao: 1, criadoEm }` + `Location`.
- `WHEN a caller with permission comm.template.criar posts a valid template, THE SYSTEM SHALL create it in state RASCUNHO and return 201.`
- `IF canal is not one of WHATSAPP|EMAIL|TELEGRAM|SMS, THEN THE SYSTEM SHALL reject with 422 error.code 'comm.template.canal-invalido'.`
- `IF tipoTemplate is not one of TRANSACIONAL|MARKETING|NOTIFICACAO, THEN THE SYSTEM SHALL reject with 422 error.code 'comm.template.tipo-invalido'.`
- `IF nome is blank, THEN THE SYSTEM SHALL reject with 422 error.code 'comm.template.nome-obrigatorio'.`
- `IF canal is EMAIL AND assunto is blank, THEN THE SYSTEM SHALL reject with 422 error.code 'comm.template.assunto-obrigatorio'.`

### GET `/templates/{id}`  · perm `comm.template.ler`
- Response 200: `TemplateResponse`.
- `IF the template does not exist in the caller's tenant schema, THEN THE SYSTEM SHALL respond 404 error.code 'comm.template.nao-encontrado'.`

### GET `/templates`  · perm `comm.template.ler`
List/search templates. Query: `?canal=&tipo=&estado=&q=&page=&size=`.
- Response 200: `Page<TemplateResumo>`.
- `THE SYSTEM SHALL return only templates belonging to the caller's tenant schema.`

### PATCH `/templates/{id}`  · perm `comm.template.editar`
Update template metadata/body (bumps `versao`).
- `WHEN a template body is edited, THE SYSTEM SHALL increment versao and re-validate that declared {{variaveis}} match placeholders in corpo.`
- `IF corpo references a placeholder not declared in variaveis, THEN THE SYSTEM SHALL reject with 422 error.code 'comm.template.variavel-nao-declarada'.`

### POST `/templates/{id}/ativar`  · perm `comm.template.publicar`
Transition `RASCUNHO → ATIVO` (usable for real dispatch).
- `WHEN activation is requested on a RASCUNHO template, THE SYSTEM SHALL move it to ATIVO.`

### POST `/templates/{id}/arquivar`  · perm `comm.template.arquivar`
- Response 200. Soft-delete: `estado=ARQUIVADO`.
- `WHEN archival is requested, THE SYSTEM SHALL set estado=ARQUIVADO without physically deleting sent messages that referenced it.`

### POST `/templates/{id}/studio/compose`  · perm `comm.studio.compor`
AI-assisted composition via TechLab AI `document_composition`. Produces a new draft body.
- Request: `{ "brief": "...", "contexto": { ... }, "assetOrigemId": "..."? }` + optional `Idempotency-Key`.
- Response 200: `TemplateResponse` (new RASCUNHO body, bumped `versao`).
- `WHEN a composition request succeeds, THE SYSTEM SHALL store the result as the template body in state RASCUNHO and SHALL never activate it automatically.`
- `THE SYSTEM SHALL record the briefComposicao for provenance.`
- `IF TechLab AI is unavailable or times out, THEN THE SYSTEM SHALL respond 503 error.code 'comm.studio.ia-indisponivel' AND SHALL NOT change the template body.`
- `IF the same Idempotency-Key is replayed, THEN THE SYSTEM SHALL return the previously produced body without calling TechLab AI again.`

---

## 2. Messages (dispatch) — `/messages` · perm `comm.mensagem.*`

### POST `/messages`  · perm `comm.mensagem.enviar`
Request a dispatch. Accepted asynchronously (rendered, persisted, enqueued).
- Request: `{ "templateId": "...", "leadId": "...", "canal": "WHATSAPP"?, "variaveis": { "nome": "Rafael" }, "agendadoPara": null }` + optional `Idempotency-Key`.
- Response 202: `MensagemResponse { id, estadoEntrega: "ENFILEIRADA", canal, leadId, criadoEm }` + `Location`.
- `WHEN a valid dispatch is accepted, THE SYSTEM SHALL render the content from the ATIVO template + variaveis, persist a Mensagem in PENDENTE, enqueue it via the outbox, and return 202 with estadoEntrega=ENFILEIRADA.`
- `IF the referenced template is not in state ATIVO, THEN THE SYSTEM SHALL reject with 409 error.code 'comm.template.nao-ativo'.`
- `IF no canal is given AND routing cannot resolve a channel for the recipient, THEN THE SYSTEM SHALL reject with 422 error.code 'comm.roteamento.sem-canal'.`
- `IF the resolved canal has no active config_canal for the tenant, THEN THE SYSTEM SHALL reject with 422 error.code 'comm.canal.nao-configurado'.`
- `IF a required {{variavel}} has no value in variaveis, THEN THE SYSTEM SHALL reject with 422 error.code 'comm.mensagem.variavel-ausente'.`
- `IF the same Idempotency-Key (per empresa) was already used, THEN THE SYSTEM SHALL return the existing Mensagem with 200 and SHALL NOT dispatch again.`

### GET `/messages/{id}`  · perm `comm.mensagem.ler`
- Response 200: `MensagemResponse { id, estadoEntrega, canal, provedor, provedorMessageId, tentativas, motivoFalha, criadoEm, atualizadoEm }`.
- `IF the message does not exist in the caller's tenant schema, THEN THE SYSTEM SHALL respond 404 error.code 'comm.mensagem.nao-encontrada'.`

### GET `/messages`  · perm `comm.mensagem.ler`
List. Query: `?leadId=&canal=&estado=&desde=&ate=&page=&size=`.
- Response 200: `Page<MensagemResumo>`.

### GET `/messages/{id}/events`  · perm `comm.mensagem.ler`
- Response 200: `List<EventoEntregaResponse { tipo, ocorridoEm }>` (lifecycle trail).
- `THE SYSTEM SHALL return the delivery events in chronological order.`

---

## 3. Routing rules — `/routing-rules` · perm `comm.roteamento.*`

### POST `/routing-rules`  · perm `comm.roteamento.criar`
- Request: `{ "nome": "...", "prioridade": 10, "condicoes": { "segmento": "quente" }, "canalPreferido": "WHATSAPP", "canaisFallback": ["EMAIL"], "templateId": "...", "ativa": true }`.
- Response 201: `RegraRoteamentoResponse`.
- `IF canalPreferido is not a valid canal, THEN THE SYSTEM SHALL reject with 422 error.code 'comm.template.canal-invalido'.`

### GET `/routing-rules` / `GET /routing-rules/{id}`  · perm `comm.roteamento.ler`
- Response 200: list / single `RegraRoteamentoResponse` (ordered by `prioridade`).

### PATCH `/routing-rules/{id}`  · perm `comm.roteamento.editar`
- Update conditions/priority/channels/active flag.

---

## 4. Channels — `/channels` · perm `comm.canal.*`

### POST `/channels`  · perm `comm.canal.configurar`
Configure a channel/provider for the tenant.
- Request: `{ "canal": "WHATSAPP", "provedor": "META_WABA", "identidadeRemetente": "+5511...", "credencialRef": "secret://comm/whatsapp", "janelaEnvio": null }`.
- Response 201: `ConfigCanalResponse { id, canal, provedor, identidadeRemetente, ativo }` — **never returns the secret**.
- `THE SYSTEM SHALL store only credencialRef (a secret reference) and SHALL NEVER persist or return the raw provider secret.`
- `IF a config already exists for (canal, provedor) in the tenant, THEN THE SYSTEM SHALL reject with 409 error.code 'comm.canal.duplicado'.`

### GET `/channels`  · perm `comm.canal.ler`
- Response 200: `List<ConfigCanalResponse>` (secret reference masked).

### PATCH `/channels/{id}`  · perm `comm.canal.configurar`
- Update sender identity / credential reference / active flag / send window.

---

## 5. Errors (RFC 7807 ProblemDetail)

| HTTP | error.code | Quando |
|---|---|---|
| 422 | `comm.template.canal-invalido` | canal fora do enum |
| 422 | `comm.template.tipo-invalido` | tipoTemplate fora do enum |
| 422 | `comm.template.nome-obrigatorio` | nome vazio |
| 422 | `comm.template.assunto-obrigatorio` | e-mail sem assunto |
| 422 | `comm.template.variavel-nao-declarada` | placeholder no corpo não declarado |
| 404 | `comm.template.nao-encontrado` | template inexistente no tenant |
| 409 | `comm.template.nao-ativo` | disparo sobre template não-ATIVO |
| 404 | `comm.mensagem.nao-encontrada` | mensagem inexistente no tenant |
| 422 | `comm.mensagem.variavel-ausente` | variável obrigatória sem valor |
| 409 | `comm.mensagem.estado-invalido` | transição de entrega inválida |
| 422 | `comm.roteamento.sem-canal` | nenhum canal resolvido (preferido/fallback) |
| 422 | `comm.canal.nao-configurado` | canal sem config ativa no tenant |
| 409 | `comm.canal.duplicado` | config (canal, provedor) já existe |
| 503 | `comm.studio.ia-indisponivel` | TechLab AI fora/timeout |
| 503 | `comm.canal.provedor-indisponivel` | provedor de canal fora (após retries) |
| 401 | `comm.auth.token-invalido` | JWT ausente/inválido |
| 403 | `comm.acesso.permissao-negada` | falta permissão `comm.*` |
| 401 | `comm.webhook.assinatura-invalida` | callback de provedor sem assinatura válida |

Todos os corpos seguem `shared/contratos/error-model.md` (`type`, `title`, `status`, `detail`, `code`, `correlationId`).

---

## 6. Webhooks — `/webhooks/{canal}` (provider callbacks)

> **Not** authenticated by user JWT. Authenticated by the provider's signature/secret.

### POST `/webhooks/{canal}`
Receive a delivery/read receipt from a channel provider.
- Request: provider-specific payload (normalized by the channel adapter).
- Response 200 (ack) — always fast-ack; processing is idempotent.
- `WHEN a provider callback is received with a valid signature, THE SYSTEM SHALL normalize it into an EventoEntrega and advance the message delivery state accordingly.`
- `IF the webhook signature is missing or invalid, THEN THE SYSTEM SHALL reject with 401 error.code 'comm.webhook.assinatura-invalida' AND SHALL NOT mutate any message.`
- `IF the same provider callback (provedorMessageId + tipo) is delivered twice, THEN THE SYSTEM SHALL process it once (idempotent) and ack the duplicate as a no-op.`
- `THE SYSTEM SHALL resolve the tenant from the referenced message, never from untrusted webhook payload fields, before writing to any schema.`
