# JRNY-016 -- BDD end-to-end (journey-creation, routing-decision, stage-transition; gate D-218)

## Contexto
Materializa os cenários Cucumber autorais em testes executáveis cobrindo as cláusulas SHALL das
specs (gate D-218). Três features: construção/publicação de jornada, decisão de roteamento e
transição de estágio.

## Spec de referencia
- SPEC-08-bdd-test-scenarios
- (cobre transversalmente SPEC-01..10)

## Escopo
- Wire dos 3 `.feature` (`journey-creation`, `routing-decision`, `stage-transition`) com step defs.
- `CucumberSpringContext` + `application-bdd.properties`; Testcontainers PostgreSQL com schema migrado.
- Stubs de WRKS (`AccessDecision`), ASST (`AssetQueryClient`) e TechLab AI (`orchestration`) — incluindo cenário de IA indisponível (fallback).
- ≥1 cenário por cláusula SHALL; cobre ROTEADO/SEM_MUDANCA/NAO_ROTEADO, fallback de IA, idempotência, cross-empresa, terminal→concluida.

## Resultado esperado
`*CucumberIT*` executa os 3 features com cenários verdes (ou `pending` no gate diferido pré-implementação), cobrindo o gate D-218.

## Criterios de aceite
- [ ] `:jrny-service:test --tests "*CucumberIT*"` executa os 3 features.
- [ ] Cada cláusula SHALL tem ≥1 cenário associado.
- [ ] Cenário de TechLab AI indisponível verifica fallback determinístico.
- [ ] Cenário cross-empresa garante isolamento.

## Dependencias
- JRNY-006, JRNY-009, JRNY-012, JRNY-014 (golden path + integrações + segurança + messaging)

## Estimativa
L

## Prioridade
P8
