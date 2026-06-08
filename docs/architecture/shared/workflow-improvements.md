# Workflow de Commands — Achados & Melhorias Propostas

> **Tipo:** análise transversal (BE + FE + scripts). **Status:** somente análise — nenhuma
> alteração em `.claude/commands/*` ou `scripts/*` foi feita a partir deste documento.
> **Origem:** primeiro uso real dos autopilots de arquitetura (`/be-architecture-autopilot` e
> `/fe-architecture-autopilot`) na Fase 1, rodando vision→specs→backlog→scaffold para os 10 módulos
> (WRKS, LEAD, JRNY, ASST, COMM, SALE, INTL, GWY, REG, MIG).

## Por que este documento existe

A Fase 1 (Arquitetura) exercitou o pipeline de commands de ponta a ponta pela primeira vez. Esse
uso real expôs atritos no workflow e nos geradores Python. Parte já está registrada de forma
dispersa — memórias do agente, `_inbox/LEARNING-*.md`, e notas `gate-deferido`/`bloqueado`
espalhadas nas seções por-módulo dos master-plans. **Faltava um documento único** que consolidasse
os achados e propusesse melhorias acionáveis. É o que este arquivo faz.

Cada achado segue o formato **Esperado → Observado → Onde dói → Melhoria proposta → Prioridade**.
Nenhuma melhoria vem com código pronto — apenas a direção da mudança e o(s) arquivo(s) que seriam
tocados numa implementação futura. As prioridades (P1/P2/P3) são consolidadas na Seção 6.

---

## 0. Sumário executivo

| # | Achado | Área | Sintoma | Melhoria | Prio |
|---|--------|------|---------|----------|------|
| A1 | Gradle ausente, gates silenciosamente diferidos | Toolchain | `compileJava`/ArchUnit/BDD não rodaram nos 10 serviços | Preflight + ledger de gates diferidos | **P1** |
| A2 | Scripts assumem binários sem preflight | Toolchain | Falha "command not found" só na execução | `shutil.which()` no início + matriz de capacidade | **P1** |
| A3 | Erro de subprocess só avisa, não para | Toolchain | Scaffold parcial silencioso | Fail-fast opt-in (`--continue-on-error` explícito) | P2 |
| A4 | `specs-validate` depende do skeleton | Toolchain | Gate empurrado de A3→A5, deferral confuso | Rodar após scaffold (determinístico) | P2 |
| B1 | `@Entity` duplicado (module vs entity-gen) | Geradores | Duas árvores de entidade / overwrite com `--force` | Fonte única + gate de validação config↔SQL | **P1** |
| B2 | Templates `.j2` vs strings inline divergem | Geradores | Mesma entidade renderizada por 2 caminhos | Convergir entity-gen para `.j2` | P2 |
| C1 | Schema de checkpoint divergente BE/FE | Consistência | `iteration` (BE) vs `fase` (FE) | Padronizar `state.json` | P2 |
| C2 | Vocabulário herdado não migrado | Consistência | `@hub/internal:tool` vs `@journeyos/internal:module` | Concluir migração + renomear referências | P3 |
| C3 | BE sem pipeline de feature | Consistência | Assimetria ao evoluir módulo pós-MVP | Avaliar família `be-feature-architect-*` | P3 |
| C4 | Gate EARS só no BE | Consistência | SPEC FE sem critérios de aceite sistemáticos | Equivalente `fe-specs-validate` | P3 |
| D1 | Header do master-plan contradiz o autopilot | Master-plan | Usuário induzido a editar à mão arquivo auto-sobrescrito | Gerador emite header "auto-gerenciado" | **P1** |
| D2 | Master-plan atualizado só no fim | Master-plan | Perda de rastro em crash no meio da corrida | Atualizar por fase, após checkpoint | **P1** |
| D3 | Gates diferidos sem ledger | Master-plan | Marcadores espalhados, sem índice nem replay | Ledger consolidado + comando `*-gates-replay` | **P1** |

Itens contextuais (registrar, não "consertar"): TechLab AI bloqueado (E1) e
`fe-prototype-analyzer` com 0 telas (E2) — Seção 5.

---

## 1. Robustez de toolchain (ambiente)

O ambiente de execução da Fase 1 não tinha o toolchain completo (sem Gradle no PATH, Docker
desligado). Os commands não anteciparam isso de forma uniforme: alguns gates foram diferidos com
nota, outros teriam falhado bruscamente se acionados.

### A1 — Gradle ausente, gates pós-scaffold silenciosamente diferidos — **P1**

