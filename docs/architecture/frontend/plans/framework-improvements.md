# Framework Improvements — Journey OS Frontend (Layer 1 / Architect)

> Retrospectiva acionável da **primeira corrida real** do pipeline de arquitetura FE
> (`/fe-architecture-autopilot WRKS`, 2026-06-05): o que quebrou, o que foi decidido e o que
> precisa mudar no framework (comandos `fe-architect-*`, gerador, skeleton) para os próximos
> módulos (ASST → INTL → LEAD → COMM → JRNY → SALE) rodarem sem fricção.
>
> **Status do WRKS ao final:** A1→A5 completos e verdes (lint+test+build dos 12 projetos +
> `e2e --list` 18 testes/6 specs). Único item deferido: mutação do Shell (ver §4.3).

---

## 1. Contexto

O pipeline FE foi **templado de um projeto-modelo** ("Hub SaaS" / `bosq-monorepo`) e nunca tinha
sido executado de ponta a ponta no Journey OS. A corrida do WRKS exercitou tudo pela primeira vez
e revelou um conjunto de lacunas — de **vocabulário herdado** a **toolchain ausente** — todas
resolvidas durante a corrida. Este doc consolida os aprendizados como melhorias de framework.

---

## 2. Problemas encontrados (e como foram resolvidos)

### 2.1 Vocabulário herdado conflitava com o projeto
Os comandos usavam `tool`, scope `@hub`, padrão `tax-map` e o gerador `@hub/internal:tool` —
em contradição direta com o `CLAUDE.md` ("only MODULE exists") e o npmScope `@journeyos`.
**Resolução:** standard `docs/architecture/frontend/standards/module-pattern.md` (Rosetta de
migração) + renomeação em massa (10 comandos `fe-*` + 21 artefatos WRKS, 432 substituições,
4 arquivos renomeados).

### 2.2 Toolchain de scaffold inexistente
- `frontend/` sem `node_modules` (sem binário `nx`).
- O gerador `@hub/internal:tool` **não existia** (não declarado, ausente no repo e nos repos irmãos).
- Faltavam dev-deps que o Nx/Angular assume: `@angular-eslint/*`, `@nx/playwright`,
  `@playwright/test`, `eslint-plugin-playwright`, `@nx/plugin`, `@nx/devkit`.
**Resolução:** `npm install` + instalação incremental das deps + **construção do gerador local**
`@journeyos/internal:module` (`frontend/libs/internal-nx-plugin/internal`).

### 2.3 Os docs vivem FORA do workspace Nx
`generator-config.yml` está em `<repo>/docs/...`, mas o workspace Nx é `<repo>/frontend`. O `Tree`
do Nx não lê fora da sua raiz. **Resolução:** o gerador lê o config via `fs` usando
`path.dirname(tree.root)` (repo-root). **Esta é uma pegadinha estrutural permanente** — qualquer
ferramenta Nx que precise dos docs tem de subir um nível.

### 2.4 O Shell (`journey-os-web`) não é um projeto Nx
É um stub hand-authored (sem `project.json`, ausente do grafo Nx; `app.routes.ts` mínimo). Logo
**não dá para registrar módulos nele via `loadChildren`** ainda. **Resolução (deferida):** o gerador
emite `apps/<mod>/src/app/<mod>-module/<mod>.descriptor.ts` (self-contained) para o Shell consumir
quando virar app Nx — em vez de mutar um stub e quebrar.

### 2.5 Tensão estrutural: módulo como `app` vs `library`
O padrão coloca a entry em `apps/<mod>` (app Angular), mas o Shell precisa fazer `loadChildren`
dela — algo que apps normalmente não fazem entre si no Nx. Decisão pendente (ver §4.4).

### 2.6 Stubs precisam compilar SEM as shared libs
As shared libs (`@journeyos/shared/*`) ainda não existem; código gerado que as importasse não
compilaria. **Resolução:** o gerador produz **stubs self-contained** (tipos `Module*` locais no
contract, zero import de `@journeyos/shared/*`). O wiring real fica para `/fe-implement` (P-waves),
depois que as shared libs existirem.

---

## 3. Decisões tomadas (já valem como padrão)

