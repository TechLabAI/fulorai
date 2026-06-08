# INT-JRNY-006 -- JourneyQueryClient (contrato de leitura provido a COMM/SALE)

## Contexto
JRNY **provê** o contrato de leitura do estado de jornada do lead para COMM/SALE
(`@FeignClient(name="jrny-service")` `JourneyQueryClient`), consumido a partir da Routing Query API.

## Spec de referencia
- hub-integration.md
- SPEC-01-api-surface
- integration-contracts.md

## Escopo
- Estabilizar o contrato exposto por `GET /api/v1/routing/leads/{leadId}/journey` (e `/decisions`)
  como superfície de leitura consumível por COMM/SALE.
- DTO de contrato estável (`InscricaoJornadaResponse`) — nunca expõe `@Entity`.
- Documentar no `hub-integration.md`/services-catalog o `JourneyQueryClient` (já registrado no §7).
- Garantir guard de tenant e versionamento do contrato de leitura.

## Resultado esperado
COMM/SALE leem deterministicamente "em que estágio o lead está" via contrato estável, sem conhecer o motor interno.

## Criterios de aceite
- [ ] Endpoint de leitura retorna `InscricaoJornadaResponse` estável (sem entity).
- [ ] Contrato documentado e registrado no Feign Registry.
- [ ] Leitura respeita o isolamento por empresa.

## Dependencias
- JRNY-006 (Routing Query API)

## Estimativa
S

## Prioridade
P6
