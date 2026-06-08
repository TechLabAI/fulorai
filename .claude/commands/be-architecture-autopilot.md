# BE Architecture Autopilot -- Meta-Orchestrator (Journey OS)

Voce e o orquestrador da **camada de arquitetura** (Layer 1 -- Architect) do backend
Journey OS (Java + Spring Boot, arquitetura hexagonal).

Encadeia em uma unica invocacao as 5 etapas de criacao arquitetural de um modulo --
**vision -> specs -> specs-validate -> backlog -> scaffold** -- e **PARA no scaffold**.
Diferente do `be-autopilot`, este command NAO entra no loop de implement (Layer 2).

Salva checkpoints (crash recovery + retomada via `--resume`) e, a cada etapa concluida,
registra o progresso no **master plan global** de arquitetura.

**Input:** `$ARGUMENTS`

Formatos aceitos:
- `<MODULO>` (ex.: `WRKS`) -> arquiteta o modulo do inicio ao scaffold (pulando etapas ja concluidas).
- `<MODULO> --resume` -> retomar de checkpoint salvo.
- `<MODULO> --force` -> reexecutar etapas mesmo que os artefatos ja existam (re-arquitetura).
- `<MODULO> --until=<etapa>` -> parar apos a etapa indicada (`vision|specs|specs-validate|backlog|scaffold`).
- `<MODULO> --dry-run` -> apenas reportar o plano de execucao (quais etapas rodariam / seriam puladas), sem executar.

Modulos validos: WRKS | LEAD | JRNY | ASST | COMM | SALE | INTL | GWY | REG | MIG

---

## Principio central

**Uma unica chamada para arquitetar o modulo ate o scaffold.** O autopilot delega para os
sub-commands existentes (`be-architect-vision`, `be-architect-specs`,
`be-architect-specs-validate`, `be-architect-backlog`, `be-architect-scaffold`) -- **nao
duplica logica**: le e segue o protocolo de cada `.md` referenciado.

Checkpoints sao salvos em disco apos cada etapa pesada para permitir retomada se a sessao
for interrompida, mas o autopilot **NAO interrompe o fluxo do usuario** no caminho feliz:
prossegue para a proxima etapa imediatamente.

A cada etapa concluida, atualiza `docs/architecture/backend/plans/architecture-master-plan.md`
(tabela de status por modulo + log cronologico).

---

## Passo 0 -- Setup e deteccao de modo

1. Extrair `<MODULO>` e flags de `$ARGUMENTS`.
2. Validar que `<MODULO>` esta no registry (WRKS/LEAD/JRNY/ASST/COMM/SALE/INTL/GWY/REG/MIG).
   Se invalido: listar os validos e parar.
3. Resolver `<service>` = `backendService` do modulo em `project-context.json`
   (default `<modulo-lowercase>-service`). Layout flat: o servico vive em `services/<service>/`.
4. Resolver `type` do modulo: `standard` por padrao; `gateway` para GWY; `registry` para REG;
   modulos com `isInfrastructure: true` **nao tem** dominio/specs de negocio -- ver "Modulos de infraestrutura".
5. Criar diretorio de checkpoint: `tmp/be-architecture-autopilot/<MODULO>/`.
6. Garantir que `docs/architecture/backend/plans/architecture-master-plan.md` existe
   (criar com o cabecalho canonico se ausente -- ver "Master plan").
7. Determinar etapa inicial:
   - Se `--resume` e `state.json` existe: ler checkpoint e retomar de `nextStep`.
   - Se `--resume` e `state.json` NAO existe: tratar como fresh start.
   - Caso contrario: comecar em A1 (vision), pulando etapas cujos artefatos ja existam
     (ver checks de pre-requisito por etapa). `--force` desativa o skip.
8. Emitir a **mensagem inicial obrigatoria** (ver final).

---

## Passo 0.5 -- Preflight de toolchain (D-323)

Antes de qualquer etapa que dependa de ferramentas externas (Gradle nos gates
pos-scaffold, Docker para integration tests), rodar **uma vez** o preflight:

```bash
python scripts/preflight.py --gates compileJava,architectureCheck,bddGate --service <service>
```

O preflight detecta o que esta disponivel no ambiente e classifica cada gate como
**runnable** ou **DIFERIDO**, com o comando de recuperacao exato. Guardar essa
**matriz de capacidade** para as etapas A3/A5:

- Gate **runnable** -> executar normalmente na etapa correspondente.
- Gate **DIFERIDO** (tool ausente) -> NAO tentar rodar. Registrar a linha no
  **Ledger de gates diferidos** do master plan com o comando de recuperacao, e prosseguir.
  O scaffold em si **nao e bloqueado** por toolchain ausente -- so os gates de verificacao
  sao adiados.

> Replay quando o toolchain aparecer: `python scripts/be-gates-replay.py --run --update`

---

## Checkpoint -- como funciona

Apos cada etapa pesada, salvar estado em `tmp/be-architecture-autopilot/<MODULO>/state.json`:

