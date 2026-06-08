# JRNY-006 -- Eventos de roteamento (outbox) + Routing Query API (estado/decisões do lead)

## Contexto
Fecha o golden path: emite o evento-âncora `journey-os.lead.roteado` (+ `estagio.transicionado` /
`jornada.concluida`) via outbox após o commit, e expõe a consulta do estado de jornada e do
decision log do lead (`/api/v1/routing/**`), consumida por COMM/SALE.

## Spec de referencia
- SPEC-02-routing-engine-orchestration
- SPEC-01-api-surface
- SPEC-09-messaging-architecture

## Escopo
- Producer (outbox): `LeadRoteado` (somente em `ROTEADO`, carrega `decisaoId`/`assistIa`),
  `EstagioTransicionado`, `JornadaConcluida`. `JornadaPublicada` ligado ao publish (JRNY-003).
- `RoteamentoQueryService`: `findLeadJourney` (`GET /leads/{leadId}/journey` → `InscricaoJornadaResponse`),
  `listLeadDecisions` (`GET /leads/{leadId}/decisions` → page, mais recentes primeiro, inclui SEM_MUDANCA/NAO_ROTEADO).
- `RoutingQueryController` + DTOs; 404 `jrny.inscricao.nao-encontrada` quando não há inscrição.
- Guard de tenant em toda leitura (nunca retorna inscrição/decisão de outra empresa).

## Resultado esperado
Consumidores reagem ao `lead.roteado`; operadores/serviços leem "em que estágio o lead está e por quê".

## Criterios de aceite
- [ ] `ROTEADO` emite `lead.roteado` após commit (outbox); `SEM_MUDANCA`/`NAO_ROTEADO` não emitem.
- [ ] Estágio terminal emite `jornada.concluida` e inscrição fica `CONCLUIDA`.
- [ ] `GET /leads/{id}/decisions` retorna decisões em ordem decrescente de `decididoEm`.
- [ ] Nenhuma leitura cruza empresa.

## Dependencias
- JRNY-005 (precede)

## Estimativa
L

## Prioridade
P2
