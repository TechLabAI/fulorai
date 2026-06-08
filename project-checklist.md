# Journey OS — Checklist

> Progresso do projeto. Setup (ETAPA 1) é sincronizado de `project-context.json` via `scripts/checklist.py sync`.

## ETAPA 1 — Setup

### P0 — Repository bootstrap (minimal structure + git init)
- [x] Repository bootstrap (minimal structure + git init) (`new-project.py bootstrap`)

### P1 — Copy .claude/ + generated CLAUDE.md
- [x] Copy .claude/ + generated CLAUDE.md (`new-project.py claude-folder`)

### P2 — Create docs/architecture/ per rigor level
- [x] Create docs/architecture/ per rigor level (`new-project.py docs-skeleton --rigor complete-bosq`)

### P3 — Sync TechLab AI docs snapshot (docs-only) and populate integration contract  _(condicional: ai.hasAi == true)_
- [ ] Sync TechLab AI docs snapshot (docs-only) and populate integration contract (`sync-techlab-ai.py --target-sha <pinned>`)

### P3b — Generate elastic-stack overlay (compose + integration contract + Java ports/adapters)  _(condicional: stack.elastic.enabled == true)_
- [x] Generate elastic-stack overlay (compose + integration contract + Java ports/adapters) (`new-project.py backend-skeleton (elastic-stack overlay triggered automatically)`)

### P4 — backend/ Gradle root + empty settings.gradle.kts
- [x] backend/ Gradle root + empty settings.gradle.kts (`new-project.py backend-skeleton`)

### P5 — frontend/ empty Nx workspace  _(condicional: stack.frontend.enabled == true)_
- [x] frontend/ empty Nx workspace (`new-project.py frontend-skeleton`)

### P6 — Handoff message: setup done, next step is /be-architect-vision <MODULE>
- [x] Handoff message: setup done, next step is /be-architect-vision <MODULE>

## ETAPA 2 — Desenvolvimento

### Módulos backend

#### WRKS — Workspace & Identity (`wrks-service`)
- [ ] **Arquitetura** — `/be-architect-vision WRKS` → specs → backlog → scaffold
- [ ] **Ciclo de desenvolvimento** — `/be-validator WRKS` → planner → implement
- **Status atual:** declared

#### LEAD — Lead Intelligence & Qualification (`lead-service`)
- [ ] **Arquitetura** — `/be-architect-vision LEAD` → specs → backlog → scaffold
- [ ] **Ciclo de desenvolvimento** — `/be-validator LEAD` → planner → implement
- **Status atual:** declared

#### JRNY — Journey & Routing (`jrny-service`)
- [ ] **Arquitetura** — `/be-architect-vision JRNY` → specs → backlog → scaffold
- [ ] **Ciclo de desenvolvimento** — `/be-validator JRNY` → planner → implement
- **Status atual:** declared

#### ASST — Asset Hub (`asst-service`)
- [ ] **Arquitetura** — `/be-architect-vision ASST` → specs → backlog → scaffold
- [ ] **Ciclo de desenvolvimento** — `/be-validator ASST` → planner → implement
- **Status atual:** declared

#### COMM — Communication Hub (`comm-service`)
- [ ] **Arquitetura** — `/be-architect-vision COMM` → specs → backlog → scaffold
- [ ] **Ciclo de desenvolvimento** — `/be-validator COMM` → planner → implement
- **Status atual:** declared

#### SALE — Sales & Revenue (`sale-service`)
- [ ] **Arquitetura** — `/be-architect-vision SALE` → specs → backlog → scaffold
- [ ] **Ciclo de desenvolvimento** — `/be-validator SALE` → planner → implement
- **Status atual:** declared

#### INTL — Intelligence & Platform (`intl-service`)
- [ ] **Arquitetura** — `/be-architect-vision INTL` → specs → backlog → scaffold
- [ ] **Ciclo de desenvolvimento** — `/be-validator INTL` → planner → implement
- **Status atual:** declared
