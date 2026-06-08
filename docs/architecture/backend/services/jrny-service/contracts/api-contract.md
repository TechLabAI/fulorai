# API Contract — JRNY (`/api/v1/journeys/**`, `/api/v1/routing/**`)

> REST surface of `jrny-service`. All error responses use `application/problem+json` (RFC 7807,
> `shared/contratos/error-model.md`). EARS invariants per endpoint.
> Guide: `docs/architecture/backend/standards/ears-notation.md`.

## Conventions

- Base paths: `/api/v1/journeys` (Journey Builder) and `/api/v1/routing` (Routing Engine queries + rule CRUD).
- Auth: Bearer JWT (RS256) issued by WRKS; validated against WRKS JWKS. No anonymous endpoints.
- Mandatory headers: `Authorization`, `X-Correlation-Id` (propagated/generated).
- Tenant: `empresa_id` travels as a JWT claim; `EmpresaContextHolder.require()` fixes the schema.
  No `empresaId` in path/body. `X-Empresa-Id` is debug/log only and never overrides the claim.
- Authorization: `jrny.<recurso>.<acao>` permissions resolved via WRKS `AccessDecision`
  (`jrny.jornada.criar|editar|publicar|arquivar|ler`, `jrny.estagio.criar|editar|ler`,
  `jrny.regra.criar|editar`, `jrny.roteamento.ler`).
- JRNY **decides and signals** — there is no endpoint that executes a channel/sales action.

---

## 1. Journey CRUD — `/api/v1/journeys` · perm `jrny.jornada.*`

### POST `/`  · perm `jrny.jornada.criar`
Create a journey in `RASCUNHO` (no stages yet, `versao=1`).
- Request: `{ "nome": "Funil de Lançamento", "descricao": "..." }`
- Response 201: `JornadaResponse { id, nome, descricao, estadoJornada: "RASCUNHO", versao: 1, criadoPor, criadoEm }` + `Location: /api/v1/journeys/{id}`.
- `WHEN a caller with permission jrny.jornada.criar posts a valid journey, THE SYSTEM SHALL create it in state RASCUNHO with versao=1 and return 201.`
- `IF nome is blank, THEN THE SYSTEM SHALL reject with 422 error.code 'jrny.jornada.nome-obrigatorio'.`

### GET `/{id}`  · perm `jrny.jornada.ler`
- Response 200: `JornadaResponse` (includes `estagios[]` ordered by `ordem` + `estadoJornada`).
- `IF the journey does not exist in the caller's tenant schema, THEN THE SYSTEM SHALL respond 404 error.code 'jrny.jornada.nao-encontrada'.`

### GET `/`  · perm `jrny.jornada.ler`
List journeys. Query: `?estado=&q=&page=&size=`.
- Response 200: `Page<JornadaResumo>`.
- `THE SYSTEM SHALL return only journeys belonging to the caller's tenant schema.`

### PATCH `/{id}`  · perm `jrny.jornada.editar`
Edit a `RASCUNHO` journey's metadata/stages.
- `IF the journey is not in RASCUNHO, THEN THE SYSTEM SHALL reject with 409 error.code 'jrny.jornada.transicao-invalida' (PUBLICADA is edited only via a new versao).`

### POST `/{id}/publicar`  · perm `jrny.jornada.publicar`
Transition `RASCUNHO → PUBLICADA`.
- Response 200: `JornadaResponse { estadoJornada: "PUBLICADA" }`.
- `WHEN publish is requested on a RASCUNHO journey that has at least one stage, THE SYSTEM SHALL set estado=PUBLICADA and emit journey-os.jornada.publicada.`
- `IF the journey has no stage, THEN THE SYSTEM SHALL reject with 422 error.code 'jrny.jornada.sem-estagio'.`
- `IF the journey is not in RASCUNHO, THEN THE SYSTEM SHALL reject with 409 error.code 'jrny.jornada.transicao-invalida'.`

### POST `/{id}/arquivar`  · perm `jrny.jornada.arquivar`
- Response 200. Logical delete: `estado=ARQUIVADA`.
- `WHEN archival is requested, THE SYSTEM SHALL set estado=ARQUIVADA without physically deleting stages, rules, enrolments or decisions.`
- `WHILE a journey is ARQUIVADA, THE SYSTEM SHALL NOT enroll or route any new lead into it.`

### POST `/{id}/nova-versao`  · perm `jrny.jornada.editar`
Clone a `PUBLICADA` journey into a new editable `RASCUNHO` with `versao+1`.
- `WHEN a new version is requested on a PUBLICADA journey, THE SYSTEM SHALL create a RASCUNHO copy with versao+1 AND SHALL NOT mutate the published version or any active enrolment.`

---

## 2. Stages — `/api/v1/journeys/{id}/estagios` · perm `jrny.estagio.*`

