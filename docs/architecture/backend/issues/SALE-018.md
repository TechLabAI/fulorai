# SALE-018 — BDD end-to-end (Cucumber)

## Contexto
Implementar os step definitions e tornar verdes (ou pending→passing) os 3 features autorais,
cobrindo as cláusulas SHALL.

## Spec de referencia
- SPEC-08, `tests/cucumber/*.feature`

## Escopo
Steps para `sales-pipeline`, `purchase-revenue`, `revenue-attribution`; CucumberIT + Testcontainers
(Postgres + Kafka); cobertura D-218 (toda SHALL → cenário).

## Resultado esperado
Suíte BDD executável e verde.

## Criterios de aceite
- [ ] 3 features executam contra Testcontainers
- [ ] cenários de idempotência/conservação/determinismo passam
- [ ] cobertura de 100% das cláusulas SHALL (gate D-218)

## Dependencias
- SALE-006, SALE-007, SALE-008, SALE-016 (precede)

## Estimativa
L

## Prioridade
P8
