# FE UI Map — Prototype Analysis (Journey OS)

Analyses the vendored HTML/CSS prototype, extracts per-screen metadata
(`@NgComponent`, `@NgSelector`, `@NgRoute`, CSS tokens, module assignment,
hybrid split), and writes `docs/architecture/frontend/prototype-map.json`.

This map is consumed by `/fe-ui-backlog` to generate the LEAD issues for each
screen. Run **once per project** after `/fe-ui-tokens`.

**Prerequisite:** prototype vendored at `prototipo/`
(run `sync-prototype.py sync` if not present, then `/fe-ui-tokens`).

**Supersedes:** `/fe-feature-architect-from-prototype` (deprecated — see D-307).

---

## Step 1 — Run the analyzer (deterministic script)

```bash
python scripts/fe-prototype-analyzer.py analyze \
  --prototype prototipo \
  --output docs/architecture/frontend/prototype-map.json \
  --report
```

The script reads every `.html` file in `prototipo/` and its
paired `.css`. For each screen it extracts:

| Field | Source |
|---|---|
| `id` | HTML filename (slug) |
| `pattern` | Inferred layout pattern (page / list / form / dashboard / …) |
| `module` | `@NgModule` comment → first route segment → first word of screen id |
| `ngComponent` | `@NgComponent: ClassName` HTML comment |
| `ngSelector` | `@NgSelector: app-selector` HTML comment |
| `ngRoute` | `@NgRoute: /path` HTML comment |
| `tokens` | All `var(--xxx)` usages in the paired CSS |
| `hybrid.material` | Material-candidate primitives (D-309 table) |
| `hybrid.custom` | Custom-keep primitives (D-309 table) |
| `sourceHtml` | Relative path of the screen HTML |
| `sourceCss` | Relative path of the paired CSS |

**Gate:** command exits `OK:` with screen count. If it exits `error:`, fix
the prototype path before proceeding.

---

## Step 2 — Review the module summary (agent judgment)

Read the `moduleSummary` block printed by `--report`:

```
MODULE      SCREENS    ROUTES
<module>    <N>        <list>
...
```

For each screen with `module: ""` (unresolved), decide which module it belongs
to. Valid modules: WRKS, LEAD, JRNY, ASST, COMM, SALE, INTL, GWY, REG, MIG.

Edit `docs/architecture/frontend/prototype-map.json` directly:

```json
{ "id": "settings-profile", "module": "<MODULE>", ... }
```

Also review `ngComponent` and `ngRoute` for screens where the HTML prototype
did **not** include `@Ng*` annotations — fill them in now. The pattern:

- `ngComponent`: `<Feature><Pattern>Component` (e.g. `SettingsProfilePageComponent`)
- `ngSelector`: `app-<module>-<feature>-<pattern>` (e.g. `app-crm-settings-profile-page`)
- `ngRoute`: relative path under the module's router (e.g. `/settings/profile`)

---

## Step 3 — Verify hybrid split (optional override)

The analyzer auto-suggests hybrid split based on the D-309 table. Override
any row in the `hybrid` field of the map entry:

```json
"hybrid": {
  "material": ["dialog", "form-field"],
  "custom":   ["kanban-card", "score-badge"]
}
```

This split is written verbatim into the Contrato de Fidelidade UI of each
LEAD issue by `/fe-ui-backlog`.

---

## Step 4 — Validate map completeness

Before running `/fe-ui-backlog`, confirm:

- [ ] Every screen has a non-empty `module`
- [ ] Every screen has `ngComponent` and `ngRoute` (even if manually filled)
- [ ] `moduleSummary` lists all expected modules (WRKS, LEAD, JRNY, ASST, COMM, SALE, INTL, GWY, REG, MIG)
- [ ] No screen has `pattern: "unknown"` without a manual override

---

## Output

```
FE UI Map analysed (Journey OS)

Screens:  <N> total
  <MODULE-A>: <X> screens
  <MODULE-B>: <Y> screens
Map:  docs/architecture/frontend/prototype-map.json

Next: /fe-ui-backlog <MODULE>   (generate LEAD issues for one module)
```
