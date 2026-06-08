# AI Framework — Consolidação de Melhorias (Journey OS)

> **O que é este documento.** O registro **único e canônico** de TODAS as melhorias feitas no
> *framework de IA* do Journey OS — os comandos `.claude/commands/*`, as skills, os geradores
> Python em `scripts/*`, o gerador Nx do FE, os gates e os artefatos de orquestração (autopilots,
> master-plans, checkpoints).
>
> **Por que existe.** As melhorias estavam dispersas em três fontes (`workflow-improvements.md`,
> `framework-improvements.md` do FE, e `_inbox/LEARNING-*`) + memórias do agente. Este arquivo
> consolida e indexa tudo, com o **estado real** de cada item. Os documentos de origem continuam
> válidos como detalhe profundo — aqui é o mapa.
>
> **Período coberto:** Fase 1 (Arquitetura) — primeira corrida real dos autopilots
> (`/be-architecture-autopilot` + `/fe-architecture-autopilot`) sobre os 10 módulos, **2026-06-04 a
> 2026-06-05**.
>
> **Legenda de status:** ✅ implementado · ⏭️ decidido NÃO fazer · ⏳ pendente · ℹ️ contextual (registrar, não consertar).

---

## 0. Sumário executivo — tabela mestra

| ID | Categoria | Melhoria | Status | Onde vive |
|----|-----------|----------|--------|-----------|
| **A1+A2+D3** | Toolchain | Preflight de toolchain + ledger de gates diferidos | ✅ | `scripts/preflight.py`, `scripts/be-gates-replay.py`, seção `## Ledger` nos master-plans |
| **A3** | Toolchain | Fail-fast em erro de sub-gerador (`--continue-on-error` opt-in) | ✅ | `scripts/be-module-generator.py` (`_invoke_subgen`) |
| **A4** | Toolchain | `specs-validate`: separar geração (A3) do gate (A5, pós-scaffold) | ✅ | `be-architecture-autopilot`, `be-spec-to-bdd.py` |
| **B1** | Geradores | Dedup `@Entity`: base canônica + gate config↔SQL | ✅ | `scripts/be-entity-generator.py`, `scripts/be-module-generator.py` |
| **B2** | Geradores | Convergir entity-gen para templates `.j2` (byte-parity) | ✅ | `templates/operational/code/java/eg-*.java.j2` |
| **C1** | Consistência | Schema de checkpoint unificado BE/FE (`progressUnit`) | ✅ | autopilots de execução (`be-autopilot`, `fe-autopilot`) |
| **C2** | Consistência | Migração de vocabulário `@hub`→`@journeyos` | ✅ | comandos, scripts, frontend, CLAUDE.md |
| **C3** | Consistência | Família `be-feature-architect-*` | ⏭️ | decisão registrada — BE usa validator/planner/implement |
| **C4** | Consistência | Gate EARS no FE | ✅ | `.claude/commands/fe-architect-specs-validate.md` |
| **D1** | Master-plan | Header "auto-gerenciado pelo autopilot" | ✅ | ambos os master-plans + geradores |
| **D2** | Master-plan | Atualizar master-plan por fase (ordem: checkpoint → master-plan) | ✅ | ambos os autopilots de arquitetura |
| **D3** | Master-plan | Ledger consolidado + comando de replay | ✅ | `scripts/be-gates-replay.py` (ver A1) |
| **F-AUTO** | Orquestração | Architecture Autopilots (meta-orquestradores Layer 1) | ✅ | `be-architecture-autopilot.md`, `fe-architecture-autopilot.md` |
| **F-MP** | Orquestração | Architecture Master-Plan (espelho global por camada) | ✅ | `docs/architecture/{backend,frontend}/plans/architecture-master-plan.md` |
| **F-CKPT** | Orquestração | Checkpoints em `tmp/` (crash-recovery + `--resume`) | ✅ | `tmp/*-architecture-autopilot/<MOD>/state.json` |
| **FE-1** | Framework FE | Vocabulário canônico `module/@journeyos/module-pattern` | ✅ | `standards/module-pattern.md` |
| **FE-2** | Framework FE | Gerador Nx local `@journeyos/internal:module` | ✅ | `frontend/libs/internal-nx-plugin/internal` |
| **FE-3** | Framework FE | Dev-deps consolidadas no `package.json` | ✅ | `frontend/package.json` |
| **FE-4** | Framework FE | 9 shared libs `@journeyos/shared/*` (Wave-0) | ✅ | `frontend/libs/shared/*` |
| **FE-5** | Framework FE | Shell `journey-os-web` promovido a app Nx | ✅ | `frontend/apps/journey-os-web` |
| **FE-6** | Framework FE | Module-entry como **library** (ADR-006) + gerador v3 | ✅ | `ADR-006-module-entry-as-library.md` |
| **TG-1** | Geradores | Bug `smart_query_methods` (TypeError 3º arg) | ✅ | `scripts/be-entity-generator.py` |
| **E1** | Contextual | TechLab AI bloqueado (openapi vazio, Docker off) → marcar PENDING | ℹ️ | `integrations/techlab-ai/`, `project-context.json` |
| **E2** | Contextual | `fe-prototype-analyzer`: 0 telas no HTML consolidado | ℹ️ | `scripts/fe-prototype-analyzer.py` |
| **FE-4.9** | Framework FE | Limpar stubs órfãos `libs/<mod>/src` do skeleton Python | ⏳ | gerador `new-project.py` |
| **FE-contracts** | Framework FE | `@journeyos/shared/contracts` (de OpenAPI) | ⏳ | bloqueado pelo BE expor contratos |

