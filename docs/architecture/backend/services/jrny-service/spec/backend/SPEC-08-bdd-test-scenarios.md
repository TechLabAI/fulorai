# SPEC-08 — BDD Test Scenarios

> Companion to `tests/cucumber/*.feature` (pure Gherkin). Documents reusable steps, example
> data and the SHALL→scenario mapping (gate D-218). ADR-005. EARS guide:
> `docs/architecture/backend/standards/ears-notation.md`.

## Objetivo

Garantir que 100% das cláusulas SHALL das specs viram cenário BDD executável (Cucumber +
Testcontainers), e centralizar steps reutilizáveis e dados de exemplo.

## Feature files

- `journey-creation.feature` — Journey Builder CRUD + publicação + versionamento + tenant isolation (SPEC-01/03/06).
- `routing-decision.feature` — avaliação determinística, prioridade, assist IA (USADO/IGNORADO/INDISPONIVEL), NAO_ROTEADO, SEM_MUDANCA, decision log imutável, idempotência (SPEC-02/05/09).
- `stage-transition.feature` — avanço, estágio terminal → jornada.concluida, re-roteamento por score/segmento, refresh de conteúdo, cross-empresa guard, decision log (SPEC-02/03/06/09).

## Reusable steps (glue)

| Step | Significado |
|---|---|
| `Given an active empresa "<slug>" with provisioned schema` | prepara tenant (Testcontainers + migrations) |
| `Given an authenticated user "<u>" with permission(s) "<perms>"` | stub de AccessDecision (WRKS) |
| `Given a published journey "<nome>" with stages "<csv>"` | fixture de jornada PUBLICADA |
| `Given a rule with priority <p> routes to "<estagio>" when "<expr>"` | fixture de regra_roteamento |
| `Given TechLab AI orchestration is available/unavailable` | stub/circuit do TechLabAiClient |
| `When a "<evento>" event arrives for lead "<id>" with score <s> ...` | injeta evento LEAD no consumer |
| `Then a decisao_roteamento is written with result "<resultado>"` | verifica decision log |
| `Then a "<evento>" event is emitted/enqueued` | verifica outbox/tópico |

## Example data

- Tipos de estágio: `CAPTURA, NUTRICAO, QUALIFICACAO, OFERTA, FECHAMENTO, POS_VENDA`.
- Estados de jornada: `RASCUNHO, PUBLICADA, ARQUIVADA`. Estados de inscrição: `ATIVA, CONCLUIDA, ENCERRADA`.
- `assist_ia`: `USADO, IGNORADO, INDISPONIVEL`. `resultado`: `ROTEADO, SEM_MUDANCA, NAO_ROTEADO`.
- Campos de `condicao` (de LEAD): `scoreAgregado`, `dimensoes.{PERFIL,ENGAJAMENTO,INTENCAO,CAPACIDADE,URGENCIA,ADERENCIA}`, `estadoQualificacao`, `segmentoId`.
- Usuários: `marina` (HEAD_GROWTH, desenho), `rafael` (INFOPRODUTOR, publicação), `lucas` (SDR, leitura).

## SHALL → scenario mapping (D-218)

Toda cláusula SHALL em SPEC-01..07/09/10 e nos `contracts/*` mapeia para ≥1 `Scenario`. A geração
mecânica (`be-spec-to-bdd.py`) é executada em A3 (specs-validate); o gate de compilação/execução
roda após o scaffold (A5.bdd-gate).

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL have at least one BDD scenario for every SHALL clause across the spec set.`
- `WHEN the BDD suite runs, THE SYSTEM SHALL execute scenarios against a Testcontainers PostgreSQL with the tenant schema migrated.`
- `THE SYSTEM SHALL stub TechLab AI, WRKS and ASST in BDD (no external network dependency).`
- `THE SYSTEM SHALL inject LEAD domain events directly into the consumer in BDD rather than depending on a running LEAD service.`
