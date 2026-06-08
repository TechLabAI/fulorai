# Aprendizado — Architecture Autopilots + Master Plan + Checkpoints em `/tmp`

> **Destino:** o projeto que **gera** o Journey OS (o gerador/template de monorepos).
> **Origem:** evolução real do Journey OS durante a fase de arquitetura (Layer 1 — Architect).
> **O que é:** um padrão validado que deve passar a ser **emitido por padrão** pelo gerador, não
> reconstruído à mão a cada novo projeto.
>
> Status: rascunho para revisão / backport. Mover para o repositório do gerador quando aprovado.

---

## 1. Contexto / problema que esse padrão resolve

O pipeline de criação de um módulo backend/frontend tem **5 etapas pesadas** (vision → specs →
[specs-validate] → backlog → scaffold/e2e). Sem orquestração:

- O usuário precisava invocar 5 commands em sequência, lembrando a ordem e os pré-requisitos.
- Uma interrupção de sessão (`/clear`, crash, limite de contexto) **perdia o progresso** — não
  havia como saber em que etapa um módulo parou nem retomar de onde estava.
- O acompanhamento global ("quais dos 10 módulos já têm scaffold?") era feito **na cabeça** ou
  em um arquivo atualizado **à mão**, que envelhecia e divergia da realidade dos arquivos.

O padrão abaixo resolve os três pontos com **um único artefato por camada** (BE e FE).

---

## 2. O aprendizado (4 partes)

### 2.1. Architecture Autopilots (BE + FE) — meta-orquestradores da camada de arquitetura

Dois commands que **encadeiam, numa única invocação**, as etapas do Architect e **param antes**
da implementação (Layer 2):

| Command | Cadeia de etapas | Para em |
|---|---|---|
| `/be-architecture-autopilot <MODULO>` | vision → specs → specs-validate → backlog → scaffold | scaffold |
| `/fe-architecture-autopilot <MODULO>` | vision → specs → backlog → scaffold → e2e-validate | e2e-validate |

Princípios não-negociáveis (ambos):

- **Não duplicar lógica.** O autopilot **lê e segue** o protocolo de cada sub-command (`*-architect-*.md`);
  ele só orquestra. Aditivo puro: **zero** alteração nos commands individuais, que continuam
  funcionando isolados.
- **Read-only sobre o repo de código.** Toda escrita em `backend/services/` ou `apps/`+`libs/`
  acontece via os scripts/plugins dos sub-commands (Python no BE, Nx no FE). O autopilot só
  escreve em dois lugares: o **checkpoint** (`/tmp/...`) e o **master plan**.
- **Encadeamento no caminho feliz.** Após cada etapa, prossegue imediatamente na mesma invocação;
  **não** manda o usuário rodar `/clear` ou `--resume` no fluxo normal.
- **Skip idempotente.** Cada etapa tem um *skip check* (o artefato-âncora já existe? → pula);
  `--force` desativa o skip (re-arquitetura).
- **Propaga bloqueios sem mascarar.** Se um sub-command devolve "documentação incompleta", o
  autopilot registra `bloqueado` no master plan e para com diagnóstico — **não inventa valores**.
- **Para na fronteira da arquitetura.** Após scaffold (BE) / e2e-validate (FE), aponta a próxima
  ação manual (`/be-autopilot --implement`, `/fe-validator ...`) e encerra.

Flags padronizadas (ambos): `--resume`, `--force`, `--until=<etapa>`, `--dry-run`.

Diferença estrutural FE×BE que o gerador precisa conhecer: o FE **não tem** `specs-validate`
(EARS→BDD) — os cenários e2e já nascem Gherkin puro no SPEC-08. Em troca, o FE ganha uma etapa
final **`e2e-validate` inline** (sem sub-command próprio): um gate read-only que confirma que os
specs Playwright compilam/são descobríveis (`nx e2e --list`), análogo ao "gate de specs-validate
deferido" do BE (que roda `compileTestJava` + `*CucumberIT*` só **depois** do scaffold, pois
depende do `build.gradle.kts`).

### 2.2. Architecture Master Plan (BE + FE) — espelho global de progresso

Um arquivo **global por camada**, rastreando todos os módulos:

- `docs/architecture/backend/plans/architecture-master-plan.md`
- `docs/architecture/frontend/plans/architecture-master-plan.md`

Regra de ouro: **é um espelho de progresso, nunca a fonte da verdade.** A verdade são os arquivos
em `docs/architecture/...` e em `backend/services/` / `apps/`+`libs/`. O master plan pode ser
reconstruído a partir do disco.

Estrutura canônica = **tabela de status por módulo** + **log cronológico append-only**.

BE — colunas: `Modulo | Servico | Vision | Specs | Specs-Validate | Backlog | Scaffold | Atualizado`
FE — colunas: `Modulo | Tool | Vision | Specs | Backlog | Scaffold | E2E-Validate | Atualizado`
Legenda comum: `pendente | em andamento | OK | bloqueado | N/A`.

