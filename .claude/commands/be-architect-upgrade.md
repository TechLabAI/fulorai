# /be-architect-upgrade

Re-apply the workspace's current architecture to this project, safely. Files
the project edited locally are **never overwritten**. Use after
`/be-architect-drift-check` reports workspace evolution.

---

## Safety invariants (read first)

The upgrade script is built around three guarantees you should understand
before invoking it:

1. **Locally-modified files are never auto-overwritten.** If you edited a
   rendered file after `/new-project`, the upgrade will skip it and the lock
   keeps tracking the original baseline — so future drift-checks keep flagging
   it for you. To accept the workspace version, delete the file first, then
   re-run upgrade (it will re-render the missing file).
2. **Drifted files (workspace evolved AND you edited) require manual merge.**
   The script prints the diff but does not write anything. Exit code is `1`.
3. **Default mode is dry-run.** Nothing is written without `--apply`.

---

## Workflow

1. **Always run `/be-architect-drift-check` first.** Understand what changed
   and what you're about to upgrade.

2. **Preview the upgrade (dry-run):**

   ```bash
   python scripts/be-architect-upgrade.py
   ```

   The script prints, per aspect:
   - `[upgrade] <file>` — will be re-rendered (workspace evolved, local copy unchanged)
   - `[preserve-local] <file>` — you edited locally; lock entry kept as-was
   - `[DRIFTED] <file>` — manual merge required (workspace evolved AND you edited)
   - `[orphan] <file>` — source template removed from workspace; consider deleting locally

   For files that would be re-rendered, a truncated unified diff is shown.
   Use `--verbose` (`-v`) to see full diffs.

3. **Apply the upgrade:**

   ```bash
   python scripts/be-architect-upgrade.py --apply
   ```

   The script writes the re-rendered files and updates `architecture.lock`
   with new SHAs. Drifted aspects are *not* touched — their lock entries are
   preserved so the conflict stays visible.

4. **Resolve any drifted files manually.** For each `[DRIFTED]` entry:
   a. Review the unified diff (`--verbose` to see it)
   b. Decide: keep your local version, accept workspace, or hand-merge
   c. Edit the file accordingly
   d. To re-baseline (tell the system "this is now the truth"), delete and
      re-render via `python scripts/be-architect-upgrade.py --apply`. Or
      run `/new-project docs-skeleton` to regenerate the lock entirely (will
      preserve files that match a known SHA).

---

## Exit codes

- `0` — completed cleanly (dry-run or apply; no drifted aspects)
- `1` — drifted aspects detected (manual merge needed) OR
  workspace evolved when running drift-check
- `2` — usage error (no `architecture.lock`, workspace not found, schema mismatch)

---

## Workspace resolution

Identical to `/be-architect-drift-check`. The script must find the
techlab-architecture workspace to re-render templates from. In order:

1. `--workspace <path>` flag
2. `TECHLAB_ARCH_HOME` environment variable
3. Walk up from cwd looking for `scripts/new-project.py` + `templates/architecture/`

If none resolves, ask the user to set `TECHLAB_ARCH_HOME` or pass
`--workspace`.

---

## What the upgrade touches

- `docs/architecture/**` (anything tracked in `architecture.lock`)
- `architecture.lock` (rewritten with new SHAs for re-rendered aspects;
  unchanged entries for drifted/preserve-local aspects)

**Not** touched: source code, tests, configurations, command files, schemas.
Tier 1.2 of techlab-architecture is *documentation-layer only*. Future tiers
will extend this to other generated artifacts.

---

## Notes for Journey OS

- Always commit your work before running `--apply`. The script writes
  directly; rollback = `git checkout -- docs/architecture/ architecture.lock`.
- The script does not run tests. If your project has architectural tests
  (e.g. ArchUnit), re-run them after upgrade.
- If you regularly hit `[DRIFTED]` for the same files, that's a signal: the
  workspace's standard for that area is diverging from your project's
  practice. Either contribute the local pattern upstream, or document why
  you intentionally deviate.
