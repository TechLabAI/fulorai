# INT-JRNY-005 -- Kafka config (topics, outbox, DLQ, retries)

## Contexto
Infraestrutura de mensageria do JRNY sobre Kafka/AWS MSK: tópicos consumidos/produzidos, padrão
outbox para produção transacional e DLQ com retries.

## Spec de referencia
- SPEC-09-messaging-architecture
- event-contracts.md
- integration-contracts.md

## Escopo
- `spring-kafka` config (`KAFKA_*` via `${VAR}`); consumer groups por serviço.
- Tópicos consumidos: `lead.qualificado`, `lead.score.atualizado`, `lead.segmento.alterado`,
  `asset.versao.publicada`, `modelo.acesso.alterado`, `empresa.provisionada`.
- Tópicos produzidos: `jornada.publicada`, `lead.roteado`, `estagio.transicionado`, `jornada.concluida`.
- Tabela outbox + publisher; DLQ `journey-os.dlq.<evento>`; backoff 1s/5s/30s (3 retries).
- `eventVersion`/`schemaVersion` v1; consumers toleram campos desconhecidos.

## Resultado esperado
Malha de tópicos pronta para JRNY-014; produção transacional (outbox) e DLQ funcionais.

## Criterios de aceite
- [ ] Tópicos consumidos/produzidos configurados (via `${VAR}`).
- [ ] Outbox publica somente após commit; rollback não emite.
- [ ] Falha persistente roteia para a DLQ após os retries.

## Dependencias
- INT-JRNY-001 (infra)

## Estimativa
M

## Prioridade
P6
