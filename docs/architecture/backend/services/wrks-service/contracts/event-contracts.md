# Event Contracts — WRKS

> Kafka (AWS MSK). Topic naming `journey-os.<aggregate>.<verb>`. All events carry headers
> `correlationId`, `empresaId` (when tenant-scoped), `eventId`, `occurredAt`, `source=wrks-service`.
> EARS behaviour per event. Guide: `docs/architecture/backend/standards/ears-notation.md`.

## 1. Published events

### `journey-os.modelo.acesso.alterado` — **anchor (integration)**
Emitted whenever the access model changes (role↔permission bundle, association role change).
Drives AccessDecision cache invalidation across all services.

```json
{ "eventId": "uuid", "modeloAcessoVersao": 42, "motivo": "papel_permissao.editado",
  "papelCodigo": "HEAD_GROWTH", "empresaId": null, "occurredAt": "ISO-8601" }
```
- `WHEN a role's permission bundle or an association's role changes, THE SYSTEM SHALL publish journey-os.modelo.acesso.alterado carrying the new modelo_acesso_versao.`
- `THE SYSTEM SHALL publish this event in the same logical transaction boundary as the version bump (transactional outbox).`

### `journey-os.usuario.criado`
```json
{ "eventId": "uuid", "usuarioId": "uuid", "email": "...", "occurredAt": "ISO-8601" }
```
- `WHEN a usuario is activated, THE SYSTEM SHALL publish journey-os.usuario.criado.`

### `journey-os.usuario.empresa.associado`
```json
{ "eventId":"uuid", "usuarioId":"uuid", "empresaId":"emp_x", "papel":"SDR", "occurredAt":"..." }
```

### `journey-os.empresa.provisionada`
```json
{ "eventId":"uuid", "empresaId":"emp_x", "schema":"emp_x", "occurredAt":"..." }
```
- `WHEN MIG confirms the schema emp_<slug> is created, THE SYSTEM SHALL set the empresa to ATIVA and publish journey-os.empresa.provisionada.`

### `journey-os.sessao.estabelecida` / `journey-os.sessao.encerrada`
Heartbeat / lifecycle. `{ usuarioId, empresaId, motivo?, occurredAt }`.

## 2. Consumed events

### `journey-os.*` (all topics) → audit
WRKS subscribes to every `journey-os.*` topic to build `evento_auditoria` + index `audit-events`.
- `WHEN any journey-os.* event is received, THE SYSTEM SHALL persist one evento_auditoria row and index it into Elastic audit-events.`
- `IF an event with the same (correlationId, evento) was already persisted, THEN THE SYSTEM SHALL skip it (idempotent consume).`

## 3. Idempotency

| Concern | Key | Window |
|---|---|---|
| Audit consume | `(correlationId, evento)` unique check | indefinite (append-only) |
| Publish | transactional outbox + `eventId` | dedup by consumers on `eventId` |

## 4. Payload versioning

- Envelope carries `schemaVersion` (int). Additive changes bump minor; breaking changes publish to a new topic suffix `.v2`. Consumers tolerate unknown fields.

## 5. Context propagation (async)

- `empresaId` travels as a message header; consumers populate `EmpresaContextHolder` and `clear()` in `finally` (see `shared/multi-empresa.md`).
