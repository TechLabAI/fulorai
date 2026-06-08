# FE Architecture Autopilot -- Meta-Orchestrator (Journey OS)

Voce e o orquestrador da **camada de arquitetura** (Layer 1 -- Architect) do frontend
Journey OS (Angular + Nx, module-pattern, Signals-first, standalone + OnPush).

Encadeia em uma unica invocacao as 6 etapas de criacao arquitetural de um modulo FE --
**vision -> specs -> specs-validate -> backlog -> scaffold -> e2e-validate** -- e
**PARA na e2e-validate**. NAO entra no loop de implement (Layer 2) nem no pipeline de feature.

Salva checkpoints (crash recovery + retomada via `--resume`) e, a cada etapa concluida,
registra o progresso no **master plan de arquitetura FE**.

**Input:** `$ARGUMENTS`

Formatos aceitos:
- `<MODULO>` (ex.: `WRKS`) -> arquiteta o modulo do inicio a validacao e2e.
- `<MODULO> --resume` -> retomar de checkpoint salvo.
- `<MODULO> --force` -> reexecutar etapas mesmo que os artefatos ja existam (re-arquitetura).
- `<MODULO> --until=<etapa>` -> parar apos a etapa indicada (`vision|specs|specs-validate|backlog|scaffold|e2e-validate`).
- `<MODULO> --dry-run` -> apenas reportar o plano de execucao, sem executar.

Modulos validos: WRKS | LEAD | JRNY | ASST | COMM | SALE | INTL | GWY | REG | MIG

---

## Principio central

**Uma unica chamada para arquitetar o modulo FE ate a validacao e2e.** O autopilot delega
para os sub-commands existentes (`fe-architect-vision`, `fe-architect-specs`,
`fe-architect-backlog`, `fe-architect-scaffold`) -- **nao duplica logica**.

**Excecao:** a etapa **e2e-validate (A5) e nova** -- nao existe command FE correspondente.
Nesta etapa o autopilot executa o gate diretamente, em modo **read-only**.

---

## Passo 0 -- Setup e deteccao de modo

1. Extrair `<MODULO>` e flags de `$ARGUMENTS`.
2. Validar que `<MODULO>` esta no registry (WRKS/LEAD/JRNY/ASST/COMM/SALE/INTL/GWY/REG/MIG).
3. Resolver `<module>` = nome canonico kebab-case do modulo FE (de `project-context.json`,
   `_brief.md` ou `generator-config.yml`; derivar provisoriamente se nao existir).
   Layout Nx: app em `apps/<module>/`, libs em `libs/<module>/*`.
4. Resolver `type` do modulo: `standard` por padrao; modulos de infra (`isInfrastructure: true`)
   nao tem features/e2e de negocio.
5. Criar diretorio de checkpoint: `tmp/fe-architecture-autopilot/<MODULO>/`.
6. Garantir que `docs/architecture/frontend/plans/architecture-master-plan.md` existe.
7. Determinar etapa inicial (resume/force/fresh-start).
8. Emitir a **mensagem inicial obrigatoria**.

---

## Passo 0.5 -- Preflight de toolchain (D-323)

Antes da etapa A4 (scaffold via Nx plugin) e A5 (e2e-validate), rodar **uma vez**:

```bash
python scripts/preflight.py --gates feChecks,e2eValidate --project <module>
```

- Gate **runnable** -> executar normalmente.
- Gate **DIFERIDO** (Nx ausente) -> NAO tentar rodar. Registrar no Ledger do master plan
  e prosseguir/parar conforme o caso (scaffold FE **depende** do Nx -- se ausente, A4
  fica bloqueado ate `npm install` ser rodado).

---

## Checkpoint -- como funciona

Apos cada etapa pesada, salvar `tmp/fe-architecture-autopilot/<MODULO>/state.json`:

```json
{
  "id": "<MODULO>",
  "pipeline": "architecture",
  "modulo": "<MODULO>",
  "module": "<module>",
  "type": "standard | gateway | registry",
  "currentStep": "<etapa concluida>",
  "nextStep": "<proxima etapa | done | blocked>",
  "timestamp": "<ISO-8601>",
  "notes": "<contexto minimo para retomar>"
}
```

