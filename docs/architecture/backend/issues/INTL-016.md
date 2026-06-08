# INTL-016 -- BDD end-to-end (Cucumber)

## Contexto
Validar o comportamento completo via os cenários BDD autorais.

## Spec de referência
- SPEC-08, features `ai-copilot`/`knowledge-base`/`event-platform-analytics`

## Escopo
Implementar step definitions e harness (CucumberSpringContext, `application-bdd.properties`) e
fazer os 19 cenários passarem (de `pending` a green), incluindo isolamento cross-tenant,
idempotência e degradação.

## Resultado esperado
`./gradlew :services:intl-service:test --tests "*CucumberIT*"` verde.

## Critérios de aceite
- [ ] 3 status do copiloto cobertos e verdes
- [ ] Cenário de isolamento cross-tenant verde (falha se vazar)
- [ ] Cenários de idempotência (evento/projeção/asset) verdes
- [ ] DLQ por rastreabilidade ausente verde

## Dependências
- INTL-005..014 (precedem)

## Estimativa
L

## Prioridade
P8