- **Esperado:** após o scaffold, rodar `compileJava` + `architectureCheck` (ArchUnit
  RULE-01..09) + BDD Cucumber, validando o serviço recém-gerado.
- **Observado:** sem `gradlew`/Gradle no PATH, nenhum dos 10 serviços teve esses gates executados.
  O fato vira uma nota `gate-deferido`/`gate-diferido` dispersa nas seções por-módulo do
  master-plan (MIG, GWY, WRKS, ASST, LEAD, COMM, SALE, INTL).
- **Onde dói:** `/be-architect-scaffold`, `/be-architecture-autopilot` (fases pós-scaffold);
  `backend/services/*` ficam sem verificação arquitetural imediata.
- **Melhoria proposta:** ver A2 (preflight) + Seção 4/D3 (ledger consolidado com comando de
  recuperação anexado a cada gate). Em vez de uma nota solta por módulo, um índice único de
  "gates pendentes + como rodar".
- **Fontes:** memória `[[gradle-toolchain-absent]]`; `docs/architecture/backend/plans/architecture-master-plan.md`.

### A2 — Scripts assumem binários sem preflight — **P1**

- **Esperado:** o command detecta cedo se o toolchain necessário existe e ajusta o plano
  (rodar agora vs. diferir).
- **Observado:** `be-module-generator.py`, `be-smoke-scaffold.py` e `fe-module-generator.py`
  invocam `gradlew`/`npx`/`nx`/`openapi-generator-cli` sem checar disponibilidade antes; a falha só
  aparece como "command not found" no meio da execução. `be-smoke-scaffold.py` chega a checar
  `gradlew` (`wrapper.is_file()` → status `skipped`), mas é a exceção, não o padrão.
- **Onde dói:** todos os `*-scaffold` e os autopilots.
- **Melhoria proposta:** passo **preflight/doctor** no início de `*-scaffold` e dos autopilots
  (via `shutil.which()` para cada binário esperado) que grava uma **matriz de capacidade** — o que
  pode rodar agora e o que será diferido — consumida pelas fases seguintes.

### A3 — Erro de subprocess só avisa, não para — P2

- **Esperado:** um sub-gerador que falha aborta o scaffold (ou exige flag explícita para
  continuar), evitando estado parcial.
- **Observado:** em `be-module-generator.py`, quando um sub-gerador (migration/entity/bdd) retorna
  código ≠ 0, emite-se `[WARN]` e o fluxo segue → scaffold parcial silencioso.
- **Onde dói:** `/be-architect-scaffold` e seu encadeamento de sub-geradores.
- **Melhoria proposta:** **fail-fast por padrão** com `--continue-on-error` explícito quando o
  parcial for desejado.

### A4 — `specs-validate` (EARS→BDD) depende do skeleton — P2

- **Esperado:** validar EARS→BDD (`be-spec-to-bdd.py`) como gate entre specs e backlog (D-218).
- **Observado:** a geração precisa de `build.gradle.kts` e da estrutura de pacotes, que só existem
  pós-scaffold → o gate é empurrado de A3 para A5, com lógica de deferral confusa (ex.: WRKS com
  "104 SHALL clauses / 26 cenários BDD já autorais; geração `be-spec-to-bdd.py` DEFERIDA p/ A5").
- **Onde dói:** `/be-architect-specs-validate`, `/be-architecture-autopilot`.
- **Melhoria proposta:** reposicionar o gate para rodar **determinísticamente após o scaffold**
  (ou exigir um skeleton-lite antes), eliminando a ambiguidade de "quando o gate realmente passa".

---

## 2. Dedup de geradores (be-module vs be-entity)

### B1 — `@Entity` duplicado — **P1**

- **Esperado:** uma definição canônica de entidade JPA por agregado.
- **Observado:** `be-module-generator.py` (~linhas 1822-1829) emite `*JpaEntity.java` a partir de
  `generator-config.yml` (`domain_aggregates`/`domain_entities`); o encadeado
  `be-entity-generator.py` (~linhas 1472-1479) emite `*Entity.java` a partir do `V1__*.sql`. **Não
  há validação** de que os nomes derivados do config batem com os derivados do SQL → resultam duas
  árvores de entidade (nomes diferentes) ou overwrite silencioso com `--force`. Confirmado no
  **INTL**: "duplicate `@Entity`/port/adapter (base `*JpaEntity` + entity-gen `*Entity`; base
  canônica)".
