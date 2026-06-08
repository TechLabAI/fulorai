# FE UI Backlog — Generate LEAD Issues (Journey OS)

Generates one LEAD issue per screen for the requested module, using
`docs/architecture/frontend/prototype-map.json` as input.

Each issue includes the **Contrato de Fidelidade UI** section:
visual source references (`raw/`), hybrid Material × custom split table,
CSS token list, Angular component tree, and fidelity acceptance criteria.

**Input:** `$ARGUMENTS` — module prefix (e.g. `CRM`, `AUTH`, `CORE`).

**Prerequisite:** `docs/architecture/frontend/prototype-map.json` must exist
and be validated (run `/fe-ui-map` first).

Valid modules: WRKS, LEAD, JRNY, ASST, COMM, SALE, INTL, GWY, REG, MIG.

---

## Step 1 — Run the issue generator (deterministic script)

Replace `<MODULE>` with the argument:

```bash
python scripts/backlog-gen.py gen \
  --from-prototype-map docs/architecture/frontend/prototype-map.json \
  --filter-module <MODULE> \
  --prototype-root prototipo \
  --layer frontend \
  --module <MODULE> \
  --prefix JOS
```

The script writes to `docs/architecture/frontend/issues/`:

```
docs/architecture/frontend/issues/
  JOS-<MODULE>-FE-NNN.md          ← LEAD issue (Markdown)
  JOS-<MODULE>-FE-NNN.contract.json  ← machine-readable contract
  raw/
    <screen-id>.html               ← symlink or copy of source HTML
    <screen-id>.css                ← symlink or copy of source CSS
```

**Gate:** script exits `OK: <N> issues generated`. If it exits `error:` or
`2` (validation), fix the prototype-map and re-run.

---

## Step 2 — Review generated issues (agent judgment)

For each generated `JOS-<MODULE>-FE-NNN.md`:

1. Read the **Contrato de Fidelidade UI** section.
2. Verify the hybrid split table matches your intent — override if needed:
   - Edit the issue `.md` and the corresponding `.contract.json` in sync.
3. Verify `ngComponent` and `ngRoute` are correct for each screen.
4. Confirm `raw/` symlinks resolve to the actual prototype files.

Borderline Material/custom decisions (e.g. a branded `<tab>` that uses
Angular Material's `MatTabsModule` but with full custom styling):

| Decision | Use |
|---|---|
| Behaviour-primary | `material` — use the component, theme with tokens |
| Visual-identity-primary | `custom` — rebuild with CSS custom + SCSS tokens |

---

## Step 3 — Update issues-map.md

After reviewing all generated issues, append the new entries to
`docs/architecture/frontend/issues-map.md`:

```markdown
| JOS-<MODULE>-FE-NNN | <screen-id> | LEAD | open | <pattern> |
```

---

## Step 4 — Gate

Confirm the following before closing this command:

- [ ] All screens in module `<MODULE>` have a corresponding LEAD issue
- [ ] Every issue has `Contrato de Fidelidade UI` section populated
- [ ] Every issue has a `raw/` entry pointing to valid prototype files
- [ ] `issues-map.md` updated with new issues
- [ ] Numbering is continuous (no gaps in `FE-NNN` sequence)

---

## Output

```
FE UI Backlog generated (Journey OS) — module: <MODULE>

Issues: JOS-<MODULE>-FE-<START>..<END>  (<N> issues)
  <screen-id> → JOS-<MODULE>-FE-NNN  (<pattern>)
  ...
raw/ entries: <N> HTML + <N> CSS

Next: /fe-ui-backlog <NEXT_MODULE>   (repeat for each module)
   or /fe-ui-autopilot <MODULE>       (begin screen-by-screen implementation)
```
