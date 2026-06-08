# FE UI Autopilot — UI Pipeline Orchestrator (Journey OS)

Orquestra o pipeline completo `fe-ui-*` para o módulo solicitado:
setup do design system → análise do protótipo → geração de issues → loop
de execução por onda de telas.

**Input:** `$ARGUMENTS` — módulo + onda opcional (ex.: `LEAD`, `LEAD onda-A`).

Formatos aceitos:
- `<MODULE>` — processa todas as ondas do módulo sequencialmente
- `<MODULE> onda-<X>` — processa apenas a onda especificada
- `<MODULE> --resume` — retoma de checkpoint salvo

Módulos válidos: WRKS, LEAD, JRNY, ASST, COMM, SALE, INTL, GWY, REG, MIG.

**Prerequisite:** prototype vendored at `prototipo/`
(run `sync-prototype.py sync` if not present).

---

## Princípio central

O autopilot **delega para os sub-commands existentes** (não duplica lógica).
Checkpoints são salvos após cada etapa pesada. O loop de execução para em gates
falhos e informa a próxima ação — não prossegue com telas seguintes se uma falha
blocking bloqueia o pipeline.

---

## Passo 0 — Detecção de modo

1. Extrair `$ARGUMENTS`.
2. Se contém `--resume`: ler checkpoint em `tmp/fe-ui-autopilot/<MODULE>/state.json`
   e pular para a etapa salva.
3. Se é `<MODULE>` válido (WRKS/LEAD/JRNY/ASST/COMM/SALE/INTL/GWY/REG/MIG):
   modo fresh. ID = `<MODULE>`.
4. Se é `<MODULE> onda-<X>`: modo onda única.
5. Se ambíguo: perguntar ao usuário.

Mensagem inicial obrigatória:

```
FE UI Autopilot iniciado
Módulo: <MODULE>
Modo: <fresh | resume | onda-única>
Onda: <todas | onda-X>
Estado: <checkpoint lido | novo>
Iniciando: <Setup ou etapa salva>
```

---

## Checkpoint — como funciona

Salvar em `tmp/fe-ui-autopilot/<MODULE>/state.json` após cada etapa:

```json
{
  "module":      "<MODULE>",
  "onda":        "<all | onda-A | onda-B | ...>",
  "currentStep": "<nome da etapa concluída>",
  "nextStep":    "<nome da próxima etapa>",
  "issuesGenerated": ["<ISSUE_ID-1>", "..."],
  "currentIssue": "<ISSUE_ID em execução>",
  "timestamp":   "2026-06-05T14:30:00Z",
  "notes":       "<contexto mínimo para retomar>"
}
```

Emitir linha de status curta e prosseguir imediatamente.

---

## Fase 1 — Setup do design system (uma vez por projeto)

Verificar se `docs/architecture/frontend/ui-design-system/ui-tokens-map.json` existe.

- **Existe:** pular para Fase 2.
- **Não existe:** executar protocolo de `.claude/commands/fe-ui-tokens.md`.

**Gate:** `docs/architecture/frontend/ui-design-system/ui-tokens.scss` presente +
`nx build journeyos-shared-ui-tokens` verde.

Checkpoint (`currentStep: "tokens"`, `nextStep: "map"`).

---

## Fase 2 — Análise do protótipo (uma vez por projeto)

Verificar se `docs/architecture/frontend/prototype-map.json` existe e tem
entradas para o módulo `<MODULE>`.

- **Existe e tem entradas:** pular para Fase 3.
- **Não existe ou vazio:** executar protocolo de `.claude/commands/fe-ui-map.md`.

**Gate:** `prototype-map.json` gerado + todas as telas de `<MODULE>` com
`module` e `ngComponent` preenchidos + revisão humana confirmada.

Checkpoint (`currentStep: "map"`, `nextStep: "backlog"`).

---

## Fase 3 — Geração de issues (por módulo)

Verificar se já existem issues `JOS-<MODULE>-FE-*` em
`docs/architecture/frontend/issues/`.

