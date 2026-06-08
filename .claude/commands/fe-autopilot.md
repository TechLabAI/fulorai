# FE Autopilot -- Meta-Orchestrator (Journey OS)

Voce e o orquestrador central do pipeline IA-First do frontend Journey OS (Angular + Nx).

Detecta o tipo de tarefa, executa o pipeline correto e salva checkpoints (crash
recovery + retomada manual via `--resume`).

**Input:** `$ARGUMENTS`

Formatos aceitos:
- `<MODULO> <feature-slug>` (ex.: `<MODULE> cadastro-cliente`) → **Pipeline A** (Architect -- nova feature em modulo existente)
- `<ISSUE_ID>` (ex.: `<MODULE>-FE-007`, `<MODULE>-INT-003`) → **Pipeline B** (Implement -- resolver issue)
- `<MODULO> <feature-slug> --resume` → Retomar Pipeline A de checkpoint salvo
- `<ISSUE_ID> --resume` → Retomar Pipeline B de checkpoint salvo

Modulos validos no FE: WRKS | LEAD | JRNY | ASST | COMM | SALE | INTL | GWY | REG | MIG

---

## Principio central

**Uma unica chamada para resolver tudo.** O autopilot delega para os sub-commands
existentes (nao duplica logica) e encadeia as etapas automaticamente em uma unica
invocacao. Checkpoints sao salvos em disco apos cada etapa pesada para permitir
retomada se a sessao for interrompida -- mas o autopilot **NAO interrompe o fluxo
do usuario**: prossegue para a proxima etapa imediatamente.

---

## Passo 0 -- Deteccao de modo

1. Extrair `$ARGUMENTS`.
2. Se contem `--resume`: ler checkpoint em `tmp/fe-autopilot/<ID>/state.json` e pular
   para a etapa salva.
3. Se input tem 2 tokens onde o primeiro e MODULO valido (WRKS/LEAD/JRNY/ASST/COMM/SALE/INTL/GWY/REG/MIG)
   e o segundo e kebab-case: **Pipeline A**. ID = `<MODULO>-<feature-slug>`.
4. Se input tem formato `<MODULO>-<FE|INT>-NNN` (ex.: `<MODULE>-FE-007`, `<MODULE>-INT-003`):
   **Pipeline B**. ID = `<ISSUE_ID>`.
5. Se ambiguo: perguntar ao usuario.

---

## Checkpoint -- como funciona

Apos cada etapa pesada, salvar estado em `tmp/fe-autopilot/<ID>/state.json`:

```json
{
  "id": "<ID>",
  "pipeline": "architect | implement",
  "modulo": "<MODULO>",
  "feature": "<feature-slug>",
  "currentStep": "<nome da etapa concluida>",
  "nextStep": "<nome da proxima etapa>",
  "progressUnit": "1",
  "iteration": 1,
  "timestamp": "2026-05-19T14:30:00Z",
  "notes": "<contexto minimo para retomar>"
}
```

Apos salvar, emitir linha de status curta e prosseguir:

```
Checkpoint: <currentStep> -> <nextStep> (progressUnit=<N>, iter=<N>)
```

O autopilot encerra a invocacao apenas em 3 casos:
- **Safety cap** atingido (5 iteracoes do loop B2->B5).
- **Erro irrecuperavel** ou intervencao manual obrigatoria (`nextStep: "blocked"`).
- **Finalizacao** da pipeline.

Nesses casos, reportar o motivo e instruir `/fe-autopilot <ID> --resume` se cabivel.

---

## Pipeline A -- Architect (nova feature em modulo existente)

Input: `<MODULO> <feature-slug>` (ex.: `<MODULE> cadastro-cliente`).

ID derivado: `<MODULO>-<feature-slug>` (ex.: `<MODULE>-cadastro-cliente`).

### Etapa A0 -- From Prototype (opcional, sob demanda)

1. Perguntar ao usuario: "Adaptar do prototipo MadeiraERP? (sim/nao + path opcional)"
2. Se sim: executar protocolo de `.claude/commands/fe-feature-architect-from-prototype.md`
   com `<MODULO> <feature-slug> --source=<path>`.
3. Checkpoint (`currentStep: "from-prototype"`, `nextStep: "discover"`).
4. Se nao: pular para A1 sem checkpoint.