---

## Pipeline de Arquitetura (A1 -> A5)

### Etapa A1 -- Vision

1. **Skip check:** se `docs/architecture/frontend/modules/<module>/frontend/01-architectural-vision.md`
   ja existe (e sem `--force`): `vision = OK (existente)`, pular para A2.
2. Executar `.claude/commands/fe-architect-vision.md` com `<MODULO>`.
3. Checkpoint (`currentStep: "vision"`, `nextStep: "specs"`).
4. Master plan: `vision = OK`, log.
5. Prosseguir para A2 (a menos que `--until=vision`).

### Etapa A2 -- Specs

1. **Pre-requisito:** docs `01..06` + >= 4 ADR aceitos. Se faltar -> bloquear.
2. **Skip check:** se `frontend-spec/SPEC-01-route-map.md` e `generator-config.yml`
   existem: `specs = OK (existente)`, pular para A2.5.
3. Executar `.claude/commands/fe-architect-specs.md` com `<MODULO>`.
4. Checkpoint (`currentStep: "specs"`, `nextStep: "specs-validate"`).
5. Master plan: `specs = OK`, log.
6. Prosseguir para A2.5 (a menos que `--until=specs`).

### Etapa A2.5 -- Specs Validate (EARS gate, D-329)

Analogo ao A3 do BE. Roda **antes** do backlog. **Read-only** (validacao; nao gera
codigo). Aplica-se a `type=standard`; infra -> `N/A`.

1. **Pre-requisito:** `frontend-spec/SPEC-01..08` + >= 1 `e2e/*.feature`. Se faltar -> bloquear.
2. Executar `.claude/commands/fe-architect-specs-validate.md` com `<MODULO>`:
   - Gate 1: `python scripts/be-validate-ears.py --file <SPEC-01..07>`.
   - Gate 2: cada SHALL tem `Scenario:` em `e2e/*.feature`.
   - Gaps **nao bloqueiam** o scaffold -- viram entrada para o backlog.
3. Checkpoint (`currentStep: "specs-validate"`, notes com `ears=N`, `gate1=PASS|FAIL`, `gaps=G`).
4. Master plan: `specs-validate = OK | OK (com gaps) | FAIL | N/A`, log.
5. Prosseguir para A3 (a menos que `--until=specs-validate`).

### Etapa A3 -- Backlog

1. **Pre-requisito:** `frontend-spec/SPEC-01..08`, `generator-config.yml`,
   `contracts/backend-api-cross-link.md`, >= 1 `e2e/*.feature`. Se faltar -> bloquear.
2. **Skip check:** se `frontend/issues/FE-<PREFIX>-001.md` e `plans/plan-FE-<PREFIX>.md`
   existem: `backlog = OK (existente)`, pular para A4.
3. Executar `.claude/commands/fe-architect-backlog.md` com `<MODULO>`.
4. Checkpoint (`currentStep: "backlog"`, `nextStep: "scaffold"`).
5. Master plan: `backlog = OK`, log.
6. Prosseguir para A4 (a menos que `--until=backlog`).

### Etapa A4 -- Scaffold

1. **Pre-requisitos:** `_brief.md`, `generator-config.yml`, `SPEC-01..08`,
   `FE-<PREFIX>-001.md`. Se faltar -> bloquear.
2. **Skip check:** se `apps/<module>/` ja existe (e sem `--force`): ir direto ao A5.
3. Executar `.claude/commands/fe-architect-scaffold.md` com `<MODULO>`.
   - O **Nx plugin** (`npx nx g @journeyos/internal:module --name=<module>`)
     gera o esqueleto. O autopilot **NAO gera arquivos** -- apenas orquestra.
   - Se Nx ausente (Passo 0.5 DIFERIDO): registrar no Ledger, bloquear A4 com instrucao
     `npm install` e parar.
4. Checkpoint (`currentStep: "scaffold"`, `nextStep: "e2e-validate"`).
5. Master plan: `scaffold = OK`, log.
6. Prosseguir para A5 (a menos que `--until=scaffold`).

### Etapa A5 -- E2E-Validate (gate inline, sem sub-command)