Módulos de infraestrutura (GWY/REG/MIG) registram **`N/A`** (não `pendente`) nas etapas que não se
aplicam (ex.: specs-validate/e2e-validate), para o plano refletir o escopo real.

### 2.3. Instrução: o autopilot atualiza o master plan a CADA mudança de fase

Esta é a parte que **costuma ser esquecida** e precisa estar explícita no command gerado.
Sequência obrigatória por etapa: **(1) executa o sub-command → (2) salva checkpoint → (3) atualiza
o master plan → (4) prossegue.** A ordem importa (checkpoint antes do master plan).

Regras de atualização (idempotentes):

- **Tabela:** uma linha por `<MODULO>`. **Antes** de iniciar a etapa, marcar a célula como
  `em andamento`; **ao concluir**, `OK` (ou `bloqueado`/`N/A`). Atualizar a coluna `Atualizado`
  (`YYYY-MM-DD`). **Nunca duplicar a linha** — editar a existente.
- **Log:** **append-only**, uma linha por transição:
  ```
  - <ISO-8601> -- <MODULO> -- <etapa> -- <inicio|OK|bloqueado|N/A|gate-fail> -- <nota curta>
  ```
  Ex.: `- 2026-06-04T14:30:00Z -- WRKS -- vision -- OK -- docs 01..06 + 5 ADR`

### 2.4. Checkpoints em `/tmp` — crash recovery e `--resume`

Após cada etapa pesada, gravar estado em:

- BE: `tmp/be-architecture-autopilot/<MODULO>/state.json`
- FE: `tmp/fe-architecture-autopilot/<MODULO>/state.json`

Schema do `state.json`:

```json
{
  "id": "<MODULO>",
  "pipeline": "architecture",
  "modulo": "<MODULO>",
  "service": "<service>",          // BE: "service"; FE: "tool"
  "type": "standard | gateway | registry",
  "currentStep": "<etapa concluida>",
  "nextStep": "<proxima etapa | done | blocked>",
  "timestamp": "<ISO-8601>",
  "notes": "<contexto minimo para retomar (ex.: gate=deferido, N cenarios)>"
}
```

Após salvar, emitir status curto (`Checkpoint: <currentStep> -> <nextStep>`) e prosseguir.
A invocação só **encerra** em 3 casos: bloqueio (`nextStep: "blocked"`), parada solicitada
(`--until`), ou finalização (`nextStep: "done"`). `--resume` lê o `state.json` e retoma de `nextStep`.

> `/tmp` aqui é o `tmp/` **do repositório do projeto gerado**, e deve estar no `.gitignore` —
> são artefatos efêmeros de execução, não versionados.

---

## 3. O que o gerador deve emitir por padrão

1. **Os dois commands** `.claude/commands/be-architecture-autopilot.md` e
   `fe-architecture-autopilot.md`, parametrizados pelo registry de módulos do projeto
   (`project-context.json.modules.registry`) e pelas etapas da camada (BE tem specs-validate; FE
   tem e2e-validate).
2. **Os dois master plans vazios**, já com o **cabeçalho gerenciado pelo autopilot** (ver §4) e a
   tabela com **uma linha por módulo do registry** em estado `pendente` (ou `N/A` para infra).
3. Entrada no `.gitignore` para `tmp/*-architecture-autopilot/`.

---

## 4. Gotcha encontrado em campo (corrigir no gerador)

O master plan BE que existe hoje no Journey OS foi criado **à mão** e traz no cabeçalho:

> "Atualizar **manualmente** conforme cada etapa for concluída."

Isso **contradiz** a especificação do autopilot, cujo cabeçalho canônico é:

> "Atualizado **automaticamente** pelo `/be-architecture-autopilot` a cada etapa concluída.
> NÃO editar à mão durante uma corrida do autopilot."

**Lição:** o gerador deve emitir o master plan **já com o cabeçalho gerenciado-pelo-autopilot**
(e com tabela/log nas colunas canônicas da §2.2), para o documento e o command não nascerem
divergentes. Um master plan herdado de "edição manual" induz o usuário a editar à mão um arquivo
que o autopilot vai sobrescrever — fonte de conflito e de tabelas com formatos diferentes entre BE
e FE.

---

## 5. Referências (no Journey OS, snapshot de origem)

- `.claude/commands/be-architecture-autopilot.md` — protocolo completo (A1–A5, checkpoint, master plan).
- `.claude/commands/fe-architecture-autopilot.md` — idem FE (com etapa e2e-validate inline).
- `docs/architecture/backend/plans/architecture-master-plan.md` — instância BE (com o cabeçalho legado a corrigir).
- `tmp/be-architecture-autopilot/<MODULO>/state.json` — exemplos reais de checkpoint dos 10 módulos.