| # | Decisão | Artefato |
|---|---|---|
| D-1 | Vocabulário canônico `module/@journeyos/module-pattern` (aposenta `tool/@hub/tax-map`) | `standards/module-pattern.md` |
| D-2 | Gerador é **plugin Nx local** (não script Python como o BE), idiomático ao Nx | `libs/internal-nx-plugin/internal` |
| D-3 | Gerador **compõe** `@nx/angular` (app+lib) + `@nx/playwright` (e2e) em vez de hand-rolar project.json/tsconfig | `generators/module/generator.ts` |
| D-4 | Stubs **self-contained** (compilam antes das shared libs); wiring real no implement | idem |
| D-5 | Shell consome o módulo via **descriptor self-contained** (ADR-004), sem mutar o Shell stub | `<mod>.descriptor.ts` |
| D-6 | Gerador **idempotente** (re-run pula projetos existentes; só adiciona o novo) | idem |
| D-7 | e2e: 1 spec stub Playwright por `.feature` (gate A5 = `nx e2e --list`) | idem |
| D-8 | `generator-config.yml` usa `module:` / `module_contract:` (não `service:`/`tool_contract:`) | WRKS config |

---

## 4. Recomendações de melhoria (backlog do framework)

> **Status Wave-0 (2026-06-05):** §4.1 ✅ · §4.5 ✅ · §4.3 ✅ · **§4.4 ✅ RESOLVIDO** (ADR-006:
> module-entry como library `@journeyos/<mod>`; gerador v3; WRKS migrado; Shell registra o WRKS).
> **Wave-0 COMPLETA** — pronto para `/fe-implement` do WRKS e para scaffoldar os próximos módulos.

### 4.1 Declarar TODAS as dev-deps do FE no `frontend/package.json` (ALTA) — ✅ FEITO
A corrida descobriu deps faltando uma a uma (`@angular-eslint/*`, `@nx/playwright`,
`@playwright/test`, `eslint-plugin-playwright`, `@nx/plugin`, `@nx/devkit`). **Ação:** consolidar
todas no `package.json` do skeleton (e/ou um `setup` script) para que o scaffold do 2º módulo em
diante não pare por dependência. Candidato a um `scripts/fe-doctor` que valida o ambiente.

### 4.2 Atualizar o comando `fe-architect-scaffold` (ALTA)
Hoje ele fala de `@hub/internal:tool` (corrigido na renomeação para `@journeyos/internal:module`),
mas deve também: (a) instruir rodar **de dentro de `frontend/`**; (b) documentar o gate A5
(`nx e2e <mod>-e2e --list`); (c) apontar a pré-condição de shared libs + Shell-Nx.

### 4.3 Promover o Shell a app Nx de verdade (ALTA) — ✅ FEITO (parcial)
`journey-os-web` virou app Nx (project.json + targets build/serve/test/lint; componentes do shell
preservados com selector `jos-*`; `provideHttpBase` de `@journeyos/shared` no `app.config`). Criado
`config/module-descriptors.ts` (registry) **vazio**. **Falta:** popular `MODULE_DESCRIPTORS` —
bloqueado por §4.4. Quando resolvido, o gerador ganha **v3** (registro automático no Shell).

### 4.4 Decidir módulo-entry: `app` vs `library` — ✅ RESOLVIDO (ADR-006, opção a)
**Decisão:** entry como **library** `libs/<mod>/shell-entry` (importPath `@journeyos/<mod>`). Gerador v3
emite a entry como lib + host fino `apps/<mod>`; Shell importa `@journeyos/<mod>`. WRKS migrado e verde.
Detalhes em `docs/architecture/frontend/adr/ADR-006-module-entry-as-library.md`. _(Contexto original:)_
O Shell precisa importar o `<mod>.descriptor.ts` para registrar o módulo, mas a entry vivia em
`apps/<mod>` — e **apps Nx não importam outros apps** (boundary), nem têm importPath. Opções avaliadas:
- **(a) Entry como library** (`libs/<mod>/shell-entry` com importPath `@journeyos/<mod>`): o Shell
  importa `@journeyos/<mod>` (descriptor + module). `apps/<mod>` vira host fino de dev/build (ou some).
  Resolve o boundary de forma limpa. **Recomendado.**