### POST `/{id}/estagios`  · perm `jrny.estagio.criar`
Add a stage to a `RASCUNHO` journey.
- Request: `{ "ordem": 1, "tipoEstagio": "CAPTURA", "nome": "Captura", "assetRefId": null, "terminal": false, "config": {} }`
- Response 201: `EstagioResponse { id, ordem, tipoEstagio, nome, assetRefId, terminal, config }`.
- `IF tipoEstagio is not one of CAPTURA|NUTRICAO|QUALIFICACAO|OFERTA|FECHAMENTO|POS_VENDA, THEN THE SYSTEM SHALL reject with 422 error.code 'jrny.estagio.tipo-invalido'.`
- `IF a stage with the same ordem already exists in the journey, THEN THE SYSTEM SHALL reject with 409 error.code 'jrny.estagio.ordem-duplicada'.`
- `IF the journey is not in RASCUNHO, THEN THE SYSTEM SHALL reject with 409 error.code 'jrny.jornada.transicao-invalida'.`

### PATCH `/{id}/estagios/{estagioId}`  · perm `jrny.estagio.editar`
- Edit a stage of a `RASCUNHO` journey (nome/asset_ref_id/terminal/config/ordem).

### GET `/{id}/estagios`  · perm `jrny.estagio.ler`
- Response 200: `List<EstagioResponse>` ordered by `ordem`.

---

## 3. Routing rules — `/api/v1/routing/rules` · perm `jrny.regra.*`

### POST `/rules`  · perm `jrny.regra.criar`
Create a versioned routing rule on a journey.
- Request: `{ "jornadaId": "...", "estagioOrigemId": null, "estagioDestinoId": "...", "condicao": { ... }, "prioridade": 100 }` (`condicao` grammar: `data-model.md` §5).
- Response 201: `RegraRoteamentoResponse { id, jornadaId, estagioOrigemId, estagioDestinoId, condicao, prioridade, versao: 1, ativa: true }`.
- `WHEN a caller with permission jrny.regra.criar posts a valid rule, THE SYSTEM SHALL create it with versao=1 and ativa=true.`
- `IF condicao references a field outside the documented snapshot grammar, THEN THE SYSTEM SHALL reject with 422 error.code 'jrny.regra.condicao-invalida'.`
- `IF estagioDestinoId does not belong to jornadaId, THEN THE SYSTEM SHALL reject with 422 error.code 'jrny.regra.estagio-invalido'.`

### PATCH `/rules/{ruleId}`  · perm `jrny.regra.editar`
Edit/deactivate a rule (produces `versao+1`).
- `WHEN a rule is edited, THE SYSTEM SHALL bump its versao and SHALL keep the prior version referenceable by existing decisao_roteamento rows.`

### GET `/rules?jornadaId=`  · perm `jrny.roteamento.ler`
- Response 200: `List<RegraRoteamentoResponse>` ordered by `prioridade`.

---

## 4. Routing queries — `/api/v1/routing` · perm `jrny.roteamento.ler`

### GET `/leads/{leadId}/journey`  · perm `jrny.roteamento.ler`
Read a lead's current journey state (consumed by COMM/SALE via `JourneyQueryClient`).
- Response 200: `InscricaoJornadaResponse { leadId, jornadaId, jornadaVersao, estagioCorrenteId, tipoEstagioCorrente, estado, entrouEm }` — or 404 if the lead has no enrolment.
- `THE SYSTEM SHALL return the lead's active enrolment for the tenant, or 404 error.code 'jrny.inscricao.nao-encontrada' when none exists.`

### GET `/leads/{leadId}/decisions`  · perm `jrny.roteamento.ler`
Read the immutable decision log for a lead ("why is it in this stage?").
- Response 200: `Page<DecisaoRoteamentoResponse { id, gatilho, regraId, assistIa, resultado, estagioAlvoId, motivo, decididoEm }>` newest first.
- `THE SYSTEM SHALL return the lead's routing decisions ordered by decididoEm descending, including SEM_MUDANCA and NAO_ROTEADO outcomes.`
- `THE SYSTEM SHALL never return a decision or enrolment belonging to another empresa.`

---

## 5. Errors (RFC 7807 ProblemDetail)

| HTTP | error.code | Quando |
|---|---|---|
| 422 | `jrny.jornada.nome-obrigatorio` | nome de jornada vazio |
| 422 | `jrny.jornada.sem-estagio` | publicar jornada sem estágios |
| 422 | `jrny.estagio.tipo-invalido` | tipoEstagio fora do enum |
| 422 | `jrny.regra.condicao-invalida` | condicao fora da gramática de snapshot |
| 422 | `jrny.regra.estagio-invalido` | estágio-destino não pertence à jornada |
| 404 | `jrny.jornada.nao-encontrada` | jornada inexistente no tenant |
| 404 | `jrny.inscricao.nao-encontrada` | lead sem inscrição no tenant |
| 409 | `jrny.jornada.transicao-invalida` | transição de estado não permitida |
| 409 | `jrny.estagio.ordem-duplicada` | ordem de estágio já usada na jornada |
| 401 | `jrny.auth.token-invalido` | JWT ausente/inválido |
| 403 | `jrny.acesso.permissao-negada` | falta permissão `jrny.*` |

Todos os corpos seguem `shared/contratos/error-model.md` (`type`, `title`, `status`, `detail`, `code`, `correlationId`).

> **No public routing-execution endpoint.** Routing happens **asynchronously**, triggered by LEAD
> events (`event-contracts.md` / SPEC-02). The HTTP surface above is **definition** (journeys,
> stages, rules) + **query** (lead journey state, decision log). JRNY does not expose a "route this
> lead now" command in the MVP.