Etapa **nova** (sem command FE correspondente). Roda **apos o scaffold** porque depende do
projeto Playwright `apps/<module>-e2e/` gerado. Aplica-se apenas a `type=standard`; infra ->
`e2e-validate = N/A`.

1. **Pre-requisito:** `apps/<module>-e2e/` existe e >= 1 `frontend/e2e/*.feature`. Se faltar ->
   bloquear.
2. Verificar que cada `e2e/<fluxo>.feature` tem spec Playwright correspondente.
3. **Gate estrutural (read-only -- nao executa fluxos reais):**
   - **Se Nx DIFERIDO (Passo 0.5):** registrar `e2eValidate` no Ledger, marcar
     `e2e-validate = OK (gate diferido)`.
   - **Se Nx disponivel:** `npx nx e2e <module>-e2e --list`.
     Esperado: specs listados, 0 erros -> gate = `OK (pending)`.
4. Checkpoint (`currentStep: "e2e-validate"`, `nextStep: "done"`).
5. Master plan: `e2e-validate = OK (pending) | gate FAIL | N/A | DIFERIDO`, log.
6. Ir para **Finalizacao**.

---

## Master plan -- `docs/architecture/frontend/plans/architecture-master-plan.md`

Estrutura canonica (criar com este cabecalho se o arquivo nao existir):

```markdown
# Architecture Master Plan -- Journey OS Frontend

> Rastreia a camada de arquitetura (Layer 1 -- Architect) de cada modulo FE, do vision a validacao e2e.
> Atualizado automaticamente pelo `/fe-architecture-autopilot` a cada etapa concluida.
> NAO editar a mao durante uma corrida do autopilot.

Legenda de status: `pendente` | `em andamento` | `OK` | `bloqueado` | `N/A`

## Status por modulo

| Modulo | Module | Vision | Specs | Specs-Validate | Backlog | Scaffold | E2E-Validate | Atualizado |
|---|---|---|---|---|---|---|---|---|

## Ledger de gates diferidos

| Data | Escopo | Gate | Comando de recuperacao | Status |
|---|---|---|---|---|

## Log cronologico

```

Replay de gates FE quando houver toolchain:
`python scripts/be-gates-replay.py --ledger docs/architecture/frontend/plans/architecture-master-plan.md --run --update`

---

## Regras gerais

- **Nao duplicar logica dos sub-commands.** A unica logica propria do autopilot e o gate A5.
- **Encadear etapas automaticamente.** Nao instruir o usuario a rodar `/clear` ou `--resume`.
- **Sempre checkpoint apos etapa pesada**, depois atualizar o master plan (nessa ordem).
- **Read-only sobre o repo de codigo:** toda escrita em `apps/`/`libs/` ocorre via o Nx plugin.
  O autopilot so escreve em: `tmp/fe-architecture-autopilot/` e o master plan FE.
- **PARA na e2e-validate.** Apos A5, apontar `/fe-validator FE-<PREFIX>-001` como proxima acao.

---

## Finalizacao

```
FE Architecture Autopilot concluido para <MODULO> (<module>)
Tipo: <standard | gateway | registry>
Etapas: vision -> specs -> specs-validate -> backlog -> scaffold -> e2e-validate
Master plan: docs/architecture/frontend/plans/architecture-master-plan.md

Verificacao pos-scaffold:
  nx lint/test/build: <OK | DIFERIDO>
  e2e gate:          <OK (pending) | N/A | FAIL | DIFERIDO>

Gates diferidos: <N> registrados no Ledger do master plan FE.
  Replay:
  python scripts/be-gates-replay.py --ledger docs/architecture/frontend/plans/architecture-master-plan.md --run --update

Proxima acao (Layer 2 -- desenvolvimento, manual):
-> /fe-validator FE-<PREFIX>-001
```

---

## Mensagem inicial obrigatoria

```
FE Architecture Autopilot iniciado
Input: <$ARGUMENTS>
Modulo: <MODULO> (<module>) -- type=<standard|gateway|registry>
Modo: <fresh | resume | force | dry-run>
Etapa inicial: <nome> (etapas a pular: <lista ou nenhuma>)
Master plan: docs/architecture/frontend/plans/architecture-master-plan.md
```
