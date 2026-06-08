# INT-ASST-001 -- Discovery via Eureka (REG)

## Contexto
Registro do `asst-service` no Eureka para descoberta por GWY e pelos consumidores (COMM/JRNY/SALE).

## Spec de referencia
- integration-contracts.md
- hub-integration.md

## Escopo
- Eureka client (`EUREKA_SERVICE_URL`), `spring.application.name=asst-service`.
- Health indicator integrado ao status do Eureka.

## Resultado esperado
Serviço aparece no dashboard do Eureka e é descoberto por `lb://asst-service`.

## Criterios de aceite
- [ ] Registro no Eureka visível.
- [ ] Descoberta funcional por GWY (rota `/api/v1/assets/**`).

## Dependencias
- REG (existente)

## Estimativa
S

## Prioridade
P1
