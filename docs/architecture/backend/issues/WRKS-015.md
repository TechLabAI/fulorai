# WRKS-015 -- Producers Kafka + transactional outbox (eventos de identidade)

## Contexto
Publicação dos eventos de ciclo de vida de identidade com garantia transacional (outbox),
incluindo o evento-âncora `modelo.acesso.alterado`.

## Spec de referencia
- SPEC-09-messaging-architecture
- event-contracts.md

## Escopo
- `infrastructure/messaging/producer`: publica `ModeloAcessoAlterado`, `UsuarioCriado`,
  `UsuarioEmpresaAssociado`, `EmpresaProvisionada`, `SessaoEstabelecida`, `SessaoEncerrada`.
- Transactional outbox: evento publicado implica commit do DB.
- Headers `correlationId`, `empresaId`, `eventId`, `occurredAt`, `source=wrks-service`.

## Resultado esperado
Eventos publicados de forma atômica com a mudança no banco; consumidores deduplicam por `eventId`.

## Criterios de aceite
- [ ] `modelo.acesso.alterado` publicado com a nova versão na mesma fronteira transacional.
- [ ] Outbox: falha de publish não aplica mudança duplicada no DB.
- [ ] Headers presentes em todos os eventos.

## Dependencias
- WRKS-007 (persistência), INT-WRKS-006

## Estimativa
M

## Prioridade
P6
