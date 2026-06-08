# SPEC-05 — Idempotency & Concurrency

> ADR-003 (mensageria idempotente), ADR-005 (decisão reproduzível). Relaciona SPEC-02 (Routing
> Engine), SPEC-09 (eventos). EARS guide: `docs/architecture/backend/standards/ears-notation.md`.

## Objetivo

Garantir que o processamento dirigido por evento seja idempotente (sem matrícula/decisão
duplicada ao reprocessar) e consistente sob concorrência (eventos simultâneos para o mesmo lead,
avanços concorrentes).

## Escopo

- **In:** idempotência de consumers (`processed_events` por `eventId`); guarda de unicidade de inscrição ATIVA; concorrência otimista no avanço de inscrição; reprodutibilidade da decisão.
- **Out:** retries de transporte (Kafka/Feign — platform-patterns); contrato do assist (SPEC-10).

## Decisões técnicas

- Consumers persistem `eventId` em `processed_events` **antes** de qualquer efeito colateral.
- Guard adicional do gatilho de roteamento: índice parcial `inscricao_jornada (lead_id, jornada_id) WHERE estado='ATIVA'` impede matrícula duplicada mesmo sob reentrega/concorrência.
- Concorrência otimista: `@Version` em `inscricao_jornada`; conflito → re-leitura/reavaliação, nunca estado corrompido.
- Reprodutibilidade: `MotorRoteamento` é função pura de `snapshot_entrada` + versão de regras (ADR-005) — o mesmo evento reprocessado produziria a mesma decisão (e é descartado por idempotência).

## Casos de borda

- Reentrega do mesmo `lead.qualificado` → no-op (já em `processed_events`); sem matrícula/decisão nova.
- Dois eventos LEAD simultâneos para o mesmo lead → um avança, o outro vê o estado já alterado (re-leitura/optimistic) e decide coerentemente; no máximo uma inscrição ATIVA.
- Race de matrícula (dois "primeiros eventos") → índice parcial garante uma única inscrição ATIVA.

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL persist eventId in processed_events before performing any side effect of a consumed event.`
- `WHEN a consumed event's eventId already exists in processed_events, THE SYSTEM SHALL skip processing as a no-op.`
- `IF the same lead.qualificado event is reprocessed, THEN THE SYSTEM SHALL NOT create a duplicate enrolment and SHALL NOT write a duplicate decisao_roteamento.`
- `THE SYSTEM SHALL allow at most one ATIVA enrolment per (lead_id, jornada_id) even under concurrent or replayed events (partial unique index).`
- `WHEN two domain events target the same lead concurrently, THE SYSTEM SHALL apply optimistic concurrency on the enrolment so at most one advance commits per version, re-reading on conflict.`
- `THE SYSTEM SHALL produce the same decision for the same snapshot_entrada and rule version (reproducible evaluation).`
