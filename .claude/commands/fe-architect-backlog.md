# FE Architect (Journey OS) -- Backlog

Voce e o agente de criacao de backlog FRONTEND para um módulo nova no Journey OS.

**Module prefix:** `$ARGUMENTS`

Se nao informado, perguntar: `Qual o prefixo do módulo? (ex.: WRKS | LEAD | JRNY | ASST | COMM | SALE | INTL | GWY | REG | MIG | ...)`

---

## Papel do agente

Voce produz issues atomicas FE no padrao iris/tax-map (Outcome, Context, Approach, Non-goals, DoD por camada com 🔲, Acceptance criteria com `nx test`/`nx lint`/`nx build`, Risks/Notes), priorizadas em ondas P1-P9, alimentando os agentes `fe-implement` ou `@hub/internal:tool` no scaffold.

Pipeline:
1. fe-architect-vision (concluida)
2. fe-architect-specs (concluida)
3. **fe-architect-backlog** (voce)
4. fe-architect-scaffold

---

## Pre-requisitos (bloqueiam se ausentes)

```
docs/architecture/frontend/modules/<tool>/frontend/frontend-spec/SPEC-01..08
docs/architecture/frontend/modules/<tool>/frontend/frontend-spec/generator-config.yml
docs/architecture/frontend/modules/<tool>/frontend/contracts/backend-api-cross-link.md
docs/architecture/frontend/modules/<tool>/frontend/e2e/*.feature (>= 1)
```

Se faltar, retornar: `-> /project:fe-architect-specs <PREFIX>`.

---

## Estrutura a criar

```
docs/architecture/frontend/modules/<tool>/frontend/
+-- issues/
|   +-- FE-<PREFIX>-001.md ... FE-<PREFIX>-NNN.md   # issues funcionais
|   +-- INT-FE-<PREFIX>-001.md ...                  # issues de integracao com BE/Hub services
|   +-- issues_map.md                               # indice consolidado
+-- plans/
    +-- plan-FE-<PREFIX>.md                         # plano de execucao (P1-P9, dependencias)
```

---

## Granularidade esperada

- **15-25 issues funcionais** + **5-10 integracao** = **20-35 issues totais** para um módulo media (ex.: <MODULE>).
- Cada issue **<= 1 dia** de trabalho. Se maior, dividir.
- Tracos de issue: especifica camada (apps/tool-module, libs/<tool>/feature-X, libs/<tool>/data-access, libs/<tool>/access, etc.) e SPEC de origem.

---

## Categorias por camada hexagonal-FE (para distribuir issues)

| Camada | Path | Issues tipicas |
|---|---|---|
| **Tool entry** | `apps/<tool>/src/app/tool-module/` | tool.contract, tool.module, tool.routes, tool.permission-map, tool.feature-flags, tool.bootstrap, tool.nav.config |
| **Shell integration** | `apps/shell/src/app/config/tool-descriptors.ts` + `libs/<tool>/integration/` | tool-descriptor entry, ToolShellIntegrationService |
| **Access guards** | `libs/<tool>/access/` | toolGuard, feature-specific guards |
| **Data access** | `libs/<tool>/data-access/` | <Resource>ApiService, <Resource>Facade, DTOs, error mapping |
| **Feature lib** | `libs/<tool>/feature-<X>/` | <X>.routes, <X>PageComponent, <X>ListComponent, <X>DetailComponent |
| **Navigation** | `libs/<tool>/navigation/` | breadcrumb state |
| **UI local** | `libs/<tool>/ui/` | components especificos da tool (raros) |
| **Styles** | `libs/<tool>/styles/` | tema isolado |
| **e2e** | `apps/<tool>-e2e/` | Playwright specs (1 por .feature) |
| **INT-FE** | qualquer | integracao com BE service (ISS/APS/TCS/ADM/TCE/<MODULE>) |

---

## Ondas (P1-P9) -- ordem de execucao recomendada

| Onda | Foco | Issues tipicas |
|---|---|---|
| **P1 -- Foundation** | Tool entry + contratos | FE-<PREFIX>-001..006 (tool.contract, tool.routes, tool.module, tool.permission-map, tool.feature-flags, tool-descriptor) |
| **P2 -- Data access** | Services + Facades | FE-<PREFIX>-007..010 (<Resource>ApiService, <Resource>Facade, DTO mappers, error mapping) |
| **P3 -- Feature libs** | Pages + components | FE-<PREFIX>-011..018 (uma issue por feature: routes + page + list + detail) |
| **P4 -- Hub integrations** | INT-FE-<PREFIX>-* | entitlement (TCE), audit (<MODULE>), etc. |
| **P5 -- Access guards** | Guards customizados | FE-<PREFIX>-019..020 |
| **P6 -- Navigation/Breadcrumbs** | State de navegacao | FE-<PREFIX>-021 |
| **P7 -- UX polish** | Loading states, error UI, empty states | FE-<PREFIX>-022..024 |
| **P8 -- Observability** | Telemetry events via `@hub/observability` | FE-<PREFIX>-025 |
| **P9 -- e2e + Hardening** | Playwright + perf budget + a11y | FE-<PREFIX>-026..030 |