---

## 1. Robustez de toolchain (A1–A4)

**Contexto:** a Fase 1 rodou num ambiente **sem Gradle no PATH e com Docker desligado**. Os
comandos não anteciparam isso de forma uniforme — alguns gates foram diferidos com nota, outros
teriam falhado bruscamente.

### A1 + A2 + D3 — Preflight + ledger de gates diferidos ✅
- **`scripts/preflight.py`** — detector de toolchain. `python scripts/preflight.py --gates compileJava,architectureCheck,bddGate --service <svc>` imprime uma **matriz de capacidade** (`shutil.which` + wrapper `backend/gradlew`) e classifica cada gate como *runnable* ou *DIFERIDO*, com o **comando de recuperação exato**. Fonte única do mapa gate→tool (dict `GATES`); importável (`from preflight import plan_gates, resolve_tool`).
- **`scripts/be-gates-replay.py`** — lê a tabela `## Ledger de gates diferidos` de um master-plan, checa disponibilidade via preflight, roda só os *runnable* e, com `--run --update`, reescreve o Status de cada linha. Compartilhado BE/FE via `--ledger <path>` (gates do FE rodam com `cwd=frontend/`).
- **Ledger** = seção `## Ledger de gates diferidos` em ambos os master-plans. BE foi *seeded* com os 3 gates Gradle diferidos (uma linha para `./gradlew compileJava` na raiz, que cobre todos os subprojetos). Ambos os autopilots de arquitetura ganharam um **Passo 0.5 — Preflight** + regra de manutenção do ledger.
- **Princípio:** quando um scaffold/gate não pode rodar por falta de toolchain, **não falhar no meio** — registrar no ledger com o comando de recuperação e continuar. O scaffold em si não é bloqueado por um verificador ausente. Rode `python scripts/be-gates-replay.py --run --update` quando o toolchain aparecer.

### A3 — Fail-fast em erro de sub-gerador ✅
`be-module-generator.py` agora aborta no 1º sub-gerador (migration/entity/bdd) que retorna código ≠ 0 — antes só emitia `[WARN]` e seguia, deixando scaffold parcial silencioso. Helper `_invoke_subgen`. Flag `--continue-on-error` restaura o modo tolerante.

### A4 — `specs-validate` reposicionado ✅
Separação **geração vs gate** tornada explícita: A3 faz só a geração (`be-spec-to-bdd.py generate`, determinística, independente de toolchain); o **gate** (`compileTestJava` + `*CucumberIT*`) vive só em A5, após o scaffold e condicionado ao Gradle (senão → ledger). Elimina a ambiguidade de "quando o gate realmente passa".

---

## 2. Dedup e robustez de geradores (B1, B2, TG-1)

### B1 — `@Entity` duplicado: base canônica + gate config↔SQL ✅
**Problema:** `be-module-generator.py` emitia a camada hexagonal canônica (`*JpaEntity`/`*JpaRepository`/`*RepositoryPort`/`*RepositoryAdapter`), e depois **encadeava** `be-entity-generator.py`, que emitia uma camada *paralela* com nomes incompatíveis (`*Entity`/`*Repository`/`*Port`/`*JpaAdapter`) sobre as **mesmas tabelas** → dois `@Entity` por tabela → Hibernate duplicate-mapping (confirmado no INTL).

