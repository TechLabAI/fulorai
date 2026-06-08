# COMM-014 -- Messaging: producers (outbox) + consumers + ingestão de webhook

## Contexto
Mensageria Kafka: publicação via outbox, consumo idempotente de eventos e ingestão de callbacks
de provedor que avançam a máquina de entrega.

## Spec de referencia
- SPEC-09-messaging-architecture
- SPEC-05-idempotency-concurrency

## Escopo
- Producers `journey-os.mensagem.{enfileirada,enviada,entregue,falhada}` via `EventPublisherPort` (outbox).
- Consumers: `ModeloAcessoAlteradoConsumer`, `EmpresaProvisionadaConsumer`, `AssetVersaoPublicadaConsumer`, `LeadSegmentoAlteradoConsumer` (idempotentes).
- `RegistrarEventoEntregaService` (webhook → `EventoEntrega` → transição ENTREGUE/LIDA/FALHADA + evento).
- DLQ após 3 retentativas (1s/5s/30s).
- Gatilhos JRNY/SALE (lead.roteado/estagio.transicionado/oportunidade.estagio.alterado) adicionados quando os nomes forem pinados.

## Resultado esperado
Eventos publicados/consumidos com idempotência; callbacks de provedor atualizam o ciclo de vida.

## Criterios de aceite
- [ ] Evento publicado só após commit (outbox); sem evento fantasma em rollback.
- [ ] Consumer reentregue → no-op (`processed_events`).
- [ ] Webhook `ENTREGUE` → estado ENTREGUE + `journey-os.mensagem.entregue`.

## Dependencias
- COMM-006 (precede)
- INT-COMM-005 (Kafka)

## Estimativa
L

## Prioridade
P6
