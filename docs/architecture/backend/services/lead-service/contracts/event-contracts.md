# Event Contracts — LEAD

> Kafka (AWS MSK). Topic naming `journey-os.<aggregate>.<verb>`. All events carry headers
> `correlationId`, `empresaId`, `eventId`, `occurredAt`, `source=lead-service`, `schemaVersion`.
> EARS behaviour per event. Guide: `docs/architecture/backend/standards/ears-notation.md`.

## 1. Published events

### `journey-os.lead.capturado`
Emitted when a lead is created or merged on ingestion.

```json
{ "eventId": "uuid", "leadId": "uuid", "empresaId": "emp_x", "fonte": "meta-ads",
  "duplicado": false, "occurredAt": "ISO-8601", "schemaVersion": 1 }
```
- `WHEN a lead is captured (created or merged), THE SYSTEM SHALL publish journey-os.lead.capturado.`

### `journey-os.lead.qualificado` — **anchor**
Emitted when the Maturity Score is computed and the lead reaches a qualified state.

```json
{ "eventId": "uuid", "leadId": "uuid", "empresaId": "emp_x", "scoreAgregado": 78,
  "versaoRegra": 3, "estadoQualificacao": "QUALIFICADO",
  "dimensoes": { "PERFIL": 80, "ENGAJAMENTO": 70, "INTENCAO": 85, "CAPACIDADE": 60, "URGENCIA": 75, "ADERENCIA": 90 },
  "assistIa": false, "occurredAt": "ISO-8601", "schemaVersion": 1 }
```
- `WHEN a Maturity Score computation transitions a lead to QUALIFICADO, THE SYSTEM SHALL publish journey-os.lead.qualificado carrying the aggregate score, rule version and per-dimension breakdown.`
- `THE SYSTEM SHALL publish this event in the same transaction boundary as persisting the score (transactional outbox).`

### `journey-os.lead.score.atualizado`
Emitted on any recompute that changes the score (survey, rule activation, new signal).

```json
{ "eventId": "uuid", "leadId": "uuid", "empresaId": "emp_x", "scoreAnterior": 55,
  "scoreAgregado": 78, "versaoRegra": 3, "occurredAt": "ISO-8601", "schemaVersion": 1 }
```
- `WHEN a recompute changes a lead's aggregate score, THE SYSTEM SHALL publish journey-os.lead.score.atualizado.`

### `journey-os.lead.segmento.alterado`
Emitted when a lead enters or leaves a segment.

```json
{ "eventId": "uuid", "leadId": "uuid", "empresaId": "emp_x", "segmentoId": "uuid",
  "acao": "ENTROU", "occurredAt": "ISO-8601", "schemaVersion": 1 }
```
- `WHEN a lead's segment membership changes, THE SYSTEM SHALL publish journey-os.lead.segmento.alterado with acao ENTROU|SAIU.`

## 2. Consumed events

### `journey-os.empresa.provisionada` (from WRKS)
- `WHEN journey-os.empresa.provisionada is received, THE SYSTEM SHALL seed the default qualification rule and default segments into the new emp_<slug> schema (idempotent).`

### `journey-os.modelo.acesso.alterado` (from WRKS)
- `WHEN journey-os.modelo.acesso.alterado is received, THE SYSTEM SHALL invalidate the cached AccessDecision entries affected by the new modelo_acesso_versao.`

> *(Post-MVP: consume engagement signals from COMM/JRNY to feed the ENGAJAMENTO dimension.)*

## 3. Idempotency

| Concern | Key | Window |
|---|---|---|
| Capture | `chave_natural` upsert | indefinite (dedup) |
| Score recompute | `(lead_id, versao_regra, hash_sinais)` | latest wins |
| Consume (seed/cache) | `(correlationId, evento)` | indefinite |
| Publish | transactional outbox + `eventId` | dedup by consumers on `eventId` |

## 4. Payload versioning

- Envelope carries `schemaVersion` (int). Additive changes bump minor; breaking changes publish to
  a new topic suffix `.v2`. Consumers tolerate unknown fields.

## 5. Context propagation (async)

- `empresaId` travels as a message header; consumers populate `EmpresaContextHolder` and `clear()`
  in `finally` (see `shared/multi-empresa.md`). No PII in event payloads beyond identifiers.