**Resolução:**
- `be-entity-generator.py` ganhou **guarda de base-canônica**: por tabela, se `<X>JpaEntity.java` já existe, ele **pula** sua própria camada + domain model/service (imprime `[=] base layer canônica presente`). Escape: `--allow-duplicate-layer`. Validado: INTL pula 7 agregados.
- `be-module-generator.py` ganhou o gate `_validate_config_vs_sql`, que **reporta** divergência de nome config↔SQL (antes silenciosa).
- Módulos scaffoldados **antes** do fix (WRKS, JRNY, ASST, COMM, SALE, LEAD) tiveram a camada órfã removida manualmente; receita de limpeza documentada na memória.

### B2 — Entity-gen convergido para templates `.j2` ✅
Os 4 emissores de persistência do `be-entity-generator.py` (entity/repository/port-out/adapter) passaram de f-strings inline para **Jinja2** (`templates/operational/code/java/eg-*.java.j2`), via `render_code_template` — mesmo mecanismo do module-gen. **Byte-parity validada** (golden diff idêntico). A lógica de colunas/tipos permanece em Python (passada como contexto). Edite o `.j2`, não strings inline.

### TG-1 — Bug `smart_query_methods` ✅
`smart_query_methods(table, pkg)` estava definida com 2 params mas o corpo usava `overrides` e o call-site passava 3 args → `TypeError` que abortava a geração após a 1ª tabela. Corrigido adicionando `overrides: GenerationOverrides | None = None` à assinatura.

---

## 3. Consistência BE/FE (C1–C4)

### C1 — Schema de checkpoint unificado ✅
O campo divergente `prioridade` (BE) / `fase` (FE) foi unificado em **`progressUnit`** (string) nos dois autopilots de execução. Envelope canônico: `id, pipeline, modulo, currentStep, nextStep, progressUnit, iteration, timestamp, notes` — identidade específica `service` (BE) / `feature` (FE).

### C2 — Migração de vocabulário `@hub`→`@journeyos` ✅
Concluída. Zero residuais em `.claude/commands/`, `scripts/`, `frontend/` (código+config), `CLAUDE.md`, `project-context.json`. As menções `@hub` restantes são **registros históricos** da migração (tabela "de→para" em `standards/module-pattern.md`, notas em master-plan FE) — corretas de manter.

### C3 — Família `be-feature-architect-*` ⏭️ NÃO criar
**Decisão deliberada (2026-06-05):** o BE evolui um serviço via `be-validator → be-planner → be-implement` (issue-based). Espelhar ~1300 linhas do pipeline de feature do FE não se justifica para o modelo do BE. Reabrir só se surgir necessidade real de features incrementais guiadas no BE.

### C4 — Gate EARS no FE ✅
Novo comando `.claude/commands/fe-architect-specs-validate.md`:
- **Gate 1** — sintaxe EARS via `scripts/be-validate-ears.py` (agnóstico de linguagem, reutilizado do BE) sobre SPEC-01..07.
- **Gate 2** — cobertura EARS→Gherkin: cada `THE SYSTEM SHALL` tem um `Scenario:` em `e2e/*.feature`.

Validation-only (sem codegen). `fe-architect-specs` passou a emitir critérios EARS; `fe-architecture-autopilot` ganhou a etapa **A2.5 — Specs Validate** (entre specs e backlog) + coluna `Specs-Val` no master-plan. Testado sobre SPEC real do WRKS (`0 issues`).

---

## 4. Orquestração: autopilots, master-plan, checkpoints (D1–D2, F-*)

Padrão validado em campo que o **gerador de monorepos** deve passar a emitir por padrão (ver `_inbox/LEARNING-architecture-autopilot-master-plan.md`).

### F-AUTO — Architecture Autopilots (Layer 1) ✅
Dois meta-orquestradores que **encadeiam numa única invocação** as etapas do Architect e **param antes** da implementação:

| Command | Cadeia | Para em |
|---|---|---|
| `/be-architecture-autopilot <MOD>` | vision → specs → specs-validate → backlog → scaffold | scaffold |
| `/fe-architecture-autopilot <MOD>` | vision → specs → specs-validate → backlog → scaffold → e2e-validate | e2e-validate |

