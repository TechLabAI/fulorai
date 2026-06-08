# SPEC-05 — Idempotency & Concurrency

> EARS guide linkado. Relaciona SPEC-03 (Studio), SPEC-09 (eventos).

## Objetivo

Garantir operações idempotentes (composição, publicação, consumo de eventos) e consistência sob
concorrência (versões/transições simultâneas).

## Escopo

- **In:** `Idempotency-Key` no Asset Studio; idempotência de publicação; idempotência de consumers (`processed_events`); concorrência otimista em transições.
- **Out:** retries de transporte (Kafka/Feign — platform-patterns).

## Decisões técnicas

- `Idempotency-Key` header → tabela/registro de requisições do Studio; replay retorna o mesmo resultado.
- Consumers persistem `eventId` em `processed_events` antes de efeitos colaterais.
- Concorrência otimista: coluna de versão (`@Version`)/checagem de estado na transição.

## Casos de borda

- Dois `publish` simultâneos do mesmo asset → apenas um efetiva; o outro vê estado já alterado (409).
- Composição reenviada (mesma key) → uma única chamada à IA, uma única versão.
- Reentrega de evento → no-op idempotente.

## Critérios de aceite (EARS)

- `IF the same Idempotency-Key is presented twice on Asset Studio, THEN THE SYSTEM SHALL produce exactly one version and return the original result.`
- `IF publish is retried for an already-published version, THEN THE SYSTEM SHALL be a no-op AND SHALL NOT emit a duplicate journey-os.asset.versao.publicada.`
- `WHEN two state transitions target the same asset concurrently, THE SYSTEM SHALL apply at most one and reject the other with 409 error.code 'asst.estado.transicao-invalida'.`
- `WHEN a consumed event's eventId already exists in processed_events, THE SYSTEM SHALL skip processing as a no-op.`
- `THE SYSTEM SHALL persist eventId in processed_events before performing any side effect of a consumed event.`
