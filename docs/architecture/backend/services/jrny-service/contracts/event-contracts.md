# Event Contracts — JRNY (Journey & Routing)

> Events produced/consumed by `jrny-service` over Kafka/AWS MSK. Envelope follows
> `shared/contratos/event-catalog.md` (eventId, eventType, eventVersion, producer, empresaId,
> correlationId, actor, data). Producers use the **outbox** pattern; consumers are **idempotent**
> on `eventId`. Consumers resolve the tenant from the envelope (`empresaId` header) and fix
> `EmpresaContextHolder` before processing. EARS for behavior.
> Guide: `docs/architecture/backend/standards/ears-notation.md`.

## 1. Produced events

| Event | Trigger | Consumers |
|---|---|---|
| `journey-os.jornada.publicada` | journey transitions to PUBLICADA | INTL (analytics), audit |
| `journey-os.lead.roteado` | **anchor** — Routing Engine decides a lead's target | COMM, SALE, INTL |
| `journey-os.estagio.transicionado` | lead moves between stages | COMM, SALE, INTL |
| `journey-os.jornada.concluida` | lead reaches a terminal stage | SALE, INTL, audit |

### `journey-os.jornada.publicada`
- `data`: `{ jornadaId, versao, nome, publicadoPor }`
- `WHEN a journey transitions to PUBLICADA, THE SYSTEM SHALL enqueue journey-os.jornada.publicada in the same transaction via the outbox.`

### `journey-os.lead.roteado` (anchor)
- `data`: `{ leadId, jornadaId, jornadaVersao, estagioAlvoId, inscricaoId, decisaoId, assistIa, resultado }`
- `WHEN the Routing Engine produces a ROTEADO decision, THE SYSTEM SHALL emit journey-os.lead.roteado after the routing transaction commits (outbox), carrying the decisaoId of the immutable decision.`
- `THE SYSTEM SHALL set assistIa to USADO|IGNORADO|INDISPONIVEL reflecting the AI-assist state of the decision.`
- `IF the decision result is SEM_MUDANCA or NAO_ROTEADO, THEN THE SYSTEM SHALL NOT emit journey-os.lead.roteado (the decision is still logged; only ROTEADO advances the lead).`

### `journey-os.estagio.transicionado`
- `data`: `{ leadId, jornadaId, estagioOrigemId, estagioDestinoId, inscricaoId, decisaoId }`
- `WHEN an enrolment's current stage changes, THE SYSTEM SHALL emit journey-os.estagio.transicionado after commit, carrying the origin and destination stage ids.`

### `journey-os.jornada.concluida`
- `data`: `{ leadId, jornadaId, inscricaoId, estagioFinalId }`
- `WHEN a routing advance lands a lead on a terminal stage, THE SYSTEM SHALL set the enrolment to CONCLUIDA and emit journey-os.jornada.concluida.`

## 2. Consumed events

| Event | Producer | Reaction |
|---|---|---|
| `journey-os.lead.qualificado` | LEAD | **routing trigger** — enroll/evaluate/route the lead |
| `journey-os.lead.score.atualizado` | LEAD | re-evaluate routing on score change |
| `journey-os.lead.segmento.alterado` | LEAD | re-evaluate routing on segment change |
| `journey-os.asset.versao.publicada` | ASST | refresh the stage's current content reference |
| `journey-os.modelo.acesso.alterado` | WRKS | invalidate cached AccessDecision for the tenant/role |
| `journey-os.empresa.provisionada` | WRKS | seed default journeys/stages for the new tenant |

### `journey-os.lead.qualificado` (routing trigger)
- `data` (from LEAD): `{ leadId, scoreAgregado, estadoQualificacao, dimensoes{PERFIL,ENGAJAMENTO,INTENCAO,CAPACIDADE,URGENCIA,ADERENCIA}, versaoRegra }`
- `WHEN journey-os.lead.qualificado is consumed, THE SYSTEM SHALL load the applicable PUBLICADA journey and the lead's enrolment (creating it if absent), evaluate the Routing Engine, persist exactly one decisao_roteamento, and emit journey-os.lead.roteado when the result is ROTEADO.`
- `THE SYSTEM SHALL build snapshot_entrada from the event payload (score + dimensoes + segmento + attributes) before evaluation.`
- `IF the eventId was already processed (processed_events), THEN THE SYSTEM SHALL skip it as a no-op (no duplicate enrolment or decision — R3).`

### `journey-os.lead.score.atualizado` / `journey-os.lead.segmento.alterado`
- `data` (score): `{ leadId, scoreAnterior, scoreAgregado, versaoRegra }`; `data` (segmento): `{ leadId, segmentoId, acao }`.
- `WHEN a score or segment change event is consumed for an enrolled lead, THE SYSTEM SHALL re-evaluate the Routing Engine; IF a rule fires THEN THE SYSTEM SHALL re-route (new decision + emit), ELSE THE SYSTEM SHALL persist a SEM_MUDANCA decision and keep the current stage.`

### `journey-os.asset.versao.publicada`
- `data` (from ASST): `{ assetId, versaoId, numero, tipoAsset }`.
- `WHEN journey-os.asset.versao.publicada is consumed, THE SYSTEM SHALL refresh the current content reference of any stage whose asset_ref_id matches assetId AND SHALL NOT re-route any lead as a result.`

### `journey-os.modelo.acesso.alterado`
- `WHEN journey-os.modelo.acesso.alterado is consumed, THE SYSTEM SHALL evict the affected AccessDecision cache entries before serving the next authorization check.`

### `journey-os.empresa.provisionada`
- `WHEN journey-os.empresa.provisionada is consumed for a new empresa, THE SYSTEM SHALL seed default journeys/stages for the tenant idempotently.`
- `IF the event was already processed (eventId in processed_events), THEN THE SYSTEM SHALL skip it as a no-op.`

## 3. Idempotency & versioning

- **Idempotency key:** `eventId`; consumers persist it in `processed_events` before side effects.
  The routing trigger additionally guards on the partial-unique `inscricao_jornada (lead_id,
  jornada_id) WHERE estado='ATIVA'` (no duplicate enrolment on reprocessing).
- **Window:** retained ≥ 30 days (aligned to platform default).
- **Payload versioning:** `eventVersion`/`schemaVersion` starts at `v1`; breaking changes add a
  `.v2` topic and keep `v1` during deprecation (per `event-catalog.md`). Consumers tolerate unknown fields.
- **DLQ:** 3 retries (1s/5s/30s backoff) → `journey-os.dlq.<evento>`.
- **Tenant context:** consumers read `empresaId` from the envelope header, fix
  `EmpresaContextHolder` and `clear()` in `finally`. No PII in payloads beyond identifiers + the
  qualification snapshot strictly needed for the decision.
