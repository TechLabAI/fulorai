# BE Autopilot -- Meta-Orchestrator (Journey OS)

Voce e o orquestrador central do pipeline IA-First do backend Journey OS (Java + Spring Boot, arquitetura hexagonal).

Detecta o estado do modulo, executa o pipeline correto (Architect ou Implement) e
salva checkpoints (crash recovery + retomada manual via `--resume`).

**Input:** `$ARGUMENTS`

Formatos aceitos:
- `<MODULO>` (ex.: `WRKS`) → detecta automaticamente: se o modulo ainda nao tem scaffold → **Pipeline A** (Architect); se ja tem → **Pipeline B** (Implement, loop validator-driven).
- `<MODULO> --architect` → forca **Pipeline A** (re-arquitetar / novo modulo).
- `<MODULO> --implement` → forca **Pipeline B** (ciclo de desenvolvimento).
- `<MODULO> --resume` → retomar de checkpoint salvo.

Modulos validos: WRKS | LEAD | JRNY | ASST | COMM | SALE | INTL | GWY | REG | MIG

---

## Principio central

**Uma unica chamada para resolver tudo.** O autopilot delega para os sub-commands
existentes (`be-architect-*`, `be-validator`, `be-planner`, `be-implement`) -- nao
duplica logica -- e encadeia as etapas automaticamente em uma unica invocacao.
Checkpoints sao salvos em disco apos cada etapa pesada para permitir retomada se a
sessao for interrompida, mas o autopilot **NAO interrompe o fluxo do usuario**:
prossegue para a proxima etapa imediatamente.

---

## Passo 0 -- Deteccao de modo

1. Extrair `<MODULO>` e flags de `$ARGUMENTS`.
2. Validar que `<MODULO>` esta no registry (WRKS/LEAD/JRNY/ASST/COMM/SALE/INTL/GWY/REG/MIG). Se invalido: listar os validos e parar.
3. Se contem `--resume`: ler checkpoint em `tmp/be-autopilot/<MODULO>/state.json` e pular para a etapa salva.
4. Se contem `--architect`: **Pipeline A**.
5. Se contem `--implement`: **Pipeline B**.
6. Caso contrario, detectar pelo estado em disco:
   - Se `backend/services/<service>/` NAO existe (modulo ainda nao scaffoldado) → **Pipeline A**, e ao terminar, encadear para **Pipeline B**.
   - Se ja existe → **Pipeline B**.
7. ID do checkpoint = `<MODULO>`.

> `<service>` = nome do servico backend do modulo (default `<modulo-lowercase>-service`), conforme `modules.registry` em `project-context.json`.

---

## Checkpoint -- como funciona

Apos cada etapa pesada, salvar estado em `tmp/be-autopilot/<MODULO>/state.json`:

```json
{
  "id": "<MODULO>",
  "pipeline": "architect | implement",
  "modulo": "<MODULO>",
  "service": "<service>",
  "currentStep": "<nome da etapa concluida>",
  "nextStep": "<nome da proxima etapa>",
  "progressUnit": "P1",
  "iteration": 1,
  "timestamp": "2026-05-19T14:30:00Z",
  "notes": "<contexto minimo para retomar>"
}
```

Apos salvar, emitir linha de status curta e prosseguir:

```
Checkpoint: <currentStep> -> <nextStep> (progressUnit=<P>, iter=<N>)
```

O autopilot encerra a invocacao apenas em 3 casos:
- **Safety cap** atingido (5 iteracoes do loop B2->B5).
- **Erro irrecuperavel** ou intervencao manual obrigatoria (`nextStep: "blocked"`).
- **Finalizacao** da pipeline.

Nesses casos, reportar o motivo e instruir `/be-autopilot <MODULO> --resume` se cabivel.

---

## Pipeline A -- Architect (novo modulo / re-arquitetura)

Input: `<MODULO>`. Produz docs 01..06 + ADR skeleton, contratos, backlog e o
esqueleto executavel do servico.

### Etapa A1 -- Vision

1. Verificar se `docs/architecture/backend/services/<service>/01-*.md` ja existe.
   - Se existe e completo: pular para A2.
2. Executar protocolo de `.claude/commands/be-architect-vision.md` com `<MODULO>`.
3. Checkpoint (`currentStep: "vision"`, `nextStep: "specs"`).
4. Prosseguir automaticamente para A2.

### Etapa A2 -- Specs

1. Verificar pre-requisito: docs 01..06 do modulo existem.
2. Verificar se os contratos (`api`, `data-model`, `events`) ja existem.
   - Se existem: pular para A3.
3. Executar protocolo de `.claude/commands/be-architect-specs.md` com `<MODULO>`.
4. Checkpoint (`currentStep: "specs"`, `nextStep: "backlog"`).
5. Prosseguir para A3.

### Etapa A3 -- Backlog

1. Verificar pre-requisito: contratos do modulo existem.
2. Verificar se `plan-<MODULO>.md` + issues ja existem.
   - Se existem: pular para A4.
3. Executar protocolo de `.claude/commands/be-architect-backlog.md` com `<MODULO>`.
4. Checkpoint (`currentStep: "backlog"`, `nextStep: "scaffold"`).
5. Prosseguir para A4.

### Etapa A4 -- Scaffold

1. Verificar pre-requisitos: issues atomicas + `plan-<MODULO>.md`.
2. Executar protocolo de `.claude/commands/be-architect-scaffold.md` com `<MODULO>`
   (o script Python gera o esqueleto executavel do servico; o autopilot NAO gera arquivos).
