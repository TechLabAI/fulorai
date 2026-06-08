"""lockfile.py — read/write/inspect ``architecture.lock``.

The lock is a JSON file at the **root of each generated project** that records
which architecture version was applied and the SHA-256 of every architectural
artifact at apply time. It enables:

- ``/be-architect-drift-check`` — detect when the workspace has evolved past
  the version the project pinned
- ``/be-architect-upgrade`` — re-apply with safety (skip files modified
  locally; update files unchanged since apply)

Schema (D-055, format version 1):

.. code-block:: json

    {
      "_schema_version": 1,
      "techlab_architecture": {
        "version": "0.4.0",
        "source_sha": "c9cf00e"
      },
      "architecture": {
        "version": "1.0.0",
        "applied_at": "2026-05-25T15:30:00Z"
      },
      "aspects": {
        "shared/rbac/papeis.md": {
          "source": "templates/architecture/shared/rbac/papeis.md.j2",
          "source_sha": "<sha256 of the source template at apply time>",
          "output": "docs/architecture/shared/rbac/papeis.md",
          "output_sha": "<sha256 of the rendered output at apply time>"
        }
      }
    }

Field semantics:

- ``_schema_version`` — bump when the lock format itself changes incompatibly.
  Readers should refuse unknown versions.
- ``techlab_architecture.version`` — workspace tool version (semver of the
  generator), read from ``pyproject.toml`` at apply time.
- ``techlab_architecture.source_sha`` — git short SHA of the workspace at
  apply time. Optional; missing if ``.git`` is unavailable.
- ``architecture.version`` — semver of the architecture (independent from the
  tool version), read from ``templates/architecture/VERSION`` at apply time.
- ``architecture.applied_at`` — ISO-8601 UTC timestamp.
- ``aspects`` — dict keyed by the **rendered file's path relative to the
  project root**. Each value records the source template, source SHA, output
  path, and output SHA, all captured at apply time. Drift detection works by
  recomputing the SHAs of the current files and comparing to these.

Drift detection semantics:

- *Source changed*: workspace SHA(``source``) != stored ``source_sha``. The
  template evolved since apply — workspace is ahead.
- *Locally modified*: client SHA(``output``) != stored ``output_sha``. The
  client edited the rendered output. Upgrade must not overwrite.
- *Drifted (both)*: both differ. Workspace evolved AND client edited.
  Resolution requires human review.
- *Synced*: neither differs.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
LOCK_FILENAME = "architecture.lock"


def sha256_of_file(path: Path) -> str:
    """Return the hex SHA-256 digest of a file's bytes."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_workspace_arch_version(workspace: Path) -> str:
    """Read the architecture semver from ``templates/architecture/VERSION``."""
    version_file = workspace / "templates" / "architecture" / "VERSION"
    if not version_file.is_file():
        return "0.0.0"
    return version_file.read_text(encoding="utf-8").strip()


def read_workspace_tool_version(workspace: Path) -> str:
    """Extract the workspace tool version from ``pyproject.toml``.

    Falls back to ``"unknown"`` when pyproject.toml is missing or unparseable.
    """
    pyproject = workspace / "pyproject.toml"
    if not pyproject.is_file():
        return "unknown"
    for line in pyproject.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("version") and "=" in line:
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return "unknown"


def read_workspace_git_sha(workspace: Path) -> str | None:
    """Return the workspace's git short SHA, or None if unavailable."""
    if not (workspace / ".git").exists():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(workspace), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip() or None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def build_aspect_entry(
    source_template: Path,
    workspace: Path,
    output_file: Path,
    project_root: Path,
) -> dict[str, str]:
    """Return one ``aspects`` entry given source + output paths.

    Both paths must exist on disk (computes their SHAs).
    """
    return {
        "source": str(source_template.relative_to(workspace)).replace("\\", "/"),
        "source_sha": sha256_of_file(source_template),
        "output": str(output_file.relative_to(project_root)).replace("\\", "/"),
        "output_sha": sha256_of_file(output_file),
    }