### Etapa A1 -- Discover

1. Verificar pre-requisitos: SPECs do modulo + generator-config.yml + issues-map.md +
   ADRs aceitos + multi-empresa.md.
   - Se faltam: reportar e bloquear (`nextStep: "blocked"`).
2. Verificar se `docs/architecture/frontend/modules/<modulo>/frontend/frontend-spec/features/<feature-slug>/conformance-report.md`
   ja existe.
   - Se existe e status == aderente: pular para A2.
3. Executar protocolo de `.claude/commands/fe-feature-architect-discover.md`.
4. Se status == ❌ Violador: bloquear (`nextStep: "blocked"`).
5. Checkpoint (`currentStep: "discover"`, `nextStep: "spec-delta"`).
6. Prosseguir automaticamente para A2.

### Etapa A2 -- Spec Delta

1. Verificar conformance-report existe e status != ❌ Violador.
2. Verificar se `spec-delta.md` ja existe.
   - Se existe: pular para A3.
3. Executar protocolo de `.claude/commands/fe-feature-architect-spec-delta.md`.
4. Checkpoint (`currentStep: "spec-delta"`, `nextStep: "backlog"`).
5. Prosseguir para A3.

### Etapa A3 -- Backlog

1. Verificar `spec-delta.md` + `generator-config.yml` (atualizado) existem.
2. Verificar se issues `<MODULO>-FE-NNN` da feature ja existem (ler `issues-map.md`).
   - Se existem: pular para A4.
3. Executar protocolo de `.claude/commands/fe-feature-architect-backlog.md`.
4. Checkpoint (`currentStep: "backlog"`, `nextStep: "scaffold"`).
5. Prosseguir para A4.

### Etapa A4 -- Scaffold

1. Verificar pre-requisitos: issues + plan + generator-config.yml.
2. Executar protocolo de `.claude/commands/fe-feature-architect-scaffold.md`.
3. Verificar gates: `nx lint`, `nx test`, `nx build`.
4. Checkpoint (`currentStep: "scaffold"`, `nextStep: "done"`).
5. Ir para Finalizacao.

### Finalizacao Pipeline A

Ao concluir o scaffold, setar `status: "Ready"` (YAML frontmatter) e `**Status:** Ready`
(body) em todas as issues geradas na Pipeline A. Elas estao prontas para implementacao.

```
Pipeline Architect concluido para <MODULO>/<feature-slug>
Etapas executadas: [from-prototype ->] discover -> spec-delta -> backlog -> scaffold
Issues geradas: <lista <MODULO>-FE-NNN..NNN+K> [status: Ready]

Para comecar a implementar a primeira issue:
-> /fe-autopilot <MODULO>-FE-NNN
```

---

## Pipeline B -- Implement (resolver issue existente)

Input: `<ISSUE_ID>` (ex.: `<MODULE>-FE-007`).

### Etapa B1 -- Baseline (Validator Modo 1)

1. Executar protocolo de `.claude/commands/fe-validator.md`, Modo 1 (BASELINE):
   - Localizar e ler a spec da issue em `docs/architecture/frontend/issues/<ISSUE_ID>.md`.
   - Consolidar estado real de cada item do checklist.
   - Calcular score de maturidade.
   - Atualizar a issue com bloco de status.
2. Confirmar que a issue esta em `status: "Backlog"` ou `status: "Ready"`. Se necessario,
   setar `status: "Ready"` (YAML) e `**Status:** Ready` (body).
3. Se score >= 80 e checklist 100% DONE: ir para Finalizacao.
4. Checkpoint (`currentStep: "baseline"`, `nextStep: "decision"`, notes com score e done/total).
5. Prosseguir para B2.

### Etapa B2 -- Decisao (Validator Modo 2)

1. Com base no estado consolidado, decidir:
   - **PLANNER** → ir para B3
   - **IMPLEMENTADOR** → ir para B4
   - **VALIDACAO** → ir para B5
   - **ENCERRAR** → Finalizacao
2. Nao salvar checkpoint aqui (etapa leve). Prosseguir imediatamente.

### Etapa B3 -- Planner

1. Executar protocolo de `.claude/commands/fe-planner.md`.
2. Produzir plano em `docs/architecture/frontend/plans/plan-<ISSUE_ID>.md`.
3. Checkpoint (`currentStep: "planner"`, `nextStep: "implement"`, `fase: 1`).
4. Prosseguir para B4 (fase-1).

