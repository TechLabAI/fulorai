# SPEC-08 — BDD Test Scenarios

> Companion to `tests/cucumber/*.feature` (pure Gherkin). Documents reusable steps, example
> data and the SHALL→scenario mapping (gate D-218). EARS guide linkado.

## Objetivo

Garantir que 100% das cláusulas SHALL das specs viram cenário BDD executável (Cucumber +
Testcontainers), e centralizar steps reutilizáveis e dados de exemplo.

## Feature files

- `asset-creation.feature` — CRUD + catálogo + tenant isolation (SPEC-01/06).
- `asset-versioning.feature` — versão imutável + Asset Studio + idempotência (SPEC-02/03/05).
- `approval-workflow.feature` — máquina de estados + eventos + consumo cross-módulo (SPEC-02/09).

## Reusable steps (glue)

| Step | Significado |
|---|---|
| `Given an active empresa "<slug>" with provisioned schema` | prepara tenant (Testcontainers + migrations) |
| `Given an authenticated user "<u>" with permission(s) "<perms>"` | stub de AccessDecision (WRKS) |
| `Given an asset "<titulo>" of type "<tipo>" in state "<estado>"` | fixture de asset |
| `Given TechLab AI document_composition is available/unavailable` | stub/circuit do TechLabAiClient |
| `When <user> composes in the Studio with ...` | chama `/studio/compose` |
| `Then a "<evento>" event is emitted/enqueued` | verifica outbox/tópico |

## Example data

- Tipos: `LANDING_PAGE, EMAIL, CRIATIVO, ROTEIRO, DOCUMENTO, SCRIPT_SDR`.
- Estados: `RASCUNHO, EM_REVISAO, APROVADO, PUBLICADO, REJEITADO, ARQUIVADO`.
- Usuários: `marina` (HEAD_GROWTH, autoria), `rafael` (INFOPRODUTOR, aprovação/publicação).

## SHALL → scenario mapping (D-218)

Toda cláusula SHALL em SPEC-01..07/09/10 e nos `contracts/*` mapeia para ≥1 `Scenario`. A
geração mecânica (`be-spec-to-bdd.py`) é executada em A3 (specs-validate); o gate de
compilação/execução roda após o scaffold (A5.bdd-gate).

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL have at least one BDD scenario for every SHALL clause across the spec set.`
- `WHEN the BDD suite runs, THE SYSTEM SHALL execute scenarios against a Testcontainers PostgreSQL with the tenant schema migrated.`
- `THE SYSTEM SHALL stub TechLab AI and WRKS in BDD (no external network dependency).`