- **(b) Manter `apps/<mod>`** e expor o descriptor via um path mapping/lib-ponte só para o Shell.
  Menos limpo; mantém um app que carrega outro.
Decisão vira **ADR global FE** e muda a estrutura que o gerador emite (afeta todos os módulos —
WRKS já scaffoldado precisaria de migração leve da entry para lib).

### 4.5 Shared libs como Wave-0 explícita (ALTA) — ✅ FEITO
As 9 libs `@journeyos/shared/{auth-session, empresa-context, access-decision, access-http-base,
error-model, observability, ui-tokens, ui-components, ui-feedback}` criadas com tags `scope:shared`
+ superfície de API pública (stubs que typecheck clean; `nx lint` + `tsc --noEmit` verdes). Wiring
real = ciclo de implement de cada lib. Falta `@journeyos/shared/contracts` (gerado de OpenAPI quando o BE expor).

### 4.9 Limpar stubs órfãos do skeleton Python (MÉDIA)
O `new-project.py` deixou `libs/<mod>/src/index.ts` + path mappings `@journeyos/<mod>` para os 10
módulos — órfãos: o module-pattern usa sub-libs (`libs/<mod>/data-access`, `feature-*`, …), não um
`libs/<mod>/src` único. Remover os 10 mappings + dirs stub (`@journeyos/wrks`, `@journeyos/asst`, …)
para evitar imports ambíguos. Não bloqueia, mas confunde.

### 4.6 e2e: avaliar `playwright-bdd` (BAIXA)
Hoje cada `.feature` vira um spec stub Playwright (`test.fixme`). Se quisermos rodar o **Gherkin
real**, avaliar `playwright-bdd` (ou Cucumber) para executar os `.feature` diretamente, em vez de
reescrever cenários em TS no implement P9.

### 4.7 Limpeza de componentes-amostra das libs não-UI (BAIXA)
`@nx/angular:library` gera um componente-amostra em toda lib (inclusive `data-access`, `access`).
São inócuos mas poluem. Avaliar removê-los no gerador (ou `--skipTests`/entry vazio) numa v2.1.

### 4.8 Nome dos componentes-stub (BAIXA)
Saem como `wrks-data-access.component` dentro de `data-access`. Cosmético; alinhar nomes na v2.1.

---

## 5. Checklist do gerador `@journeyos/internal:module`

- [x] App `apps/<mod>` (standalone, OnPush, routing) com tags
- [x] Libs `data-access, access, integration, navigation, ui, styles` + `feature-*` por config
- [x] `<mod>-module/` (contract, permission-map, feature-flags, routes, nav.config, bootstrap, module)
- [x] `<mod>.descriptor.ts` (consumível pelo Shell)
- [x] `apps/<mod>-e2e` (Playwright) + 1 spec por `.feature`
- [x] Idempotência (re-run pula existentes)
- [x] Lê `generator-config.yml` via `fs` do repo-root
- [ ] **v3:** registrar no Shell (`module-descriptors.ts`/`shell-routes`) — após §4.3
- [ ] **v2.1:** limpar componentes-amostra das libs não-UI; nomes de stub
- [ ] Flag `--skipE2e` / `--force` documentadas

---

## 6. Sequência recomendada para o próximo módulo (ASST)

1. (uma vez) §4.1 deps + §4.5 shared libs + §4.3 Shell-Nx.
2. `/fe-architecture-autopilot ASST` (A1→A3 docs; A4 já roda com o gerador existente).
3. Quando §4.3 estiver pronto, evoluir o gerador p/ **v3** e o registro no Shell passa a ser automático.

---

## Referências

- `docs/architecture/frontend/standards/module-pattern.md` — padrão canônico de módulo + Rosetta
- `docs/architecture/frontend/plans/architecture-master-plan.md` — progresso por módulo
- `frontend/libs/internal-nx-plugin/internal/src/generators/module/generator.ts` — o gerador
- Memória: `fe-scaffold-toolchain-absent` — histórico do bloqueio e da resolução