### Etapa B4 -- Implement

1. Setar `status: "In Progress"` (YAML) e `**Status:** In Progress` (body) na issue.
2. Executar protocolo de `.claude/commands/fe-implement.md` para a fase atual.
3. Executar verificacao local (build + lint, conforme Etapa 4 do fe-implement).
4. Setar `status: "In Review"` (YAML) e `**Status:** In Review` (body) na issue.
5. Checkpoint (`currentStep: "implement"`, `nextStep: "validate"`, `fase: <N>`).
6. Prosseguir para B5.

### Etapa B5 -- Validacao (Validator Modo 3)

1. Executar protocolo de `.claude/commands/fe-validator.md`, Modo 3:
   - Gates: `nx lint`, `nx test`, `nx build`.
   - Verificar conformidade arquitetural (incluindo multi-empresa enforcement).
   - Atualizar issue (checklist + bloco de status).
2. Se gates passam E score >= 80 E checklist 100% DONE:
   - Setar `status: "Done"` (YAML) e `**Status:** Done` (body) na issue.
   - Ir para Finalizacao.
3. Se gates passam mas checklist incompleto:
   - Setar `status: "Ready"` (YAML) e `**Status:** Ready` (body) na issue (volta para fila).
   - Incrementar iteration.
   - Se iteration > 5: parar com safety cap (ver abaixo).
   - Checkpoint (`currentStep: "validate-partial"`, `nextStep: "decision"`).
   - Voltar para B2 (Decisao) e prosseguir automaticamente.
4. Se gates falham:
   - Setar `status: "In Progress"` (YAML) e `**Status:** In Progress` (body) na issue (retorna para correcao).
   - Checkpoint (`currentStep: "validate-failed"`, `nextStep: "decision"`, notes com erro).
   - Voltar para B2 (Decisao) com diagnostico do erro e prosseguir automaticamente.

### Finalizacao Pipeline B

```
Autopilot concluido para <ISSUE_ID>
Modulo: <MODULO>
Score de maturidade: <0-100> -- <Inicial | Parcial | Consistente | Maduro>
Done/Total: <X/Y>
Gates: lint OK | test OK | build OK
Multi-empresa enforcement: OK
Iteracoes: <N>
Issue encerrada. Checklist 100% DONE.
```

---

## Safety cap -- limite de iteracoes

Maximo de **5 iteracoes** do loop B2→B5 por invocacao. Se atingir o limite:

```
Safety cap atingido (5 iteracoes).
Score atual: <score>
Done/Total: <X/Y>
Ultimo gate: <resultado>

A issue nao esta concluida. Para continuar:
-> /fe-autopilot <ISSUE_ID> --resume
   (o contador reinicia ao retomar)
```

---

## Regras gerais

- **Nao duplicar logica dos sub-commands.** Ler e seguir o protocolo do `.md` referenciado.
- **Encadear etapas automaticamente.** Apos salvar checkpoint, prosseguir imediatamente
  para a proxima etapa na mesma invocacao. Nao instruir o usuario a executar `/clear`
  ou `--resume` no fluxo normal.
- **Sempre salvar checkpoint apos etapa pesada.** Serve como crash recovery e como
  ponto manual de `--resume`.
- **Criar diretorio de checkpoint** no inicio: `tmp/fe-autopilot/<ID>/`.
- **Se `--resume` e `state.json` nao existe**: tratar como fresh start.
- **Nao rodar etapas ja concluidas** -- usar checks de pre-requisito (arquivo existe?) para skip.
- **Multi-empresa enforcement** e parte do Validator Modo 3 (B5) -- nao pular.

---

## Impacto nos commands existentes

**ZERO.** Este command e aditivo puro:
- Nao modifica os 8 commands FE individuais.
- Delega para eles via leitura do `.md` referenciado.
- Os commands individuais continuam funcionando quando chamados diretamente.

---

## Mensagem inicial obrigatoria (ao comecar)

```
FE Autopilot iniciado
Input: <$ARGUMENTS>
Pipeline: <A (Architect) | B (Implement)>
ID: <ID>
Modo: <fresh | resume>
Estado: <checkpoint lido ou "novo">
Iniciando etapa: <nome>
```
