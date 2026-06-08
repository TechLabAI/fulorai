# JRNY-014 -- Messaging: consumers (6 eventos) idempotentes + producers (4 eventos) via outbox

## Contexto
Implementa a malha de mensageria do JRNY: consome os gatilhos de LEAD/ASST/WRKS e publica os
eventos de roteamento. Consumers idempotentes (eventId), producers transacionais (outbox).

## Spec de referencia
- SPEC-09-messaging-architecture
- event-contracts.md

## Escopo
- Consumers: `LeadQualificadoConsumer` (gatilho de roteamento → `RotearLeadService`),
  `LeadScoreAtualizadoConsumer`, `LeadSegmentoAlteradoConsumer` (reavaliação),
  `AssetVersaoPublicadaConsumer` (refresh de referência), `ModeloAcessoAlteradoConsumer`
  (invalida cache AccessDecision), `EmpresaProvisionadaConsumer` (seed de jornadas default, idempotente).
- Producers (outbox): `JornadaPublicada`, `LeadRoteado`, `EstagioTransicionado`, `JornadaConcluida`.
- Tenant do envelope fixado antes de processar; sem chamada Feign síncrona dentro do consumer crítico.
- Reavaliação por score/segmento: regra dispara → reroteia (decisão + evento); senão `SEM_MUDANCA`.

## Resultado esperado
Roteamento reativo end-to-end: eventos de LEAD entram, decisões saem; rollback nunca publica; reentrega é no-op.

## Criterios de aceite
- [ ] 6 consumers registrados e idempotentes (eventId).
- [ ] Rollback da transação não emite evento (outbox).
- [ ] `lead.score.atualizado` que dispara regra gera novo `lead.roteado`; senão grava `SEM_MUDANCA`.
- [ ] `empresa.provisionada` semeia jornadas default de forma idempotente.

## Dependencias
- JRNY-006 (eventos)
- INT-JRNY-005 (Kafka config)

## Estimativa
L

## Prioridade
P6