def build_lock(
    workspace: Path,
    project_root: Path,
    aspects: dict[str, dict[str, str]],
) -> dict[str, Any]:
    """Construct the full lock payload."""
    lock: dict[str, Any] = {
        "_schema_version": SCHEMA_VERSION,
        "techlab_architecture": {
            "version": read_workspace_tool_version(workspace),
        },
        "architecture": {
            "version": read_workspace_arch_version(workspace),
            "applied_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "aspects": aspects,
    }
    git_sha = read_workspace_git_sha(workspace)
    if git_sha:
        lock["techlab_architecture"]["source_sha"] = git_sha
    return lock


def write_lock(project_root: Path, lock: dict[str, Any]) -> Path:
    """Write the lock atomically (temp file + rename) at project root."""
    target = project_root / LOCK_FILENAME
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(
        json.dumps(lock, indent=2, ensure_ascii=False, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    tmp.replace(target)
    return target


def _deep_merge_local(base: dict, override: dict) -> dict:
    """Mirror of new-project.py:_deep_merge — replicated here to keep
    lockfile.py dependency-free (D-074). Empty literals replace."""
    out = dict(base)
    for k, v in override.items():
        if v == {} or v == []:
            out[k] = v
        elif isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge_local(out[k], v)
        else:
            out[k] = v
    return out


def _sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_merged_decision_content(
    entry: dict[str, str], workspace: Path, project_root: Path
) -> str | None:
    """D-074: re-derive the merged content for an aspect with composite
    source. Returns the merged JSON as serialised text (matches what
    copy_decisions_snapshot writes to disk), or None when any required
    part is missing.

    Source format: `templates/.../<aspect>.arch.json + <override_part>
    [+ <override_part>...]`. Override parts are either a project-relative
    file path (`arch/overrides/<aspect>.partial.json`) or a sentinel like
    `project-context.json:modules.registry` (dynamic override re-derived
    from project-context).

    Public so be-architect-upgrade.py can use the same logic to compute
    the would-be content for an upgrade dry-run / apply.
    """
    parts = [p.strip() for p in entry["source"].split(" + ")]
    if not parts:
        return None
    base_path = workspace / parts[0]
    if not base_path.is_file():
        return None
    merged: dict = json.loads(base_path.read_text(encoding="utf-8"))

    aspect_name = Path(parts[0]).name.removesuffix(".arch.json")
    for part in parts[1:]:
        if part.startswith("project-context.json:"):
            ctx_file = project_root / "project-context.json"
            if not ctx_file.is_file():
                return None
            ctx = json.loads(ctx_file.read_text(encoding="utf-8"))
            dynamic = _derive_dynamic_overrides_local(ctx)
            if aspect_name in dynamic:
                merged = _deep_merge_local(merged, dynamic[aspect_name])
        else:
            override_path = project_root / part
            if not override_path.is_file():
                return None
            override_data = json.loads(override_path.read_text(encoding="utf-8"))
            merged = _deep_merge_local(merged, override_data)

    return json.dumps(merged, indent=2, ensure_ascii=False) + "\n"


def _recompute_composite_source_sha(
    entry: dict[str, str], workspace: Path, project_root: Path
) -> str | None:
    """SHA of the merged decision content (D-074). Delegates to
    `build_merged_decision_content` so the same logic produces both the
    SHA used for drift detection and the text written during upgrade.
    """
    out_text = build_merged_decision_content(entry, workspace, project_root)
    if out_text is None:
        return None
    return _sha256_of_bytes(out_text.encode("utf-8"))


def _recompute_aggregate_source_sha(
    entry: dict[str, str], project_root: Path
) -> str | None:
    """D-072: constitution.md's source is an aggregate over every
    `arch/decisions/*.arch.json` in the project. Recompute current
    synthetic SHA by hashing the concatenated per-aspect SHAs.
    """
    decisions_dir = project_root / "arch" / "decisions"
    if not decisions_dir.is_dir():
        return None
    aspect_files = sorted(decisions_dir.glob("*.arch.json"))
    if not aspect_files:
        return None
    agg = hashlib.sha256()
    for ap in aspect_files:
        agg.update(sha256_of_file(ap).encode("ascii"))
    return agg.hexdigest()


def _derive_dynamic_overrides_local(ctx: dict) -> dict[str, dict]:
    """Mirror of new-project.py:_derive_dynamic_overrides — kept here so
    lockfile.py stays free of new-project import."""
    out: dict[str, dict] = {}
    modules = (ctx.get("modules") or {}).get("registry") or []
    if modules:
        out["permission-catalogue"] = {
            "modules": [
                {
                    "prefix": (m.get("prefix") or "").lower(),
                    "name": m.get("displayName", m.get("prefix", "")),
                    "description": m.get("description", ""),
                    "permissions": [],
                }
                for m in modules
            ]
        }
    out["events"] = {"modules": []}
    out["error-model"] = {"modules": []}
    out["entity-scope"] = {"scopes": {}}
    return out


def classify_aspect(
    aspect_key: str,
    entry: dict[str, str],
    workspace: Path,
    project_root: Path,
) -> dict[str, Any]:
    """Recompute SHAs and classify one aspect entry.

    Returns a dict with the entry's static info plus:
        state: one of "synced", "source_changed", "locally_modified",
               "drifted", "source_missing", "output_missing"
        source_sha_current, output_sha_current: recomputed SHAs (or None
            when the corresponding file is gone)

    For COMPOSITE sources (D-074) — entries whose `source` contains ` + ` —
    `source_sha_current` is recomputed by re-running the deep-merge of
    workspace base + project override files + dynamic project-context
    overrides, hashing the result. Drift then catches both workspace bumps
    AND override edits.

    Consumed by both ``be-architect-drift-check.py`` and
    ``be-architect-upgrade.py``.
    """
    is_composite = " + " in entry["source"]
    is_aggregate = entry["source"].startswith("aggregate(")
    output = project_root / entry["output"]
    output_current = sha256_of_file(output) if output.is_file() else None

    if is_aggregate:
        # D-072: constitution.md uses synthetic source
        # "aggregate(arch/decisions/*.arch.json)". Recompute by hashing the
        # concatenated per-aspect SHAs in the project's pinned decisions.
        source_current = _recompute_aggregate_source_sha(
            entry, project_root)
    elif is_composite:
        source_current = _recompute_composite_source_sha(
            entry, workspace, project_root)
    else:
        source = workspace / entry["source"]
        source_current = sha256_of_file(source) if source.is_file() else None

    if source_current is None:
        state = "source_missing"
    elif output_current is None:
        state = "output_missing"
    elif source_current != entry["source_sha"] and output_current != entry["output_sha"]:
        state = "drifted"
    elif source_current != entry["source_sha"]:
        state = "source_changed"
    elif output_current != entry["output_sha"]:
        state = "locally_modified"
    else:
        state = "synced"

    return {
        "aspect": aspect_key,
        "state": state,
        "source": entry["source"],
        "output": entry["output"],
        "source_sha_pinned": entry["source_sha"],
        "source_sha_current": source_current,
        "output_sha_pinned": entry["output_sha"],
        "output_sha_current": output_current,
    }


def read_lock(project_root: Path) -> dict[str, Any]:
    """Load and validate the lock file."""
    target = project_root / LOCK_FILENAME
    if not target.is_file():
        raise FileNotFoundError(
            f"{LOCK_FILENAME} not found at {project_root}. "
            f"Was the project generated with /new-project?"
        )
    lock = json.loads(target.read_text(encoding="utf-8"))
    schema = lock.get("_schema_version")
    if schema != SCHEMA_VERSION:
        raise ValueError(
            f"{LOCK_FILENAME} schema version {schema!r} is not supported; "
            f"this tool understands version {SCHEMA_VERSION}."
        )
    return lock
