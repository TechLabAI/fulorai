# COMM-016 -- BDD end-to-end (Cucumber: 3 features)

## Contexto
Cobertura BDD do gate D-218: toda cláusula SHALL das specs vira cenário executável.

## Spec de referencia
- SPEC-08-bdd-test-scenarios
- SPEC-01..SPEC-10 (cobertura cruzada)

## Escopo
- Implementar step defs das 3 features: `message-dispatch`, `template-rendering`, `channel-routing`.
- Harness Cucumber + `CucumberSpringContext` + `application-bdd.properties` (gerado em A5/scaffold).
- Testcontainers (PostgreSQL); adapters de provedor e TechLab AI stubbados.
- Estado inicial: cenários `pending` → implementados até `passing`.

## Resultado esperado
Suite BDD verde cobrindo golden path, roteamento/fallback, idempotência, Studio e segurança.

## Criterios de aceite
- [ ] `:comm-service:test --tests "*CucumberIT*"` executa as 3 features.
- [ ] ≥ 1 cenário por cláusula SHALL (gate D-218).
- [ ] 0 `failed` ao final (todos `passing`).

## Dependencias
- COMM-006, COMM-009, COMM-010, COMM-012, COMM-013, COMM-014 (precedem)

## Estimativa
L

## Prioridade
P8
