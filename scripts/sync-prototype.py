#!/usr/bin/env python3
"""sync-prototype.py — Vendor the frontend design prototype into the project.

Copies the HTML/CSS prototype directory from an external source into
frontend/design-reference/ (canonical vendored location per D-314).

Ensures the prototype is version-controlled within the generated project,
making it self-contained (R4) and reproducible for all team members.
Supports drift detection via a SHA-256 fingerprint of the source directory.

Usage:
    python scripts/sync-prototype.py sync
    python scripts/sync-prototype.py sync --source /absolute/path/to/frontend-reference
    python scripts/sync-prototype.py sync --target /path/to/project
    python scripts/sync-prototype.py status

Source resolution (sync):
    1. --source flag (explicit absolute path).
    2. project-context.json → _extensions.frontend_reference.path (set by ingest_discovery).

R3: argparse subcommands, atomic-safe copy, OK:/error:, exit 0/1/2.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VENDOR_RELATIVE = "frontend/design-reference"
SCREEN_GLOB = "*-screen-*.html"


# ── Project context helpers ───────────────────────────────────────────────────


def find_project_root(explicit: Path | None) -> Path:
    """Walk up from CWD looking for project-context.json."""
    if explicit:
        if not (explicit / "project-context.json").exists():
            sys.exit(f"error: {explicit}/project-context.json not found")
        return explicit.resolve()
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / "project-context.json").exists():
            return parent.resolve()
    sys.exit("error: project-context.json not found (run from inside the project)")


def load_context(root: Path) -> dict[str, Any]:
    path = root / "project-context.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"error: project-context.json is not valid JSON: {exc}")


def save_context(root: Path, ctx: dict[str, Any]) -> None:
    """Atomic write with refreshed lastUpdatedAt."""
    ctx["lastUpdatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    path = root / "project-context.json"
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(ctx, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


# ── Directory fingerprint ─────────────────────────────────────────────────────


def _dir_hash(directory: Path) -> str:
    """SHA-256 fingerprint of all files in a directory (sorted, stable)."""
    h = hashlib.sha256()
    for f in sorted(directory.rglob("*")):
        if f.is_file():
            rel = f.relative_to(directory).as_posix()
            h.update(rel.encode())
            h.update(f.read_bytes())
    return h.hexdigest()[:16]


# ── Source resolution ─────────────────────────────────────────────────────────


def _resolve_source(ctx: dict[str, Any], source_arg: str | None) -> Path | None:
    """Return the external source directory path, or None if not found."""
    if source_arg:
        p = Path(source_arg).resolve()
        if not p.exists():
            print(f"error: --source path does not exist: {p}", file=sys.stderr)
            return None
        if not p.is_dir():
            print(f"error: --source must be a directory: {p}", file=sys.stderr)
            return None
        return p

    ext_path = ctx.get("_extensions", {}).get("frontend_reference", {}).get("path", "")
    if ext_path:
        p = Path(ext_path)
        if p.exists() and p.is_dir():
            return p
        print(
            f"error: _extensions.frontend_reference.path ({ext_path}) does not exist.\n"
            "       Provide --source or update the path in project-context.json.",
            file=sys.stderr,
        )
        return None

    print(
        "error: no prototype source found.\n"
        "       Provide --source or run ingest_discovery to populate\n"
        "       _extensions.frontend_reference.path in project-context.json.",
        file=sys.stderr,
    )
    return None


# ── Subcommands ───────────────────────────────────────────────────────────────


def cmd_sync(args: argparse.Namespace) -> int:
    root = find_project_root(Path(args.target) if args.target else None)
    ctx = load_context(root)

    source = _resolve_source(ctx, args.source)
    if source is None:
        return 1

    vendor_dst = root / VENDOR_RELATIVE
    existing_hash = ctx.get("_extensions", {}).get("frontend_reference", {}).get("vendorHash", "")

    source_hash = _dir_hash(source)

    if vendor_dst.exists() and existing_hash and existing_hash == source_hash and not args.force:
        screen_count = len(list(vendor_dst.glob(SCREEN_GLOB)))
        print(f"OK: prototype already up-to-date (hash {source_hash}, {screen_count} screens)")
        return 0

    # Copy (overwrite)
    if vendor_dst.exists():
        shutil.rmtree(vendor_dst)
    shutil.copytree(source, vendor_dst)

    file_count = len([f for f in vendor_dst.rglob("*") if f.is_file()])
    screen_count = len(list(vendor_dst.glob(SCREEN_GLOB)))

    # Update context
    ctx.setdefault("stack", {}).setdefault("frontend", {})["prototypePath"] = VENDOR_RELATIVE
    ext_fr = ctx.setdefault("_extensions", {}).setdefault("frontend_reference", {})
    ext_fr["path"] = str(source)
    ext_fr["vendorPath"] = VENDOR_RELATIVE
    ext_fr["vendorHash"] = source_hash
    ext_fr["vendorSyncedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ext_fr["screen_count"] = screen_count
    ext_fr["has_tokens"] = (vendor_dst / "00-tokens.css").is_file()
    ext_fr["css_files"] = len(list(vendor_dst.glob("*.css")))

    save_context(root, ctx)

    action = "updated" if existing_hash and existing_hash != source_hash else "synced"
    print(f"OK: prototype {action} → {VENDOR_RELATIVE}/ ({file_count} files, {screen_count} screens, hash {source_hash})")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    root = find_project_root(Path(args.target) if args.target else None)
    ctx = load_context(root)

    ext_fr = ctx.get("_extensions", {}).get("frontend_reference", {})
    vendor_path_rel = ext_fr.get("vendorPath", VENDOR_RELATIVE)
    vendor_dst = root / vendor_path_rel
    source_path = ext_fr.get("path", "")
    vendor_hash = ext_fr.get("vendorHash", "")
    synced_at = ext_fr.get("vendorSyncedAt", "never")

    print(f"Source:      {source_path or '(not set)'}")
    print(f"Vendor path: {vendor_path_rel}")
    print(f"Vendor hash: {vendor_hash or '(not synced)'}")
    print(f"Synced at:   {synced_at}")
    print(f"Exists:      {'yes' if vendor_dst.exists() else 'NO — run sync'}")

    if vendor_dst.exists():
        screens = list(vendor_dst.glob(SCREEN_GLOB))
        print(f"Screens:     {len(screens)}")
        has_tokens = (vendor_dst / "00-tokens.css").is_file()
        print(f"Tokens CSS:  {'yes' if has_tokens else 'no'}")

        if source_path and Path(source_path).exists():
            current_hash = _dir_hash(Path(source_path))
            if current_hash != vendor_hash:
                print(f"Drift:       YES — source changed (current {current_hash} ≠ vendor {vendor_hash})")
                print("             Run: python scripts/sync-prototype.py sync")
            else:
                print(f"Drift:       none")
        else:
            print("Drift:       unknown (source path not accessible)")

    return 0


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="sync-prototype",
        description="Vendor the frontend design prototype into frontend/design-reference/.",
    )
    parser.add_argument("--target", metavar="DIR", help="Project root (default: walk up from CWD)")

    sub = parser.add_subparsers(dest="command", required=True)

    sync_p = sub.add_parser("sync", help="Copy prototype from source to frontend/design-reference/")
    sync_p.add_argument("--source", metavar="DIR", help="Absolute path to source prototype directory")
    sync_p.add_argument("--force", action="store_true", help="Re-copy even if hash matches")

    status_p = sub.add_parser("status", help="Show sync status and drift check")
    _ = status_p  # no extra args

    args = parser.parse_args()

    if args.command == "sync":
        sys.exit(cmd_sync(args))
    elif args.command == "status":
        sys.exit(cmd_status(args))


if __name__ == "__main__":
    main()