Princípios: **não duplicar lógica** (lê e segue cada sub-command); **read-only sobre o código** (só escreve checkpoint + master-plan); encadeamento no caminho feliz; **skip idempotente** (`--force` desativa); propaga bloqueios sem mascarar. Flags padronizadas: `--resume`, `--force`, `--until=<etapa>`, `--dry-run`.

### F-MP — Architecture Master-Plan ✅
Arquivo **global por camada** (`docs/architecture/{backend,frontend}/plans/architecture-master-plan.md`). **Regra de ouro:** é um *espelho* de progresso, nunca a fonte da verdade — reconstruível do disco. Estrutura = tabela de status por módulo + log cronológico append-only. Infra (GWY/REG/MIG) marca `N/A` nas etapas que não se aplicam.

### F-CKPT — Checkpoints em `tmp/` ✅
Após cada etapa pesada, grava `tmp/*-architecture-autopilot/<MOD>/state.json` (crash-recovery + `--resume`). `tmp/` está no `.gitignore` (efêmero).

### D1 — Header "auto-gerenciado" ✅
O master-plan BE legado tinha header "atualizar **manualmente**", contradizendo o protocolo do autopilot ("atualizado **automaticamente** … NÃO editar à mão durante uma corrida"). Corrigido: o gerador emite o header "auto-gerenciado pelo autopilot" + tabela/log nas colunas canônicas.

### D2 — Atualizar master-plan por fase ✅
Sequência obrigatória por etapa: **(1) executa sub-command → (2) salva checkpoint → (3) atualiza master-plan → (4) prossegue.** A ordem importa (checkpoint **antes** do master-plan), para sobreviver a crash no meio da corrida.

---

## 5. Framework FE específico (FE-1 … FE-6)

Retrospectiva da 1ª corrida real do FE (`/fe-architecture-autopilot WRKS`). O pipeline FE foi *templado* de um projeto-modelo ("Hub SaaS") e nunca rodara de ponta a ponta no Journey OS.

| ID | Melhoria | Detalhe |
|----|----------|---------|
| **FE-1** | Vocabulário canônico | `module/@journeyos/module-pattern` aposenta `tool/@hub/tax-map`. Renomeação em massa: 10 comandos `fe-*` + 21 artefatos WRKS (432 substituições). Rosetta em `standards/module-pattern.md`. |
| **FE-2** | Gerador Nx local | `@journeyos/internal:module` (`npx nx g @journeyos/internal:module <mod>`, rodar de dentro de `frontend/`). **Plugin Nx**, não script Python como o BE — compõe `@nx/angular` (app+libs) + `@nx/playwright`. Idempotente. Lê `generator-config.yml` via `fs` do repo-root (docs vivem **fora** do workspace Nx — pegadinha estrutural permanente). |
| **FE-3** | Dev-deps consolidadas | A corrida descobriu deps faltando uma a uma (`@angular-eslint/*`, `@nx/playwright`, `@playwright/test`, `eslint-plugin-playwright`, `@nx/plugin`, `@nx/devkit`). Todas consolidadas no `frontend/package.json`. |
| **FE-4** | Shared libs Wave-0 | 9 libs `@journeyos/shared/{auth-session, empresa-context, access-decision, access-http-base, error-model, observability, ui-tokens, ui-components, ui-feedback}` criadas (stubs de API, typecheck clean). Wiring real = ciclo de implement de cada lib. |
| **FE-5** | Shell → app Nx | `journey-os-web` virou app Nx (project.json + targets build/serve/test/lint; `provideHttpBase` wired; registry `config/module-descriptors.ts`). |
| **FE-6** | Module-entry como library (ADR-006) | A entry do módulo é uma **library** `libs/<mod>/shell-entry` (importPath `@journeyos/<mod>`), porque apps Nx não importam outros apps. Gerador **v3** emite a entry como lib + host fino `apps/<mod>` que faz `loadChildren(() => import('@journeyos/<mod>'))`. O Shell registra módulos importando `@journeyos/<mod>`. WRKS migrado e verde. **Wave-0 COMPLETA.** |

**Decisões FE já valendo como padrão (D-1…D-8):** gerador é plugin Nx local (não Python); compõe `@nx/angular`+`@nx/playwright` em vez de hand-roll; stubs self-contained (compilam antes das shared libs); Shell consome via descriptor self-contained; idempotência; 1 spec Playwright por `.feature` (gate A5 = `nx e2e --list`); `generator-config.yml` usa `module:`/`module_contract:`.

