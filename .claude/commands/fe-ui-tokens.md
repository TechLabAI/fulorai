# FE UI Tokens — Design System Migration (Journey OS)

Migrates the prototype design system (CSS variables, layout primitives, shell
components) into the Angular shared libs, **once per project**, before any
screen-level UI work begins.

**Prerequisite:** prototype vendored at `prototipo/`
(run `sync-prototype.py sync` if not present).

---

## Step 1 — Extract (deterministic script)

Run the LAYER 3 extractor. It reads `00-tokens.css`, `shell.css`, and
`02-components.html` from the prototype and emits three artefacts:

```bash
python scripts/fe-ui-token-extractor.py extract \
  --prototype prototipo \
  --output docs/architecture/frontend/ui-design-system \
  --report
```

Outputs:
- `docs/architecture/frontend/ui-design-system/ui-tokens-map.json` — CSS var → SCSS name + category
- `docs/architecture/frontend/ui-design-system/ui-tokens.scss` — ready-to-paste SCSS partial
- `docs/architecture/frontend/ui-design-system/components-catalog.md` — primitive inventory

**Gate:** command exits `OK:` with token count. If it exits `error:`, fix the
missing file before proceeding.

---

## Step 2 — Review the catalog (agent judgment)

Read `docs/architecture/frontend/ui-design-system/components-catalog.md`.

For each row marked `review`, decide:

| Verdict | Criterion |
|---|---|
| **material** | Primitive resolves accessibility/behaviour (focus trap, ARIA, keyboard nav, scroll-lock). Use Material component + token theming via `mat-theme`. |
| **custom** | Primitive is signature visual identity (specific layout, shape, interaction). Keep CSS-custom + tokens. |

Overrides: edit the `components-catalog.md` file directly — update the
`Hybrid Classification` column. This file is the authoritative record consumed
by `fe-ui-backlog` to populate the Contrato de Fidelidade UI per screen.

---

## Step 3 — Migrate tokens to `@journeyos/shared/ui-tokens`

Copy `ui-tokens.scss` into:

```
frontend/libs/shared/ui-tokens/src/lib/_tokens.scss
```

> Canonical target: `frontend/libs/shared/ui-tokens/src/lib/_tokens.scss`

Then re-export from `index.ts`:

```typescript
export * from './lib/_tokens.scss';
```

Add the SCSS file to the Angular project's `styles` array in
`frontend/apps/journey-os-web/project.json` (or `angular.json`):

```json
"styles": [
  "frontend/libs/shared/ui-tokens/src/lib/_tokens.scss",
  "src/styles.scss"
]
```

---

## Step 4 — Shell layout migration

For primitives classified **custom** that come from `shell.css` (sidebar,
topbar, ai-drawer, content grid), migrate to
`frontend/libs/shared/ui-components/src/lib/`:

- Create one SCSS partial per component group (e.g. `_sidebar.scss`, `_topbar.scss`).
- Reference token SCSS names (`$bg-surface`, `$sidebar-width`) — **zero hardcoded
  colour/spacing values**.
- For each custom component, create a stub Angular component (standalone) that
  applies the class — the `fe-implement` pipeline fills the template/logic.

---

## Step 5 — Gate

Run:

```bash
npx nx build journeyos-shared-ui-tokens
```

Expected: build passes, no TS errors. If it fails, fix the SCSS syntax before
continuing.

Then verify the theme switches:
1. Add `[data-theme="dark"]` to `<html>` in `apps/journey-os-web/src/index.html`.
2. Open the app — colours should switch without a page reload.
3. Remove the attribute.

---

## Output

```
FE UI Tokens migrated (Journey OS)

Tokens:     <N> CSS vars → SCSS (color, typography, spacing, radius, shadow, layout)
Primitives: <M> from shell.css + 02-components.html
  material: <X>  custom: <Y>  review-overridden: <Z>
Libs updated:
  @journeyos/shared/ui-tokens  — _tokens.scss + index.ts
  @journeyos/shared/ui-components — <K> stub component(s)
Gate: nx build journeyos-shared-ui-tokens → OK

Next: /fe-ui-map   (analyse prototype screens → prototype-map.json)
```
