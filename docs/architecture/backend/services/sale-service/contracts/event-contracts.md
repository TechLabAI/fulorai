# Event Contracts — SALE

> Kafka (AWS MSK). Topic naming `journey-os.<aggregate>.<verb>`. All events carry headers
> `correlationId`, `empresaId`, `eventId`, `occurredAt`, `source=sale-service`, `schemaVersion`.
> EARS behaviour per event. Guide: `docs/architecture/backend/standards/ears-notation.md`.

## 1. Published events

### `journey-os.oportunidade.criada`
Emitted when a deal is opened (from a qualified lead or via API).

```json
{ "eventId": "uuid", "oportunidadeId": "uuid", "empresaId": "emp_x", "leadId": "uuid",
  "estagio": "NOVA", "valorEstimado": 1997.00, "occurredAt": "ISO-8601", "schemaVersion": 1 }
```
- `WHEN an oportunidade is created, THE SYSTEM SHALL publish journey-os.oportunidade.criada.`

### `journey-os.oportunidade.estagio.alterado`
Emitted on every pipeline stage transition.

```json
{ "eventId": "uuid", "oportunidadeId": "uuid", "empresaId": "emp_x",
  "deEstagio": "NOVA", "paraEstagio": "PROPOSTA", "occurredAt": "ISO-8601", "schemaVersion": 1 }
```
- `WHEN an oportunidade stage changes, THE SYSTEM SHALL publish journey-os.oportunidade.estagio.alterado.`

### `journey-os.oportunidade.ganha`
Emitted when a deal is marked won.

```json
{ "eventId": "uuid", "oportunidadeId": "uuid", "empresaId": "emp_x", "valorEstimado": 1997.00,
  "occurredAt": "ISO-8601", "schemaVersion": 1 }
```
- `WHEN an oportunidade is marked won, THE SYSTEM SHALL publish journey-os.oportunidade.ganha.`

### `journey-os.oportunidade.perdida`
Emitted when a deal is marked lost (with reason).

```json
{ "eventId": "uuid", "oportunidadeId": "uuid", "empresaId": "emp_x", "motivoPerda": "preco",
  "occurredAt": "ISO-8601", "schemaVersion": 1 }
```
- `WHEN an oportunidade is marked lost, THE SYSTEM SHALL publish journey-os.oportunidade.perdida carrying motivoPerda.`

### `journey-os.compra.confirmada` — **anchor**
Emitted when an order is confirmed and revenue is recognized.

```json
{ "eventId": "uuid", "compraId": "uuid", "empresaId": "emp_x", "idExterno": "HOT-9981",
  "origem": "hotmart", "contatoRef": "rafael@acme.com", "oportunidadeId": "uuid",
  "valorTotal": 1997.00, "moeda": "BRL", "occurredAt": "ISO-8601", "schemaVersion": 1 }
```
- `WHEN an order is confirmed and revenue is recognized, THE SYSTEM SHALL publish journey-os.compra.confirmada.`
- `THE SYSTEM SHALL publish this event in the same transaction boundary as persisting the compra (transactional outbox).`
- `IF the same (idExterno, origem) was already confirmed, THEN THE SYSTEM SHALL NOT publish journey-os.compra.confirmada again (idempotency).`

### `journey-os.receita.atribuida`
Emitted when a purchase's revenue is distributed across touchpoints.

```json
{ "eventId": "uuid", "compraId": "uuid", "empresaId": "emp_x", "versaoModelo": 1,
  "atribuicoes": [ { "touchpoint": "meta-ads", "tipo": "CAMPANHA", "valor": 1997.00 } ],
  "occurredAt": "ISO-8601", "schemaVersion": 1 }
```
- `WHEN revenue is attributed for a compra, THE SYSTEM SHALL publish journey-os.receita.atribuida carrying the model version and the per-touchpoint breakdown.`

### `journey-os.ltv.atualizado`
Emitted when a contact's LTV is recomputed.

```json
{ "eventId": "uuid", "contatoRef": "rafael@acme.com", "empresaId": "emp_x",
  "valorTotal": 3994.00, "numCompras": 2, "occurredAt": "ISO-8601", "schemaVersion": 1 }
```
- `WHEN a contact's LTV changes, THE SYSTEM SHALL publish journey-os.ltv.atualizado.`

## 2. Consumed events

### `journey-os.lead.qualificado` (from LEAD)
- `WHEN journey-os.lead.qualificado is received, THE SYSTEM SHALL create or update an oportunidade for that lead in the initial pipeline stage (idempotent by leadId).`

### `journey-os.lead.score.atualizado` (from LEAD)
- `WHEN journey-os.lead.score.atualizado is received, THE SYSTEM SHALL update the priority/estimated value of the open oportunidade for that lead, if any.`

### `journey-os.empresa.provisionada` (from WRKS)
- `WHEN journey-os.empresa.provisionada is received, THE SYSTEM SHALL seed default pipeline stages, an initial oferta catalog and a default LAST_TOUCH attribution model into the new emp_<slug> schema (idempotent).`

### `journey-os.modelo.acesso.alterado` (from WRKS)
- `WHEN journey-os.modelo.acesso.alterado is received, THE SYSTEM SHALL invalidate the cached AccessDecision entries affected by the new modelo_acesso_versao.`

> *(Post-MVP: consume `journey-os.lead.roteado` / `journey-os.estagio.transicionado` / `journey-os.jornada.concluida` from JRNY to set the responsible user and enrich attribution touchpoints.)*

## 3. Idempotency

| Concern | Key | Window |
|---|---|---|
| Purchase ingestion | `(id_externo, origem)` upsert | indefinite (revenue dedup) |
| Re-attribution | `(compra_id, versao_modelo)` | latest wins |
| Opportunity from lead | `leadId` (one open deal per lead) | indefinite |
| Consume (seed/cache) | `(correlationId, evento)` | indefinite |
| Publish | transactional outbox + `eventId` | dedup by consumers on `eventId` |

## 4. Payload versioning

- Envelope carries `schemaVersion` (int). Additive changes bump minor; breaking changes publish to a
  new topic suffix `.v2`. Consumers tolerate unknown fields. Monetary fields are strings/decimals,
  never floats, to avoid precision loss.

## 5. Context propagation (async)

- `empresaId` travels as a message header; consumers populate `EmpresaContextHolder` and `clear()` in
  `finally` (see `shared/multi-empresa.md`). No buyer PII in event payloads beyond `contatoRef`
  (normalized key) — never `nome_comprador`/`email_comprador` in clear.
