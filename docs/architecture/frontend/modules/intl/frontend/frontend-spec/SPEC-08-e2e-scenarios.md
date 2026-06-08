# SPEC-08 — E2E Scenarios — INTL

> Cenários Gherkin (Playwright). Cada um vira um `.feature` em `frontend/e2e/`, copiado pelo
> gerador para `apps/intl-e2e/src/` como spec stub (`test.fixme`) no scaffold (A4). A execução real
> dos fluxos é feita em `/fe-implement` (P9).

## Cenários

| Arquivo `.feature` | Tipo | Cobre |
|---|---|---|
| `copilot-grounded-answer.feature` | happy path | perguntar → `RESPONDIDA` com citações clicáveis |
| `copilot-degraded-answer.feature` | error/degradação | `DEGRADADA` e `NAO_FUNDAMENTADA` sinalizados, sem citação fabricada |
| `knowledge-curation.feature` | happy + recovery | criar nó → indexar → `INDEXADO`; `503` → retry |
| `analytics-read.feature` | happy path | funil + uso do copiloto carregam read-only; filtro de período |
| `entitlement-denied.feature` | entitlement | rota/menu ocultos sem permissão; `403` em runtime |
| `empresa-switch-isolation.feature` | isolamento | trocar empresa limpa conversa e recarrega listas (sem vazamento) |
| `deep-link.feature` | deep-link | abrir `/intl/knowledge/:id` direto resolve guards + breadcrumbs |

## Princípios de teste

- **Fundamentação:** o teste de `copilot-grounded-answer` asserta ≥1 chip de citação que resolve ao
  documento-fonte; o de `copilot-degraded-answer` asserta **ausência** de citação nos estados
  degradados (INV-FE-1).
- **Degradação não é erro:** nenhum cenário de IA off espera `5xx`/tela de erro — espera badge de
  estado.
- **Isolamento:** `empresa-switch-isolation` garante 0 vazamento cross-empresa na UI.
- **Acesso:** `entitlement-denied` valida que a UI é **ausente por decisão de acesso**, não escondida
  por convenção.

> Os 7 `.feature` estão em `frontend/e2e/` e listados no `generator-config.yml` (`e2e.features`).
