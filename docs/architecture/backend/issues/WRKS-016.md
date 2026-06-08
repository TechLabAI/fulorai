# WRKS-016 -- Consumer de auditoria (journey-os.* → evento_auditoria + Elastic)

## Contexto
WRKS é o sink único da trilha de auditoria: consome todos os eventos `journey-os.*` e grava
`evento_auditoria` + indexa em `audit-events`.

## Spec de referencia
- SPEC-09-messaging-architecture
- SPEC-05-idempotency-concurrency

## Escopo
- `infrastructure/messaging/consumer`: `AuditoriaEventConsumer` subscreve `journey-os.*`.
- Persiste 1 `evento_auditoria` por evento (idempotente em `correlationId`+`evento`).
- Indexa async no Elastic `audit-events` após a linha persistida (`AuditIndexPort`).
- Propaga contexto: header `empresaId` → `EmpresaContextHolder`, `clear()` em `finally`.

## Resultado esperado
Trilha consolidada e idempotente; indexação resiliente (PostgreSQL é a verdade).

## Criterios de aceite
- [ ] 1 linha por evento; duplicata (`correlationId`+`evento`) ignorada.
- [ ] `empresaId` populado em eventos de empresa; `clear()` em `finally`.
- [ ] Elastic down → linha persiste; index retry com backoff.

## Dependencias
- WRKS-007 (persistência), INT-WRKS-005 (Elastic)

## Estimativa
M

## Prioridade
P6
