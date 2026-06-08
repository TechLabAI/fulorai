# INT-WRKS-001 -- Discovery via Eureka (REG)

## Contexto
Registro do `wrks-service` no Eureka para descoberta por GWY e demais serviços.

## Spec de referencia
- integration-contracts.md
- hub-integration.md

## Escopo
- Eureka client (`EUREKA_SERVICE_URL`), `spring.application.name=wrks-service`.
- Health indicator integrado ao status do Eureka.

## Resultado esperado
Serviço aparece no dashboard do Eureka e é descoberto por `lb://wrks-service`.

## Criterios de aceite
- [ ] Registro no Eureka visível.
- [ ] Descoberta funcional por GWY (rota `/api/v1/iam/**`).

## Dependencias
- REG (existente)

## Estimativa
S

## Prioridade
P1
