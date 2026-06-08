# SPEC-08 — BDD Test Scenarios

> Features Gherkin: `tests/cucumber/{ai-copilot,knowledge-base,event-platform-analytics}.feature`.
> Geração de step stubs: `be-spec-to-bdd.py` / `be-bdd-generator.py`.

## Objetivo

Mapear as features Cucumber, steps reutilizáveis e dados de exemplo que validam os critérios EARS.

## Features

| Feature | Cobre | SPEC |
|---|---|---|
| `ai-copilot.feature` | resposta fundamentada/nao_fundamentada/degradada, isolamento, custo, 404 | SPEC-02, SPEC-06 |
| `knowledge-base.feature` | criar/indexar/editar/arquivar nó, ingestão por asset, idempotência, 503 | SPEC-03, SPEC-05 |
| `event-platform-analytics.feature` | DLQ, idempotência de projeção, descentralização, filtro de empresa, seed | SPEC-03, SPEC-05 |

## Steps reutilizáveis (documentar; não duplicar nos `.feature`)

- `Given uma empresa "<slug>" provisionada [com base de conhecimento]`
- `Given um usuário autenticado com a permissão "<perm>"`
- `Given a TechLab AI está disponível|indisponível [para gerar embedding]`
- `Given existem nós de conhecimento [indexados] relevantes à pergunta`
- `When o usuário pergunta "<texto>"` / `When o usuário cria|indexa|edita|arquiva um nó`
- `When o evento "<tipo>" é consumido|reentregue [para "<ref>"]`
- `Then a resposta tem status "<STATUS>"` / `Then o serviço responde <codigo>`
- `Then um documento é projetado no índice "<indice>" com o bloco de rastreabilidade`
- `Then um evento "<tipo>" é publicado`

## Dados de exemplo

- Empresas: `acme` (solicitante), `globex` (isolamento cross-tenant).
- Asset ref: `asset-123:2`.
- Permissões: `intl.copilot.use`, `intl.knowledge.write`, `intl.analytics.read`.

## Critérios de aceite (EARS)

- THE SYSTEM SHALL ter cenários cobrindo os três status do copiloto (`RESPONDIDA`, `NAO_FUNDAMENTADA`, `DEGRADADA`).
- THE SYSTEM SHALL ter um cenário de isolamento cross-tenant que falha se houver vazamento.
- THE SYSTEM SHALL ter cenários de idempotência (evento reentregue, projeção reprocessada, asset reentregue).
- WHEN o harness BDD roda no scaffold, THE SYSTEM SHALL apresentar os cenários como `pending` (0 `failed`) antes da implementação.