- **Onde dói:** `/be-architect-scaffold` (encadeamento module→migration→entity).
- **Melhoria proposta:**
  - **Fonte única de verdade** da camada JPA: o módulo standard emite apenas o stub-base e o
    entity-gen é o canônico (convenção já registrada em memória) — ou o inverso, mas **escolher um**.
  - **Gate de validação config↔SQL** antes de encadear o entity-gen, abortando em colisão de nome
    em vez de sobrescrever silenciosamente.
- **Fontes:** memória `[[toolchain-entity-generator-conflict]]`; seção INTL do master-plan BE.

### B2 — Templates `.j2` vs strings inline divergem — P2

- **Esperado:** uma superfície de manutenção para o código gerado.
- **Observado:** `be-module-generator` usa templates Jinja2 (`templates/operational/code/`);
  `be-entity-generator` e `be-scaffold` usam strings Python inline. A mesma entidade é renderizada
  por dois caminhos distintos — manutenção duplicada e risco de divergência sutil.
- **Onde dói:** `scripts/be-entity-generator.py`, `scripts/be-scaffold.py`.
- **Melhoria proposta:** convergir o entity-gen (e o scaffold) para os `.j2` de
  `templates/operational/code/`, unificando o ponto de manutenção.

---

## 3. Consistência BE/FE

Os pipelines BE e FE foram concebidos como espelhos, mas o uso real revelou divergências.

### C1 — Schema de checkpoint divergente — P2

- **Esperado:** o `state.json` de checkpoint (resume/crash-recovery) tem o mesmo formato em BE e FE.
- **Observado:** o checkpoint BE usa `iteration`; o FE usa `fase`. Mesma semântica, campos
  diferentes → manutenção duplicada nos dois autopilots.
- **Onde dói:** `tmp/be-autopilot/<MOD>/state.json`, `tmp/fe-autopilot/<ID>/state.json`.
- **Melhoria proposta:** **padronizar o schema de checkpoint** (mesmos nomes de campo) entre BE e FE.

### C2 — Vocabulário herdado não migrado — P3

- **Esperado:** vocabulário único `module/@journeyos/module-pattern` em commands, docs e artefatos.
- **Observado:** o vocabulário legado `tool/@hub/tax-map` ainda aparece; comandos `fe-architect-*`
  e artefatos referenciam `@hub/internal:tool` enquanto o plugin real é `@journeyos/internal:module`.
  A renomeação está marcada como pendente no master-plan FE.
- **Onde dói:** `.claude/commands/fe-architect-*.md`, docs FE, `nx.json`/plugins.
- **Melhoria proposta:** concluir a migração de vocabulário e renomear todas as referências
  `@hub/internal:tool` → `@journeyos/internal:module`.
- **Fontes:** memória `[[fe-scaffold-toolchain-absent]]`; master-plan FE.

### C3 — BE sem pipeline de feature — P3

- **Esperado:** simetria para evoluir um módulo existente com uma nova feature.
- **Observado:** o FE tem a família `fe-feature-architect-*`
  (discover→spec-delta→backlog→scaffold) para trabalho incremental; o BE só opera em nível de
  serviço → adicionar feature pós-MVP no BE é mais pesado.
- **Onde dói:** ausência em `.claude/commands/` (não há `be-feature-architect-*`).
- **Melhoria proposta:** avaliar criar **`be-feature-architect-*`** espelhando o FE (backlog).

### C4 — Gate EARS só no BE — P3

- **Esperado:** critérios de aceite sistemáticos (EARS) validados nos dois lados.
- **Observado:** `/be-architect-specs-validate` valida EARS→BDD; no FE não há equivalente —
  SPEC-01..07 não têm validação sistemática de critérios de aceite (apenas SPEC-08 Gherkin, escrito
  à mão).
- **Onde dói:** pipeline FE de specs.
- **Melhoria proposta:** estender as specs FE para notação EARS em SPEC-01..07 e validar a sintaxe
  antes do spec-delta (equivalente `fe-specs-validate`).

---

## 4. Gestão do master-plan

O master-plan é o artefato de status global por camada (BE/FE), mantido pelos autopilots. Três
atritos apareceram.

### D1 — Header contradiz o autopilot — **P1**

- **Esperado:** o master-plan declara que é auto-gerenciado pelo autopilot.
- **Observado:** o master-plan BE foi criado **à mão** com o header "Atualizar **manualmente**
  conforme cada etapa for concluída" — que **contradiz** o protocolo do autopilot ("Atualizado
  **automaticamente** … NÃO editar à mão durante uma corrida"). Isso induz o usuário a editar à mão
  um arquivo que o autopilot vai sobrescrever — fonte de conflito e de tabelas com formatos
  diferentes entre BE e FE.
