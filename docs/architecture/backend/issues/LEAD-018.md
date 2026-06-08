# LEAD-018 -- BDD end-to-end (Cucumber): capture, qualification, maturity score

## Contexto
Implementar os step definitions e fechar o golden path end-to-end com Cucumber + Testcontainers,
cobrindo as cláusulas SHALL (gate D-218).

## Spec de referencia
- SPEC-08-bdd-test-scenarios
- SPEC-02, SPEC-03

## Escopo
- Implementar steps dos `.feature`: `lead-capture`, `lead-qualification`, `maturity-score`.
- `CucumberSpringContext` + `application-bdd.properties`; PostgreSQL via singleton Testcontainer.
- Stubs (WireMock) para WRKS AccessDecision e TechLab AI (disponível/indisponível).
- Asserts em eventos publicados (broker de teste / tabela outbox).

## Resultado esperado
Cenários BDD passam cobrindo o golden path e os caminhos de borda (dedup, fallback IA, cross-empresa).

## Criterios de aceite
- [ ] ≥1 cenário BDD por cláusula SHALL de SPEC-01..06 e SPEC-09 (gate D-218).
- [ ] `:lead-service:integrationTest` (Cucumber) PASS.
- [ ] Sem `@Testcontainers`/`@Container` — padrão singleton (static initializer).
- [ ] Cenários de fallback da TechLab AI e cross-empresa cobertos.

## Dependencias
- LEAD-004..016 (funcionalidade implementada)

## Estimativa
L

## Prioridade
P8
