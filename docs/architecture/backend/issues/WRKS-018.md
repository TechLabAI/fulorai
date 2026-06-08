# WRKS-018 -- BDD end-to-end (step defs Cucumber das 4 features)

## Contexto
Implementar os step definitions que tornam executáveis os cenários BDD derivados das specs EARS
(gate D-218), saindo do estado `pending` para `passing`.

## Spec de referencia
- SPEC-08-bdd-test-scenarios
- (todas as SPEC-01..10 via cláusulas SHALL)

## Escopo
- `WrksStepDefs` + `CucumberSpringContext` + `application-bdd.properties`.
- Implementar steps das features: `login-and-session`, `access-decision`,
  `workspace-provisioning`, `user-administration`.
- Testcontainers singleton (PostgreSQL/Redis/Kafka) via static initializer (nunca `@Container`).
- Keycloak/MIG stub (WireMock); `spring-security-test` para `jwt()` post-processor.

## Resultado esperado
26 cenários executam: 0 failed; cobertura de toda cláusula SHALL.

## Criterios de aceite
- [ ] `:wrks-service:test --tests "*CucumberIT*"` → 0 failed.
- [ ] 1 cenário por cláusula SHALL (gate D-218).
- [ ] Testcontainers singleton (sem `@Container`).

## Dependencias
- WRKS-004..016 (implementação coberta pelos cenários)

## Estimativa
L

## Prioridade
P8