---

## 6. Itens contextuais e pendências (E1, E2, FE-4.9, contracts)

### ℹ️ E1 — TechLab AI bloqueado
`integrations/techlab-ai/openapi.json` vazio, SHA `PENDING_FIRST_COMMIT`, Docker desligado → DTOs e contratos de IA são placeholders (afeta LEAD/ASST/JRNY/INTL/COMM). O workflow deve **marcar o estado PENDING explicitamente** nos artefatos, em vez de prosseguir como se o contrato existisse. Recuperar com `python scripts/sync-techlab-ai.py --target-sha <sha>` quando o upstream tiver primeiro commit + Docker rodando.

### ℹ️ E2 — `fe-prototype-analyzer`: 0 telas
O analisador detectou 0 telas no HTML consolidado → `prototype-map.json` não gerado. Revisitar com a estrutura de diretório modular do protótipo.

### ⏳ Pendências abertas
- **FE-4.9** — limpar stubs órfãos `libs/<mod>/src/index.ts` + path mappings `@journeyos/<mod>` deixados pelo `new-project.py` para os 10 módulos (o module-pattern usa sub-libs, não um `src` único). Não bloqueia; confunde.
- **`@journeyos/shared/contracts`** — gerado de OpenAPI quando o BE expor contratos.
- **FE-4.6/4.7/4.8** (BAIXA) — avaliar `playwright-bdd` para Gherkin real; limpar componentes-amostra das libs não-UI; alinhar nomes dos componentes-stub (v2.1 do gerador).

---

## 7. Artefatos criados/alterados (índice rápido)

**Scripts novos (melhorias):**
- `scripts/preflight.py` — detector de toolchain + matriz de capacidade (A1/A2)
- `scripts/be-gates-replay.py` — executa gates diferidos do ledger (D3)
- `scripts/be-validate-ears.py` — validador EARS agnóstico (reusado BE↔FE, C4)

**Scripts alterados:**
- `scripts/be-module-generator.py` — fail-fast (A3) + gate config↔SQL (B1) + preflight
- `scripts/be-entity-generator.py` — guarda base-canônica (B1) + templates `.j2` (B2) + fix `smart_query_methods` (TG-1)
- `scripts/be-spec-to-bdd.py` — separação geração/gate (A4)

**Comandos novos:**
- `.claude/commands/fe-architect-specs-validate.md` — gate EARS do FE (C4)
- `.claude/commands/be-architecture-autopilot.md` + `fe-architecture-autopilot.md` — autopilots Layer 1 (F-AUTO)

**Templates novos:** `templates/operational/code/java/eg-*.java.j2` (B2)

**FE (gerador Nx + skeleton):**
- `frontend/libs/internal-nx-plugin/internal` — gerador `@journeyos/internal:module` v3 (FE-2, FE-6)
- `frontend/libs/shared/*` — 9 shared libs Wave-0 (FE-4)
- `frontend/apps/journey-os-web` — Shell promovido a app Nx (FE-5)
- `docs/architecture/frontend/adr/ADR-006-module-entry-as-library.md` (FE-6)

---

## 8. Fontes detalhadas (para aprofundar cada item)

| Documento | Cobre |
|---|---|
| `docs/architecture/shared/workflow-improvements.md` | Análise transversal completa A1–E2 (Esperado→Observado→Onde dói→Melhoria→Prio) + backlog P1/P2/P3 |
| `docs/architecture/frontend/plans/framework-improvements.md` | Retrospectiva FE detalhada (§1–6): problemas, decisões D-1..D-8, backlog §4.x, checklist do gerador |
| `_inbox/LEARNING-architecture-autopilot-master-plan.md` | Padrão autopilot+master-plan+checkpoint para backport ao gerador de monorepos |
| `docs/architecture/frontend/standards/module-pattern.md` | Padrão canônico de módulo FE + Rosetta `@hub`→`@journeyos` |
| `docs/architecture/{backend,frontend}/plans/architecture-master-plan.md` | Instâncias dos master-plans (tabela de status + ledger de gates) |

**Memórias do agente relacionadas:** `toolchain-preflight-ledger`, `toolchain-entity-generator-conflict`, `workflow-p3-decisions`, `fe-module-framework`, `fe-scaffold-toolchain-absent`, `gradle-toolchain-absent`, `feedback-master-plan-each-phase`.
