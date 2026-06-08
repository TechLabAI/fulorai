# INT-WRKS-005 -- Indexação Elasticsearch (audit-events)

## Contexto
Indexação da trilha de auditoria no índice Elastic `audit-events` (domainContext WRKS),
via cliente Java direto.

## Spec de referencia
- integration-contracts.md §3
- SPEC-09-messaging-architecture

## Escopo
- `AuditIndexPort` adapter (cliente Java Elastic, `ELASTIC_URIS`, índice `audit-events`).
- Index async após `evento_auditoria` persistida; retry com backoff.

## Resultado esperado
Eventos auditados pesquisáveis no Elastic; PostgreSQL permanece source of truth.

## Criterios de aceite
- [ ] Documento indexado em `audit-events` por evento auditado.
- [ ] Elastic down → linha persiste; index retry; sem perda da verdade.

## Dependencias
- WRKS-016

## Estimativa
S

## Prioridade
P6