- **Onde dói:** `docs/architecture/backend/plans/architecture-master-plan.md` (header legado);
  o gerador que emite o master-plan.
- **Melhoria proposta:** o **gerador deve emitir o master-plan já com o header "auto-gerenciado
  pelo autopilot — não editar durante uma corrida"** e com tabela/log nas colunas canônicas, para
  documento e command não nascerem divergentes.
- **Fontes:** `_inbox/LEARNING-architecture-autopilot-master-plan.md` (§4, linhas ~146-161).

### D2 — Atualização só no fim, não por fase — **P1**

- **Esperado:** o autopilot atualiza o master-plan a cada transição de fase, para refletir
  progresso e sobreviver a crash no meio da corrida.
- **Observado:** feedback registrado em memória — autopilots tendem a atualizar o master-plan só
  ao concluir, perdendo o rastro intermediário.
- **Onde dói:** `/be-architecture-autopilot`, `/fe-architecture-autopilot`.
- **Melhoria proposta:** o autopilot **escreve o checkpoint e em seguida atualiza o master-plan,
  por fase** (ordem: checkpoint → master-plan).
- **Fontes:** memória `[[feedback-master-plan-each-phase]]`.

### D3 — Gates diferidos sem ledger — **P1**

- **Esperado:** uma visão única do que ficou pendente e de como recuperá-lo.
- **Observado:** marcadores `gate-deferido`/`bloqueado` espalhados por seção de módulo, sem índice
  consolidado nem mecanismo de "replay".
- **Onde dói:** ambos os master-plans; recuperação manual e propensa a esquecimento.
- **Melhoria proposta:** **ledger consolidado de gates diferidos** (tabela no topo do master-plan
  ou arquivo dedicado) com o **comando de recuperação exato** por linha, + ideia de comando futuro
  `*-gates-replay` que executa todos os gates pendentes quando o toolchain aparecer. Conecta com A1.

---

## 5. Itens contextuais que afetam o workflow (registrar, não "consertar")

### E1 — TechLab AI bloqueado

- `integrations/techlab-ai/openapi.json` vazio, SHA `PENDING_FIRST_COMMIT`, Docker desligado → os
  DTOs e contratos de IA são placeholders (afeta LEAD/ASST/JRNY/INTL). O workflow deve **marcar o
  estado PENDING explicitamente** nos artefatos, em vez de prosseguir como se o contrato existisse.
- **Fontes:** `project-journal.md` ("P3 techlab-ai-sync → blocked: Docker not running"),
  `project-context.json` (`ai.techlabAi.sourceSha`), CLAUDE.md.

### E2 — `fe-prototype-analyzer`: 0 telas

- O analisador detectou 0 telas no HTML consolidado → `prototype-map.json` não gerado; revisitar
  com a estrutura de diretório modular.
- **Fontes:** `project-journal.md`.

---

## 6. Backlog priorizado

### P1 — ✅ IMPLEMENTADO (2026-06-05)

1. **Preflight de toolchain + ledger de gates diferidos** (A1, A2, D3) — ✅
   - `scripts/preflight.py` — detector de toolchain (`shutil.which` + wrapper `backend/gradlew`)
     + registro gate→tool + plano runnable/diferido com comando de recuperação.
   - `scripts/be-gates-replay.py` — lê o `## Ledger de gates diferidos` do master-plan, checa
     disponibilidade via preflight, roda só os runnable e reescreve o status (`--run --update`).
     Compartilhado BE/FE (`--ledger`).
   - Seção `## Ledger de gates diferidos` adicionada a ambos os master-plans (BE seeded com os 3
     gates Gradle diferidos do projeto). `be-module-generator.py` agora faz preflight nos próximos
     passos. Ambos os autopilots ganharam **Passo 0.5 — Preflight** + manutenção do ledger.
2. **Dedup de geradores via gate config↔SQL + fonte única** (B1) — ✅
   - `be-entity-generator.py`: guarda base-canônica — quando `*JpaEntity` (layer base do
     module-gen) já existe, pula a layer paralela do entity-gen (elimina o `@Entity` duplicado do
     INTL). Escape: `--allow-duplicate-layer`. Validado: INTL pula 7 agregados.
   - `be-module-generator.py`: gate `_validate_config_vs_sql` reporta divergência config↔SQL
     (antes silenciosa).
3. **Master-plan auto-gerenciado** (D1, D2) — ✅ já presente nos commands (header "auto-gerenciado",
   atualização por fase após checkpoint); reforçada a ordem checkpoint→master-plan e adicionada a
   regra do ledger (D3).

