# INTL-013 -- Messaging: consumers + producer (outbox)

## Contexto
Consumo transversal de eventos e publicação do evento-âncora.

## Spec de referência
- SPEC-09, `contracts/event-contracts.md`

## Escopo
Consumers idempotentes (`AssetVersaoPublicadaConsumer`, `EmpresaProvisionadaConsumer`,
`ModeloAcessoAlteradoConsumer`) com dedupe por `eventId`; producer `CopilotRespostaGerada` via
outbox (consistência com a persistência). Envelope canônico (`empresa`/`correlationId`). DLQ de
mensageria após retries.

## Resultado esperado
Eventos consumidos/publicados de forma idempotente e consistente.

## Critérios de aceite
- [ ] Reentrega de `eventId` → no-op
- [ ] `copilot.resposta.gerada` publicado exatamente uma vez (outbox)
- [ ] `empresa.provisionada` → seed idempotente da base
- [ ] `modelo.acesso.alterado` → invalida cache AccessDecision

## Dependências
- INTL-005, INTL-011, INTL-012 (precedem)

## Estimativa
L

## Prioridade
P6
