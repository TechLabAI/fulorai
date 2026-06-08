# FE Architect -- Specs Validate (EARS gate)

Voce e o agente que **valida** as specs FE: garante que os criterios de aceite de
`SPEC-01..07` estao em **notacao EARS** e que **toda clausula SHALL tem um cenario e2e
Gherkin** correspondente em `e2e/*.feature`. E o analogo FE do `/be-architect-specs-validate`
(D-329, C4).

**Module prefix:** `$ARGUMENTS`

Se nao informado, perguntar: `Qual o prefixo do modulo a validar? (ex.: WRKS | LEAD | JRNY | ASST | COMM | SALE | INTL | GWY | REG | MIG)`

---

## Papel do agente

No BE, `/be-architect-specs-validate` fecha o elo "toda SHALL clause vira um cenario BDD".
No FE faltava o equivalente: as specs eram Gherkin-first (SPEC-08) **sem** criterios EARS
sistematicos em SPEC-01..07. Este comando adiciona esse gate, **sem gerar codigo** (read-only +
validacao): a geracao dos specs Playwright continua no scaffold via Nx.

Dois gates:

1. **Gate de sintaxe EARS** (automatizado) -- `scripts/be-validate-ears.py` (agnostico de
   linguagem, reutilizado do BE) sobre `SPEC-01..07`.
2. **Gate de cobertura EARS -> Gherkin** -- cada clausula `THE SYSTEM SHALL` tem ao menos um
   cenario (`Scenario:`) em `e2e/*.feature`.

Pipeline FE:
1. /fe-architect-vision
2. /fe-architect-specs
3. **/fe-architect-specs-validate (voce — D-329)**
4. /fe-architect-backlog
5. /fe-architect-scaffold
6. e2e-validate (gate de compilacao/list, no `/fe-architecture-autopilot` A5)

---

## Pre-requisitos

1. Specs existem em `docs/architecture/frontend/modules/<module>/frontend/frontend-spec/SPEC-01..08.md`.
2. Ha >= 1 `docs/architecture/frontend/modules/<module>/frontend/e2e/<fluxo>.feature`.
3. Os criterios de aceite de SPEC-01..07 usam **EARS** (escritos por `/fe-architect-specs`).

> **Modulos de infraestrutura:** sem specs de dominio/e2e -> `specs-validate = N/A`.

---

## Passos

### 1. Resolver paths

Do prefixo (`$ARGUMENTS`), resolver:

- `MODULE_PREFIX` = `$ARGUMENTS` (uppercase)
- `MODULE` = nome canonico kebab-case (de `project-context.json` / `_brief.md`)
- `SPEC_DIR` = `docs/architecture/frontend/modules/<MODULE>/frontend/frontend-spec/`
- `E2E_DIR` = `docs/architecture/frontend/modules/<MODULE>/frontend/e2e/`

### 2. Gate 1 -- sintaxe EARS (automatizado)

Rodar o validador EARS em cada SPEC com criterios de aceite (01..07):

```bash
python scripts/be-validate-ears.py --file <SPEC_DIR>/SPEC-01-route-map.md
# repetir para SPEC-02..07
```

- Cada linha com `THE SYSTEM SHALL` deve casar **exatamente** um dos 5 padroes EARS
  (Ubiquitous / Event-driven `WHEN` / State-driven `WHILE` / Optional `WHERE` / Unwanted `IF..THEN`).
- Saida com `0 violations` -> Gate 1 PASS.
- `no EARS clauses found` numa SPEC que deveria ter criterios -> sinalizar.

### 3. Gate 2 -- cobertura EARS -> Gherkin

Para cada clausula `THE SYSTEM SHALL <...>` extraida de SPEC-01..07, confirmar que existe ao
menos um `Scenario:` em `E2E_DIR/*.feature` que a exercita (match por palavra-chave do
comportamento ou referencia ao id da clausula).

- Listar clausulas **sem** cenario correspondente -> `cobertura = GAP` (reportar, nao bloquear
  o scaffold; e sinal para `/fe-architect-backlog` criar a issue do cenario faltante).
- Listar cenarios `.feature` **sem** clausula EARS de origem -> `cenario orfao` (INFO).

### 4. Report

```markdown
## FE Specs validate -- <MODULE>

- SPEC-01..07 validadas: 7
- Clausulas EARS: N
- Distribuicao: ubiquitous X | event Y | state Z | optional W | unwanted K
- Gate 1 (sintaxe EARS): PASS / FAIL (<arquivo>:<linha> ...)
- Cenarios e2e (.feature): M
- Gate 2 (cobertura EARS->Gherkin): N-G/N cobertas | G gap(s) | O orfao(s)
```

### 5. Resultado / proximo passo

- **Gate 1 PASS + 0 gaps:** `specs-validate = OK`. Prosseguir para `/fe-architect-backlog`.
- **Gate 1 FAIL:** corrigir a sintaxe EARS nas SPECs apontadas e re-rodar (re-rodar e sempre
  seguro -- read-only).
- **Gaps de cobertura:** `specs-validate = OK (com gaps)`; registrar os cenarios faltantes
  como entrada para o backlog (uma issue por gap). Nao inventar cenario sem o criterio de origem.

---

## Convencoes

- **Read-only / validacao:** este comando **nao gera** `.feature` nem specs Playwright.
  So valida sintaxe + cobertura. Re-rodar e sempre seguro.
- **EARS e a fonte:** os 5 padroes seguem `scripts/be-validate-ears.py`. O FE reutiliza
  o mesmo validador do BE -- agnostico de linguagem.
- **Gherkin permanece:** SPEC-08 + `e2e/*.feature` continuam Gherkin (Playwright). EARS
  adiciona os criterios de aceite *sistematicos* em SPEC-01..07; nao substitui os cenarios.

---

## Erros comuns

| Erro | Causa | Remediar |
|---|---|---|
| `no EARS clauses found` | SPEC-01..07 sem criterios EARS | `/fe-architect-specs` deve emitir criterios em notacao EARS |
| Violacao de padrao EARS | SHALL fora dos 5 padroes | Reescrever para `WHEN/WHILE/WHERE/IF..THEN/THE SYSTEM SHALL` |
| Gap de cobertura | SHALL sem cenario `.feature` | Criar o `.feature`/Scenario (vai como issue no backlog) |
| Cenario orfao | `.feature` sem clausula EARS de origem | INFO -- documentar a origem do cenario na SPEC |

---

## Referencias

- `scripts/be-validate-ears.py` -- validador EARS (agnostico; reutilizado pelo FE).
- `.claude/commands/be-architect-specs-validate.md` -- analogo BE (EARS -> BDD/Cucumber).
- `.claude/commands/fe-architect-specs.md` -- emite SPEC-01..08 + criterios EARS.
