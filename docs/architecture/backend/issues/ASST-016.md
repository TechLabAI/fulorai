# ASST-016 -- BDD end-to-end (Cucumber)

## Contexto
Suíte BDD cobrindo criação, versionamento/Studio e workflow de aprovação, contra Testcontainers,
fechando o gate D-218 (toda SHALL → cenário).

## Spec de referencia
- SPEC-08-bdd-test-scenarios
- tests/cucumber/{asset-creation,asset-versioning,approval-workflow}.feature

## Escopo
- Implementar step defs dos 3 `.feature` (glue) + `CucumberSpringContext`.
- Stubs de TechLab AI e WRKS (sem rede externa); Testcontainers PostgreSQL com schema migrado.
- Cobrir todas as 125 cláusulas SHALL das specs/contracts.

## Resultado esperado
Cenários executáveis; gate de compilação + comportamento (pending→passing) verde.

## Criterios de aceite
- [ ] `:asst-service:integrationTest --tests "*CucumberIT*"` executa os 3 features.
- [ ] ≥1 cenário por cláusula SHALL.
- [ ] TechLab AI e WRKS stubados (sem dependência de rede).

## Dependencias
- ASST-006, ASST-009, ASST-012, ASST-014 (golden path + integrações)

## Estimativa
L

## Prioridade
P8