```json
{
  "id": "<MODULO>",
  "pipeline": "architecture",
  "modulo": "<MODULO>",
  "service": "<service>",
  "type": "standard | gateway | registry",
  "currentStep": "<etapa concluida>",
  "nextStep": "<proxima etapa | done | blocked>",
  "timestamp": "<ISO-8601>",
  "notes": "<contexto minimo para retomar>"
}
```

Apos salvar, emitir linha de status curta e prosseguir:

```
Checkpoint: <currentStep> -> <nextStep>
```

O autopilot encerra a invocacao apenas em 3 casos:
- **Bloqueio** de pre-requisito ou erro irrecuperavel (`nextStep: "blocked"`).
- **Parada solicitada** via `--until=<etapa>`.
- **Finalizacao** (scaffold concluido, `nextStep: "done"`).

---

## Pipeline de Arquitetura (A1 -> A5)

> Cada etapa: (1) checa pre-requisito de skip, (2) le e executa o protocolo do sub-command
> referenciado, (3) salva checkpoint, (4) atualiza o master plan, (5) prossegue.

### Etapa A1 -- Vision

1. **Skip check:** se `docs/architecture/backend/services/<service>/01-architectural-vision.md`
   ja existe e esta completo (e sem `--force`): marcar `vision = OK (existente)` no master plan,
   pular para A2.
2. Executar o protocolo de `.claude/commands/be-architect-vision.md` com `<MODULO>`.
3. Checkpoint (`currentStep: "vision"`, `nextStep: "specs"`).
4. Master plan: `vision = OK`, log da etapa.
5. Prosseguir para A2 (a menos que `--until=vision`).

### Etapa A2 -- Specs

1. **Pre-requisito:** docs `01..06` + `adr/ADR-001.md` existem. Se faltar -> bloquear.
2. **Skip check:** se `contracts/api-contract.md`, `contracts/data-model.md` e
   `contracts/event-contracts.md` ja existem (e sem `--force`): `specs = OK (existente)`,
   pular para A3.
3. Executar o protocolo de `.claude/commands/be-architect-specs.md` com `<MODULO>`.
4. Checkpoint (`currentStep: "specs"`, `nextStep: "specs-validate"`).
5. Master plan: `specs = OK`, log da etapa.
6. Prosseguir para A3 (a menos que `--until=specs`).

### Etapa A3 -- Specs Validate (EARS -> BDD)

Esta etapa roda em **modo generate** (determinístico, independente de toolchain);
o **gate de compilacao** e deferido para apos o A5 (ver A5.bdd-gate).

1. **Pre-requisito:** specs EARS existem em `spec/backend/`. Se faltar -> bloquear.
2. Executar o protocolo de `.claude/commands/be-architect-specs-validate.md` com `<MODULO>`,
   **apenas a parte de geracao** (`be-spec-to-bdd.py generate ...`).
   - **Gate de compilacao/comportamento e diferido** se Gradle ausente (Passo 0.5) ou scaffold
     ainda nao rodou. Registrar `bddGate` no Ledger de gates diferidos.
3. Checkpoint (`currentStep: "specs-validate"`, `nextStep: "backlog"`,
   notes com `gate=deferido|ok|fail` e contagem de cenarios).
4. Master plan: `specs-validate = OK (gate deferido)` ou `OK`, log da etapa.
5. Prosseguir para A4 (a menos que `--until=specs-validate`).

> **Modulos de infraestrutura:** pular A3, marcar `specs-validate = N/A`.

### Etapa A4 -- Backlog

1. **Pre-requisito:** contracts, SPECs e event-catalog existem. Se faltar -> bloquear.
2. **Skip check:** se `docs/architecture/backend/plans/plan-<MODULO>.md` +
   `generator-config.yml` ja existem (e sem `--force`): `backlog = OK (existente)`, pular para A5.
3. Executar o protocolo de `.claude/commands/be-architect-backlog.md` com `<MODULO>`.
4. Checkpoint (`currentStep: "backlog"`, `nextStep: "scaffold"`).
5. Master plan: `backlog = OK`, log da etapa.
6. Prosseguir para A5 (a menos que `--until=backlog`).

### Etapa A5 -- Scaffold

1. **Pre-requisitos:** `setup-local.md`, `<service>-spec.md`, `generator-config.yml`,
   `<MODULO>-001.md`. Se faltar -> bloquear.
2. **Skip check:** se `backend/services/<service>/build.gradle.kts` ja existe (e sem `--force`):
   ir direto ao A5.bdd-gate.
3. Executar o protocolo de `.claude/commands/be-architect-scaffold.md` com `<MODULO>`.
4. **A5.bdd-gate:** consultar a matriz do Passo 0.5 (apenas `type=standard`):
   - **Se Gradle disponivel:** rodar gate diferido do A3 (`compileTestJava` + `*CucumberIT*`).
   - **Se Gradle ausente (DIFERIDO):** registrar `bddGate` no Ledger, marcar
     `specs-validate = OK (gate diferido)`.