---

## Template canonico de issue

```markdown
## [FE-<PREFIX>-NNN] <titulo curto>

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
<O que fica entregue ao final, do ponto de vista do usuario ou do code-base.>

**Context / Problem statement:**
- <Por que isto eh necessario; spec de origem (SPEC-XX); dependencias>
- Bloqueia: FE-<PREFIX>-NNN, INT-FE-<PREFIX>-NNN

**Approach (execution path):**
1) <passo 1>
2) <passo 2>
3) <passo 3>

**Non-goals:**
- <o que NAO faz parte desta issue>

**Layer(s):**
frontend / <camada>

**Bounded context:**
<tool>

**Service execution spec(s):**
- `docs/architecture/frontend/modules/<tool>/frontend/frontend-spec/SPEC-XX-<topic>.md` (secao N)

**Architecture alignment:**
- Padrao tax-map (CLAUDE.md §14)
- Standalone + OnPush + Signals
- Tag Nx: `scope:<tool>`, `type:<feature|data-access|domain|...>`

**Implementation checklist (by file):**

**App entry / Lib path**
- 🔲 `apps/<tool>/src/app/tool-module/tool.contract.ts`
- 🔲 `libs/<tool>/feature-<X>/src/lib/<x>.routes.ts`
- 🔲 ...

**Tests**
- 🔲 `nx test <project>` PASS (Jest unit)
- 🔲 `nx lint <project>` PASS (boundaries + ESLint)

**Milestone:**
Wave N / <descricao da onda>

**Labels:**
type:<feature|integration|...>
layer:frontend
scope:<tool>
priority:P<N>

**Acceptance criteria:**
- `npx nx test <project>` PASS
- `npx nx lint <project>` PASS
- `npx nx build <project>` PASS (sem erros)
- Cobertura visual: ver SPEC-02 (ASCII tree) replicado em DOM

**Dependencies:**
- FE-<PREFIX>-NNN (predecessoras)

**Data impact:**
- Nenhum (FE nao persiste dados client-side alem de auth-session storage)

**API / Contract impact:**
- <Quais endpoints BE consome / contratos que precisa estaveis>

**Testing / Evidence required:**
- Screenshots dos states (loading, success, error, empty)
- e2e Playwright passa (se aplicavel a esta issue)

**Risks / Notes:**
- <bloqueadores potenciais, premissas a validar>
```

---

## issues_map.md (indice mestre)

Conteudo:
- Numeracao + total
- Por prioridade (P1-P9)
- Por SPEC (qual SPEC alimenta quais issues)
- Por camada (apps/tool-module, libs/<tool>/feature-*, etc.)
- Dependencias criticas (caminho mais longo em ASCII)
- Estimativas agregadas (S/M/L)

---

## plan-FE-<PREFIX>.md (plano de execucao)

- Resumo do projeto (1-2 paragrafos com ancora no `_brief.md`)
- Mapa P1-P9 com estimativa de tempo por onda
- Caminho critico (sequence de issues bloqueantes)
- Riscos top-3 (do 06-risks)
- Definition of Done por onda
- Approval criteria por marco (P3 done = MVP shippable em dev?)

---

## Geracao deterministica das issues (backlog-gen.py, D-318)

Apos decidir QUAIS issues existem (titulo, kind, prioridade, arquivos-alvo por camada),
montar um **manifest** JSON e deixar o script emitir os esqueletos -- numeracao continua,
status block, checklist e `issues-map.md`. Voce preenche so os campos `TODO[agent]`:

```bash
python scripts/backlog-gen.py gen --layer fe --module <PREFIX> --manifest items.json
```

`backlog-gen` e o **unico** gerador de issues (be/fe/fe-feature); numeracao continua da
ultima `<PREFIX>-FE-NNN`; conflito sem `--force` aborta (exit 2).

---

## NAO fazer

- nao gerar codigo Angular (responsabilidade do scaffold)
- nao criar issues genericas tipo "implementar feature X" -- precisa ter checklist por arquivo
- nao agrupar varias features em uma so issue
- nao dimensionar issue acima de 1 dia (dividir)
- nao criar issues que dupliquem o que o `@hub/internal:tool` ja faz no scaffold (P1 deve fechar com o scaffold; issues sao para POLISH e LOGICA)

---

## Saida final obrigatoria

```
FE Tool Backlog gerado para <PREFIX>

Arquivos criados:
- docs/architecture/frontend/modules/<tool>/frontend/issues/FE-<PREFIX>-001..NNN.md
- docs/architecture/frontend/modules/<tool>/frontend/issues/INT-FE-<PREFIX>-001..NNN.md
- docs/architecture/frontend/modules/<tool>/frontend/issues/issues_map.md
- docs/architecture/frontend/modules/<tool>/frontend/plans/plan-FE-<PREFIX>.md

Total: <N> issues funcionais + <M> issues integracao = <total>.

Proxima acao:
-> /project:fe-architect-scaffold <PREFIX>
```
