# /be-spec-drift (Journey OS)

Detect drift between EARS spec + `arch.json` and the actual Java AST of a service. **Read-only** — the command produces a markdown report; never edits spec or code (D-160).

**Módulo:** `$ARGUMENTS`

Se nao informado, perguntar: `Qual modulo? (WRKS | LEAD | JRNY | ASST | COMM | SALE | INTL | GWY | REG | MIG)`

Mapeamento modulo -> microservico:

- WRKS = ``
- LEAD = ``
- JRNY = ``
- ASST = ``
- COMM = ``
- SALE = ``
- INTL = ``
- GWY = ``
- REG = ``
- MIG = ``

---

## Quando rodar

**Sempre que você edita um destes três sem casar com os outros dois:**

1. `backend/services/<service>/src/main/java/.../api/controller/*Controller.java`
2. `backend/services/<service>/src/main/java/.../application/service/*Service.java` (anotações `@PreAuthorize`)
3. `docs/architecture/backend/services/<service>/spec/**/*.md` (cláusulas EARS)
4. `arch/decisions/rbac.arch.json`, `multi-tenancy.arch.json`, `error-model.arch.json`, `events.arch.json`

**Não rode** depois de:

- Alterações puramente em prosa narrativa do spec.
- Refactor interno de domain/model (sem mudança de contrato).
- Mudanças em Flyway / SQL (out of scope v1.0).

---

## Como rodar

```bash
python scripts/be-spec-drift.py \
  --module <PREFIX> \
  --service backend/services/<service>
```

Resolução automática quando flags omitidas:

- `--spec`: discover por convenção (`docs/architecture/backend/services/<service>/spec/**/*.md` + `docs/architecture/backend/issues/<MODULE>-*.md`).
- `--arch-dir`: walk up até achar `arch/decisions/*.arch.json`.
- `--mapping`: usa `arch/shared/code-mapping/code-mapping.arch.json` pinado pelo projeto (opt-in via `new-project.py docs-skeleton --with-code-mapping`); se ausente, cai para o workspace.
- `--output`: stdout (padrão); para gravar em arquivo: `--output clients/<project>/spec-drift-report.md`.

Flags úteis:

- `--show-unmapped` — inclui cláusulas EARS que não casaram com nenhuma regra (coverage gap).
- `--strict` — exit 2 quando há finding de severidade `error`.

---

## Como interpretar o report

O report classifica cada divergência em quatro classes (D-160, D-162):

| Classe | Significado | Ação típica |
|---|---|---|
| `MISSING_IN_CODE` | Spec exige; código não tem | Atualizar código OU relaxar spec. Spec é a fonte presumida (D-162). |
| `MISSING_IN_SPEC` | Código tem; spec silencia | Documentar comportamento no spec OU remover do código. Código é a fonte presumida. |
| `MISMATCH` | Ambos presentes; valores conflitam | Arquiteto decide. Sem preferência automática. |
| `UNMAPPED` | Cláusula EARS sem regra correspondente | Não é drift — é coverage gap. Estender o mapping ou marcar a cláusula como prosa. Suprimido por default. |

**A ferramenta não decide.** Cada finding tem um `resolution_hint` — sugestão default que ataca 70% dos casos; arquiteto valida ou descarta.

**Severidades:**

- `error` — bloqueante (RBAC role, endpoint, context resolution).
- `warning` — não-bloqueante (validação de DTO, audit hook, falta de cobertura no spec).
- `info` — coverage gap (UNMAPPED apenas).

---

## Fluxo recomendado

1. Você editou um controller adicionando `@PreAuthorize("hasRole('NEW_ROLE')")`.
2. Você roda `/be-spec-drift WRKS`.
3. Report acusa `MISSING_IN_SPEC E2` — código tem role nova, spec não.
4. Você decide:
   - Adicionar cláusula EARS no spec: `**IF** o usuário não tem role NEW_ROLE, **THEN** o sistema **SHALL** retornar 403.`; OU
   - Remover o `@PreAuthorize` se foi adicionado por engano.
5. Roda novamente. Report deve estar limpo (ou listar apenas itens que você decidiu deixar como divergência intencional documentada).

---

## Limites conhecidos (D-160, escopo v1.0)

- Cobre 6 EARS patterns (endpoint, RBAC role, validation, event publish, context resolution, audit hook) + 4 arch.json aspects (RBAC enforcement default, audit_required, multi-tenancy filter presence, exception handler coverage).
- Java 16+ features (records, pattern matching, sealed types) podem falhar no parser javalang; o fallback regex captura anotações de classe, mas não method-level. Affected files são listados na seção "Notes" do report.
- Não distingue "código atualizado, spec atrasada" de "spec atualizada, código atrasado" — heurística inversa do `resolution_hint` é probabilística, não definitiva.

---

## Anti-uso

- **Não rode** como hook de pre-commit. O report é informativo, não bloqueante.
- **Não trate UNMAPPED como bug.** É coverage gap; expanda a regra de mapping ou aceite a cláusula como prosa.
- **Não confie cegamente em `resolution_hint`.** Veja o contexto.
- **Não edite o report manualmente.** Cada execução re-gera; edits seriam perdidos.

---

## Referências

- D-160 — Modelo de drift bidirecional (read-only, manual resolve)
- D-161 — Formato do `code-mapping.arch.json`
- D-162 — Política de resolução (humano decide)
- Runbook: `docs/runbooks/aspects/code-mapping.md`