3. Checkpoint (`currentStep: "scaffold"`, `nextStep: "implement-loop"`).
4. Ir para Pipeline B (Etapa B1) automaticamente -- o modulo agora tem scaffold.

### Finalizacao Pipeline A (quando rodado com `--architect`, sem encadear)

```
Pipeline Architect concluido para <MODULO> (<service>)
Etapas executadas: vision -> specs -> backlog -> scaffold
Para iniciar o ciclo de desenvolvimento:
-> /be-autopilot <MODULO> --implement
```

---

## Pipeline B -- Implement (ciclo validator-driven)

Input: `<MODULO>` ja scaffoldado. Itera sobre as prioridades do plano ate o checklist
fechar ou o safety cap ser atingido.

### Etapa B1 -- Baseline (Validator Modo 1)

1. Executar protocolo de `.claude/commands/be-validator.md`, **Modo 1 (BASELINE)**:
   - Consolidar estado real de cada item do checklist do modulo.
   - Calcular score de maturidade (0-100).
   - Atualizar o plano/issues com bloco de status.
2. Se score >= 80 e checklist 100% DONE: ir para Finalizacao.
3. Checkpoint (`currentStep: "baseline"`, `nextStep: "decision"`, notes com score e done/total).
4. Prosseguir para B2.

### Etapa B2 -- Decisao (Validator Modo 2)

1. Com base no estado consolidado, decidir a proxima acao:
   - **PLANNER** → ir para B3
   - **IMPLEMENTADOR** → ir para B4
   - **VALIDAR** → ir para B5
   - **ENCERRAR** → Finalizacao
2. Nao salvar checkpoint aqui (etapa leve). Prosseguir imediatamente.

### Etapa B3 -- Planner

1. Executar protocolo de `.claude/commands/be-planner.md` com `<MODULO>`.
2. Produzir/atualizar `plan-<MODULO>.md` (prioridades detalhadas P1, P2, ...).
3. Checkpoint (`currentStep: "planner"`, `nextStep: "implement"`, `prioridade: "<P alvo>"`).
4. Prosseguir para B4 com a prioridade alvo.

### Etapa B4 -- Implement (uma prioridade por vez)

1. Executar protocolo de `.claude/commands/be-implement.md` com `<MODULO> <PRIORIDADE>`.
   - Implementar **uma unica prioridade**, seguindo exatamente a ordem das fases do plano.
2. Seguir a verificacao local prevista no be-implement (o be-implement **NAO** roda `./gradlew`).
3. Checkpoint (`currentStep: "implement"`, `nextStep: "validate"`, `prioridade: "<P>"`).
4. Prosseguir para B5.

### Etapa B5 -- Validacao (Validator Modo 3)

1. Executar protocolo de `.claude/commands/be-validator.md`, **Modo 3 (VALIDACAO)**:
   - Gates de build/teste do servico.
   - Conformidade arquitetural (hexagonal + enforcement multi-empresa).
   - Atualizar checklist + bloco de status.
2. Se gates passam E score >= 80 E checklist 100% DONE: ir para Finalizacao.
3. Se gates passam mas checklist incompleto:
   - Incrementar `iteration`.
   - Se `iteration` > 5: parar com safety cap (ver abaixo).
   - Checkpoint (`currentStep: "validate-partial"`, `nextStep: "decision"`).
   - Voltar para B2 (Decisao) e prosseguir automaticamente (proxima prioridade).
4. Se gates falham:
   - Checkpoint (`currentStep: "validate-failed"`, `nextStep: "decision"`, notes com erro).
   - Voltar para B2 (Decisao) com o diagnostico do erro e prosseguir automaticamente.

### Finalizacao Pipeline B

```
Autopilot concluido para <MODULO> (<service>)
Score de maturidade: <0-100> -- <Inicial | Parcial | Consistente | Maduro>
Done/Total: <X/Y>
Gates: build OK | test OK
Arquitetura hexagonal: OK
Multi-empresa enforcement: OK
Iteracoes: <N>
Modulo com checklist 100% DONE.
```

---

## Safety cap -- limite de iteracoes

Maximo de **5 iteracoes** do loop B2→B5 por invocacao. Se atingir o limite:

```
Safety cap atingido (5 iteracoes).
Score atual: <score>
Done/Total: <X/Y>
Ultimo gate: <resultado>

O modulo nao esta concluido. Para continuar:
-> /be-autopilot <MODULO> --resume
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
- **Criar diretorio de checkpoint** no inicio: `tmp/be-autopilot/<MODULO>/` (versionado, D-041).
- **Se `--resume` e `state.json` nao existe**: tratar como fresh start.
- **Nao rodar etapas ja concluidas** -- usar checks de pre-requisito (arquivo existe?) para skip.
- **Uma prioridade por vez** no B4 -- nunca misturar prioridades numa mesma invocacao do be-implement.
- **Multi-empresa enforcement** e parte do Validator Modo 3 (B5) -- nao pular.

---

## Impacto nos commands existentes

**ZERO.** Este command e aditivo puro:
- Nao modifica os commands BE individuais (`be-architect-*`, `be-validator`, `be-planner`, `be-implement`).
- Delega para eles via leitura do `.md` referenciado.
- Os commands individuais continuam funcionando quando chamados diretamente.

---

## Mensagem inicial obrigatoria (ao comecar)

```
BE Autopilot iniciado
Input: <$ARGUMENTS>
Pipeline: <A (Architect) | B (Implement)>
Modulo: <MODULO> (<service>)
Modo: <fresh | resume>
Estado: <checkpoint lido ou "novo">
Iniciando etapa: <nome>
```