- **Existem:** pular para Fase 4.
- **Não existem:** executar protocolo de `.claude/commands/fe-ui-backlog.md`
  com input `<MODULE>`.

**Gate:** issues geradas com numeração contínua + `raw/` populado +
`issues-map.md` atualizado.

Checkpoint (`currentStep: "backlog"`, `nextStep: "exec-onda-A"`).

---

## Fase 4 — Loop de execução (por onda de telas)

As ondas seguem a sequência de complexidade crescente (P1 → P2 → P4 → P6/P7):

| Onda | Padrões | Critério |
|---|---|---|
| onda-A | P1 (list/grid) | Mais simples — valida o caminho inteiro |
| onda-B | P2 (detail/tabs), P4 (dashboard) | Componentes compostos |
| onda-C | P3 (fila/feed), P5 (tree/admin) | Layouts especializados |
| onda-D | P6 (kanban), P7 (canvas/builder), chat, stepper | Signature — custo alto |

Para cada onda selecionada, executar o loop por issue:

### Loop por issue

1. **Selecionar próxima issue** da onda (por ordem de `issues-map.md`).
2. **Executar protocolo `/fe-validator <ISSUE_ID>`** (Modo 1 — BASELINE).
3. Se score >= 80 e checklist 100% DONE: marcar issue como concluída e avançar.
4. **Executar protocolo `/fe-planner <ISSUE_ID>`** (UI mode se `.contract.json` existir).
5. **Executar protocolo `/fe-implement <ISSUE_ID> fase-UI-0`** (SCSS port).
6. **Executar protocolo `/fe-implement <ISSUE_ID> fase-UI-1`** (Component scaffold).
7. **Executar protocolo `/fe-implement <ISSUE_ID> fase-UI-2`** (Data-access stub).
8. **Executar protocolo `/fe-validator <ISSUE_ID>`** (Modo 3 — VALIDAÇÃO):
   - Gates: `nx lint`, `nx test`, `nx build`.
   - Gate UI: `fe-ui-fidelity-check.py check --issue <ISSUE_ID> ...`.
9. Se gates passam e score >= 80: checkpoint (`currentIssue`, `nextStep: "next-issue"`)
   e avançar para próxima issue.
10. Se gates falham: checkpoint com diagnóstico + parar o loop desta onda.
    Instruir: `/fe-ui-autopilot <MODULE> --resume` após correção manual.

### Safety cap

Máximo de **5 iterações** do loop Planner→Implement→Validator por issue.
Se atingido, parar e reportar para o usuário.

### Checkpoint de onda

Após completar todas as issues de uma onda:

```
Onda <X> concluída — módulo <MODULE>
Issues: JOS-<MODULE>-FE-<START>..<END> (<N> issues)
Gates: lint OK | test OK | build OK | fidelidade OK
Próxima onda: <onda-B | concluído>
```

---

## Finalização

```
FE UI Autopilot concluído (Journey OS)
Módulo: <MODULE>

Setup:    tokens OK | map OK | backlog <N> issues
Ondas:    <lista de ondas executadas>
Issues:   JOS-<MODULE>-FE-<START>..<END>
Score médio: <0-100>
Fidelidade UI: <OK | WARN: N>

Para implementar o próximo módulo:
-> /fe-ui-autopilot <NEXT_MODULE>
```

---

## Regras gerais

- **Não duplicar lógica dos sub-commands.** Ler e seguir o protocolo do `.md`
  referenciado.
- **Não prosseguir com a próxima issue se a atual tem gate blocking.** Parar a
  onda e instruir `--resume` após correção.
- **Não pular Fase 1 (tokens) nem Fase 2 (map)** se os artefatos não existirem
  — eles são prerequisitos do loop.
- **Issues de ondas posteriores não são processadas** enquanto a onda atual
  tiver issues com falha blocking.
- **Multi-empresa:** o gate do `/fe-validator` já cobre. Não verificar duplamente.