5. Checkpoint (`currentStep: "scaffold"`, `nextStep: "done"`).
6. Master plan: `scaffold = OK`, log da etapa.
7. Ir para **Finalizacao**.

---

## Master plan -- `docs/architecture/backend/plans/architecture-master-plan.md`

Atualizado a cada etapa concluida. **Idempotente:** atualizar a linha do modulo (criar
se nao existir) e **anexar** ao log.

Estrutura canonica (criar com este cabecalho se o arquivo nao existir):

```markdown
# Architecture Master Plan -- Journey OS

> Rastreia a camada de arquitetura (Layer 1 -- Architect) de cada modulo, do vision ao scaffold.
> Atualizado automaticamente pelo `/be-architecture-autopilot` a cada etapa concluida.
> NAO editar a mao durante uma corrida do autopilot.

Legenda de status: `pendente` | `em andamento` | `OK` | `bloqueado` | `N/A`

## Status por modulo

| Modulo | Servico | Vision | Specs | Specs-Validate | Backlog | Scaffold | Atualizado |
|---|---|---|---|---|---|---|---|

## Ledger de gates diferidos

| Data | Escopo | Gate | Comando de recuperacao | Status |
|---|---|---|---|---|

## Log cronologico

```

### Ledger de gates diferidos (D-323)

Secao `## Ledger de gates diferidos` -- **indice unico** de todos os gates que nao
puderam rodar por toolchain ausente. Cada linha tem o **comando de recuperacao exato**.

- Quando o Passo 0.5 marcar um gate como DIFERIDO: **acrescentar/atualizar** a linha
  (Status `diferido`). Nao duplicar: uma linha por (escopo, gate).
- Replay quando o toolchain aparecer:
  `python scripts/be-gates-replay.py --run --update`

Regras de atualizacao:
- **Tabela:** uma linha por `<MODULO>`. Antes de iniciar: `em andamento`. Ao concluir:
  `OK`, `bloqueado` ou `N/A`. Atualizar coluna `Atualizado` (`YYYY-MM-DD`).
- **Log:** append-only, uma linha por transicao:
  ```
  - <ISO-8601> -- <MODULO> -- <etapa> -- <inicio|OK|bloqueado|N/A|gate-fail> -- <nota>
  ```

---

## Modulos de infraestrutura

Modulos com `isInfrastructure: true` nao tem dominio/specs de negocio. Pular A3
(specs-validate) marcando `N/A`; backlog emite apenas `generator-config.yml` basico;
scaffold gera estrutura reduzida. Registrar `N/A` nas etapas nao aplicaveis.

---

## Regras gerais

- **Nao duplicar logica dos sub-commands.** Ler e seguir o protocolo do `.md` referenciado.
- **Encadear etapas automaticamente.** Nao instruir o usuario a rodar `/clear` ou `--resume`.
- **Sempre salvar checkpoint apos etapa pesada** e **atualizar o master plan** -- nessa ordem.
- **Read-only sobre o repo de codigo:** toda escrita em `backend/services/` ocorre via os
  scripts Python dos sub-commands. O autopilot so escreve em:
  `tmp/be-architecture-autopilot/` (checkpoint) e
  `docs/architecture/backend/plans/architecture-master-plan.md` (progresso).
- **PARA no scaffold.** Apos A5, apontar `/be-autopilot <MODULO> --implement` como proxima acao.

---

## Finalizacao

```
BE Architecture Autopilot concluido para <MODULO> (<service>)
Tipo: <standard | gateway | registry>
Etapas: vision -> specs -> specs-validate -> backlog -> scaffold
Master plan: docs/architecture/backend/plans/architecture-master-plan.md

Verificacao pos-scaffold:
  compileJava:       <OK | DIFERIDO>
  architectureCheck: <OK | DIFERIDO>
  BDD gate:          <OK | pending | N/A | FAIL | DIFERIDO>

Gates diferidos: <N> registrados no Ledger do master plan.
  Replay: python scripts/be-gates-replay.py --run --update

Proxima acao (Layer 2 -- desenvolvimento, manual):
-> /be-autopilot <MODULO> --implement
```

Em caso de parada antecipada (`--until` ou bloqueio):

```
BE Architecture Autopilot pausado em <MODULO>
Ultima etapa: <currentStep> -> <nextStep>
Motivo: <until | bloqueio: descricao>
Master plan atualizado.
Retomar: /be-architecture-autopilot <MODULO> --resume
```

---

## Mensagem inicial obrigatoria

```
BE Architecture Autopilot iniciado
Input: <$ARGUMENTS>
Modulo: <MODULO> (<service>) -- type=<standard|gateway|registry>
Modo: <fresh | resume | force | dry-run>
Etapa inicial: <nome> (etapas a pular: <lista ou nenhuma>)
Master plan: docs/architecture/backend/plans/architecture-master-plan.md
```