### P2 — ✅ IMPLEMENTADO (2026-06-05)

4. **Fail-fast em erro de subprocess** (A3) — ✅ `be-module-generator.py`: helper `_invoke_subgen`
   aborta o scaffold no 1º sub-gerador que falha (antes só `[WARN]` e seguia parcial). Flag
   `--continue-on-error` restaura o modo tolerante. Testado (ambos os ramos).
5. **Reposicionar `specs-validate` para após scaffold** (A4) — ✅ separação geração vs gate
   tornada explícita: A3 = só geração (`be-spec-to-bdd.py generate`, determinística, independente
   de toolchain); o gate (compileTestJava + `*CucumberIT*`) vive só no A5.bdd-gate, após scaffold
   e condicionado ao Gradle (senão → ledger). Documentado no `be-architecture-autopilot`.
6. **Unificar schema de checkpoint BE/FE** (C1) — ✅ campo divergente `prioridade`(BE)/`fase`(FE)
   unificado em `progressUnit` (string) nos dois autopilots de execução; envelope canônico
   documentado (`id, pipeline, modulo, currentStep, nextStep, progressUnit, iteration, timestamp,
   notes`; identidade específica `service`/`feature`).
7. **Convergir entity-gen para templates `.j2`** (B2) — ✅ os 4 emissores de persistência do
   `be-entity-generator.py` (entity/repository/port-out/adapter) passaram de f-strings inline para
   Jinja2 (`templates/operational/code/java/eg-*.java.j2`), via `render_code_template` — mesmo
   mecanismo do module-gen. **Byte-parity validada** (golden diff = idêntico). A lógica de
   colunas/tipos permanece em Python (passada como contexto). Nota: B1 já havia removido a
   dupla-emissão da MESMA entidade, então o ganho aqui é consistência de mecanismo de renderização.

### P3 — resolvido (2026-06-05)

8. **Migração de vocabulário `@hub`→`@journeyos`** (C2) — ✅ **já concluída.** Verificado:
   zero residuais em `.claude/commands/`, `scripts/`, `frontend/` (código+config), `CLAUDE.md` e
   `project-context.json`. As únicas menções a `@hub` restantes são **registros históricos** da
   migração (tabela "de→para" em `standards/module-pattern.md`, notas em master-plan FE e
   `framework-improvements.md`) — corretas de manter.
9. **Família `be-feature-architect-*`** (C3) — ⏭️ **decisão: NÃO criar** (2026-06-05). O BE já
   cobre evolução de serviço via `be-validator → be-planner → be-implement` (issue-based); um
   pipeline de feature espelhando o FE (~1300 linhas) não se justifica para o modelo do BE.
   Decisão registrada; reabrir se surgir necessidade real de features incrementais guiadas no BE.
10. **Gate EARS no FE** (C4) — ✅ **implementado.** Novo comando
    `.claude/commands/fe-architect-specs-validate.md`: Gate 1 (sintaxe EARS via
    `scripts/be-validate-ears.py`, agnóstico — reutilizado) sobre SPEC-01..07 + Gate 2 (cobertura
    EARS→Gherkin: cada SHALL tem `Scenario:` em `e2e/*.feature`). `fe-architect-specs` passou a
    emitir critérios EARS; `fe-architecture-autopilot` ganhou a etapa **A2.5 — Specs Validate**
    (entre specs e backlog) + coluna `Specs-Val` no master-plan; registrado em `CLAUDE.md`.
    Validador testado sobre SPEC real do WRKS (`0 issues`).

---

## Fontes consultadas

- `_inbox/LEARNING-architecture-autopilot-master-plan.md` (§4 gotcha do header).
- `docs/architecture/backend/plans/architecture-master-plan.md` e
  `docs/architecture/frontend/plans/architecture-master-plan.md` (notas `gate-deferido`/`bloqueado`,
  seção INTL com `@Entity` duplicado, pendências do gerador FE v2).
- `project-journal.md`, `project-context.json` (P3 bloqueado, analyzer 0 telas).
- Scripts: `scripts/be-module-generator.py`, `scripts/be-entity-generator.py`,
  `scripts/be-smoke-scaffold.py`, `scripts/fe-module-generator.py`.
- Memórias do agente: `[[gradle-toolchain-absent]]`, `[[toolchain-entity-generator-conflict]]`,
  `[[feedback-master-plan-each-phase]]`, `[[fe-scaffold-toolchain-absent]]`.
