# /be-architect-drift-check

Detect whether the **architectural decisions and standards** that this project
was generated from have evolved in the techlab-architecture workspace since
they were last applied here. This is the read-only counterpart to
`/be-architect-upgrade`.

---

## What it does

Runs `scripts/be-architect-drift-check.py`, which reads `architecture.lock`
(written at `/new-project` P2) and recomputes SHA-256 of every architectural
artifact in both the workspace and this project. Each file is classified:

| State | Meaning |
|---|---|
| `synced` | Both SHAs match. Nothing to do. |
| `source_changed` | Workspace template evolved. **Safe** to upgrade — local copy unmodified. |
| `locally_modified` | This project edited the rendered file. Workspace unchanged. |
| `drifted` | Both differ. Conflict — requires human review. |
| `source_missing` | The source template was removed from the workspace. |
| `output_missing` | The rendered output was deleted from this project. |

---

## Workflow

1. **Locate the workspace.** The script needs to compare against
   `templates/architecture/` in the techlab-architecture workspace. Try in
   order:
   - `--workspace <path>` flag (if the user provides one)
   - `TECHLAB_ARCH_HOME` env var
   - Walking up from cwd

   If none resolves, ask the user to set `TECHLAB_ARCH_HOME` or pass
   `--workspace`.

2. **Run the script:**

   ```bash
   python scripts/be-architect-drift-check.py
   ```

   Exit code `0` = no workspace evolution. Exit code `1` = workspace has
   evolved (drift detected). Exit code `2` = setup error.

3. **Interpret the report:**
   - **Nothing to do** if everything is `synced` (or only `locally_modified`
     entries exist — the user knows what they edited).
   - **Recommend `/be-architect-upgrade`** if any `source_changed` or
     `drifted` entries exist. Highlight which aspect areas evolved.
   - **Investigate** if `source_missing` or `output_missing` appears — that
     indicates a structural change (e.g., a template was renamed/removed in
     the workspace, or a doc was deleted from this project).

4. **Do NOT auto-fix anything.** This command is read-only by design. The
   user must explicitly run `/be-architect-upgrade` to apply changes.

---

## Output format

The script prints a grouped report. Example with one workspace evolution and
one local edit:

```
Architecture drift report
  Pinned:  arch 1.0.0 | tool 0.4.0 | sha c9cf00e | applied 2026-05-25T18:12:09Z
  Current: arch 1.1.0 | tool 0.4.0 | sha c9cf00e
  [drift] architecture version differs (1.0.0 -> 1.1.0)
    -> backend/standards — workspace evolved (safe to upgrade) (8 file(s))
      [->] backend/standards/java-conventions.md
  [ok] frontend/standards (5 synced)
  ...
    *  shared/rbac — modified locally (workspace unchanged) (8 file(s))
      [*] shared/rbac/papeis.md

Summary:
  synced                                           33
  workspace evolved (safe to upgrade)              1
  modified locally (workspace unchanged)           1

Workspace has evolved. Run /be-architect-upgrade to preview a safe upgrade.
```

Use `--verbose` (`-v`) to show every file, including synced ones. Use
`--json` for machine-readable output (useful when chaining commands).

---

## Notes for Journey OS

- This command is read-only — it never writes to disk.
- The `architecture.lock` at the root is the source of truth for what was
  applied. Do not edit it by hand; let `/be-architect-upgrade` maintain it.
- If `architecture.lock` is missing, the project was likely generated before
  Tier 1.2 of techlab-architecture. Re-run `/new-project docs-skeleton` once
  to create it (it will not touch already-rendered files).
