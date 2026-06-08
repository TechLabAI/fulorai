#!/usr/bin/env python3
"""sync-techlab-ai.py — Materialize a docs-only snapshot of techlab-ai.

This script implements decision D-048 (docs-only sync) and creates/refreshes
`integrations/techlab-ai/` inside the consumer project. It does NOT install
or build anything beyond pulling files; the Gradle plugin in
`backend/services/techlab-ai-client-lib/build.gradle.kts` regenerates Java
DTOs automatically on next build (D-051).

Sync strategies (in order of preference):

  C — From `docs/openapi.json` versioned in the techlab-ai repo (primary)
      Trivial `git show <sha>:docs/openapi.json` + clone of docs/ tree.
      Requires the techlab-ai repo to have the export-openapi.yml workflow
      committing docs/openapi.json on each push.

  B — From the Docker image (fallback)
      `docker run` the published image, curl /openapi.json, then `docker stop`.
      Used when docs/openapi.json is not available at the requested SHA.

  --from-local <path> (dev mode)
      Pull docs and openapi.json from a local clone of techlab-ai instead of
      from GitHub. Useful before the repo is published publicly.

Usage:
    # Production: sync to a specific SHA from GitHub
    python scripts/sync-techlab-ai.py --target-sha abc1234

    # Dev: sync from local clone
    python scripts/sync-techlab-ai.py --from-local ~/dev/techlab-ai --target-sha abc1234

    # Force Docker fallback (skip C strategy)
    python scripts/sync-techlab-ai.py --target-sha abc1234 --force-docker

    # Verify current snapshot integrity (no sync)
    python scripts/sync-techlab-ai.py --verify

What gets materialized:
    integrations/techlab-ai/
    ├── README.md                # upstream README at pinned SHA
    ├── openapi.json             # OpenAPI 3.x spec (source for DTO gen)
    ├── docs/                    # SDD.md, ADRs, SPECs, contracts, RUNBOOK
    └── .source-sha              # the pinned commit SHA

What gets updated in project-context.json:
    ai.techlabAi.sourceSha               ← target SHA
    ai.techlabAi.dockerImage.tag         ← short SHA (if tagFromSha=true)
    setup.phases[P3-techlab-ai-sync]     ← status: done
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_REPO = "https://github.com/DaniloAmaral-Dev/techlab-ai.git"
DEFAULT_DOCS_TARGET = "integrations/techlab-ai"
DEFAULT_HEALTH_TIMEOUT_S = 60
DEFAULT_HEALTH_POLL_S = 2


# ── Project context resolution ───────────────────────────────────────────────


def find_project_root(explicit: Path | None) -> Path:
    """Find project root by walking up looking for project-context.json."""
    if explicit:
        if not (explicit / "project-context.json").exists():
            sys.exit(f"error: {explicit}/project-context.json not found")
        return explicit.resolve()
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / "project-context.json").exists():
            return parent.resolve()
    sys.exit(
        "error: project-context.json not found in cwd or any parent directory. "
        "Run from inside a generated project."
    )


def load_context(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_context(path: Path, ctx: dict[str, Any]) -> None:
    ctx["lastUpdatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    path.write_text(json.dumps(ctx, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ── Logging helpers ──────────────────────────────────────────────────────────


def log(msg: str) -> None:
    print(f"[sync-techlab-ai] {msg}", flush=True)


def warn(msg: str) -> None:
    print(f"[sync-techlab-ai] WARN: {msg}", file=sys.stderr, flush=True)


def die(msg: str, code: int = 1) -> None:
    print(f"[sync-techlab-ai] ERROR: {msg}", file=sys.stderr, flush=True)
    sys.exit(code)


# ── Strategy C — Pull docs/openapi.json from git ─────────────────────────────


def strategy_c_from_git(
    repo_url: str,
    target_sha: str,
    work_dir: Path,
) -> tuple[Path, bool]:
    """Clone the techlab-ai repo (shallow) and check out target_sha.

    Returns (clone_path, openapi_was_versioned). If openapi_was_versioned is
    False, the snapshot still has README + docs/ but openapi.json must be
    obtained via strategy B.
    """
    log(f"Strategy C: cloning {repo_url} at {target_sha[:7]}")
    clone_path = work_dir / "techlab-ai-clone"

    # Try shallow clone at a tag/branch first; fall back to full clone for a specific SHA.
    try:
        subprocess.run(
            ["git", "clone", "--quiet", "--filter=blob:none", repo_url, str(clone_path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        die(f"git clone failed: {e.stderr or e.stdout}")
    except FileNotFoundError:
        die("git not found on PATH")

    try:
        subprocess.run(
            ["git", "-C", str(clone_path), "checkout", "--quiet", target_sha],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        die(f"git checkout {target_sha[:7]} failed: {e.stderr or e.stdout}")

    log(f"  cloned at {clone_path}")

    # Look for versioned openapi at docs/openapi.json (root) OR in techlab_ai/docs/openapi.json
    openapi_candidates = [
        clone_path / "docs" / "openapi.json",
        clone_path / "techlab_ai" / "docs" / "openapi.json",
    ]
    openapi_path = next((p for p in openapi_candidates if p.exists()), None)
    openapi_versioned = openapi_path is not None

    if openapi_versioned:
        log(f"  found versioned openapi.json at {openapi_path.relative_to(clone_path)}")
    else:
        warn("docs/openapi.json not versioned in this SHA — will fall back to strategy B")

    return clone_path, openapi_versioned


def strategy_c_from_local(local_path: Path, target_sha: str) -> tuple[Path, bool]:
    """Use a local clone of techlab-ai instead of fetching from GitHub.

    Validates that the local repo's HEAD matches target_sha (warns if not).
    """
    log(f"Strategy C (local): using {local_path}")
    if not local_path.exists():
        die(f"--from-local path does not exist: {local_path}")
    if not (local_path / ".git").exists() and not (local_path / "techlab_ai").exists():
        die(f"--from-local path does not look like a techlab-ai checkout: {local_path}")

    # Best-effort SHA check
    if (local_path / ".git").exists():
        try:
            result = subprocess.run(
                ["git", "-C", str(local_path), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            )
            actual_sha = result.stdout.strip()
            if target_sha and not actual_sha.startswith(target_sha) and not target_sha.startswith(actual_sha[:7]):
                warn(
                    f"local HEAD ({actual_sha[:7]}) does not match --target-sha ({target_sha[:7]})"
                )
        except subprocess.CalledProcessError:
            warn("could not verify local SHA")

    openapi_candidates = [
        local_path / "docs" / "openapi.json",
        local_path / "techlab_ai" / "docs" / "openapi.json",
    ]
    openapi_path = next((p for p in openapi_candidates if p.exists()), None)
    openapi_versioned = openapi_path is not None

    if openapi_versioned:
        log(f"  found versioned openapi.json at {openapi_path.relative_to(local_path)}")
    else:
        warn("docs/openapi.json not present in local checkout — will fall back to strategy B")

    return local_path, openapi_versioned


# ── Strategy B — Pull openapi.json from running Docker container ─────────────


def strategy_b_from_docker(
    docker_image: str,
    port: int,
    timeout_s: int = DEFAULT_HEALTH_TIMEOUT_S,
    allow_missing: bool = False,
) -> bytes | None:
    """Pull the Docker image, start it, fetch /openapi.json, stop it.

    Returns the openapi.json bytes. On failure: dies, unless `allow_missing`
    is set (D-294) — then it warns and returns None so the caller can still
    materialize a docs-only snapshot (README + docs/) without openapi.json.
    Useful when the GHCR image is private/unauthenticated or the per-commit
    tag was never published.
    """
    def _fail(msg: str) -> None:
        if allow_missing:
            warn(f"{msg} — continuing without openapi.json (docs-only snapshot)")
            return None
        die(msg)

    log(f"Strategy B: pulling Docker image {docker_image}")
    try:
        subprocess.run(
            ["docker", "pull", docker_image],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        return _fail(f"docker pull failed: {e.stderr or e.stdout}")
    except FileNotFoundError:
        return _fail("docker not found on PATH (strategy B requires Docker)")

    container_name = f"techlab-ai-sync-{int(time.time())}"
    log(f"  starting container {container_name} on port {port}")

    # Run with minimal env to skip auth and external deps
    env_args = []
    for key, val in [
        ("TECHLAB_AI_ENV", "local"),
        ("TECHLAB_AI_JWT_ENABLED", "false"),
        ("TECHLAB_AI_DB_HOST", "skip"),  # the service should still respond to /openapi.json without DB
    ]:
        env_args += ["-e", f"{key}={val}"]

    try:
        subprocess.run(
            ["docker", "run", "-d", "--rm", "--name", container_name,
             "-p", f"{port}:8090", *env_args, docker_image],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        return _fail(f"docker run failed: {e.stderr or e.stdout}")

    try:
        # Wait for /openapi.json to respond
        log(f"  waiting up to {timeout_s}s for /openapi.json")
        openapi_bytes = _poll_openapi(port, timeout_s, allow_missing=allow_missing)
        return openapi_bytes
    finally:
        log(f"  stopping container {container_name}")
        subprocess.run(
            ["docker", "stop", container_name],
            capture_output=True,
            text=True,
        )


def _poll_openapi(port: int, timeout_s: int,
                  allow_missing: bool = False) -> bytes | None:
    """Poll http://localhost:<port>/openapi.json until it returns 200 or timeout."""
    import urllib.error
    import urllib.request

    deadline = time.time() + timeout_s
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(
                f"http://localhost:{port}/openapi.json", timeout=5
            ) as resp:
                if resp.status == 200:
                    return resp.read()
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            last_err = e
        time.sleep(DEFAULT_HEALTH_POLL_S)
    if allow_missing:
        warn(f"timed out waiting for /openapi.json: {last_err} — "
             f"continuing without it")
        return None
    die(f"timed out waiting for /openapi.json: {last_err}")


# ── Materialize snapshot ─────────────────────────────────────────────────────


def materialize_snapshot(
    source_path: Path,
    target_dir: Path,
    target_sha: str,
    openapi_bytes: bytes | None,
) -> None:
    """Copy README + docs/ from source_path into target_dir, write openapi.json + .source-sha."""
    log(f"Materializing snapshot into {target_dir}")
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True)

    # README.md (root of techlab-ai)
    readme_candidates = [
        source_path / "README.md",
        source_path / "techlab_ai" / "README.md",
    ]
    readme_src = next((p for p in readme_candidates if p.exists()), None)
    if readme_src:
        shutil.copy2(readme_src, target_dir / "README.md")
        log(f"  copied README.md from {readme_src.name}")
    else:
        warn("README.md not found in source — skipping")

    # docs/ tree
    docs_candidates = [
        source_path / "docs",
        source_path / "techlab_ai" / "docs",
    ]
    docs_src = next((p for p in docs_candidates if p.exists()), None)
    if docs_src:
        shutil.copytree(docs_src, target_dir / "docs")
        n_files = sum(1 for _ in (target_dir / "docs").rglob("*") if _.is_file())
        log(f"  copied docs/ tree ({n_files} files)")
    else:
        warn("docs/ tree not found in source — skipping")

    # openapi.json — either from strategy C versioned, or strategy B bytes
    if openapi_bytes is not None:
        (target_dir / "openapi.json").write_bytes(openapi_bytes)
        log(f"  wrote openapi.json ({len(openapi_bytes)} bytes)")
    else:
        # Strategy C versioned — copy from source
        versioned_candidates = [
            source_path / "docs" / "openapi.json",
            source_path / "techlab_ai" / "docs" / "openapi.json",
        ]
        versioned = next((p for p in versioned_candidates if p.exists()), None)
        if versioned:
            shutil.copy2(versioned, target_dir / "openapi.json")
            log(f"  copied versioned openapi.json ({versioned.stat().st_size} bytes)")
        else:
            warn("no openapi.json materialized — Java DTO generation will not work")

    # .source-sha
    (target_dir / ".source-sha").write_text(target_sha.strip() + "\n", encoding="utf-8")
    log(f"  wrote .source-sha = {target_sha[:7]}")


# ── Verification ─────────────────────────────────────────────────────────────


def verify_snapshot(target_dir: Path) -> int:
    """Check the snapshot has the expected files and report."""
    log(f"Verifying snapshot at {target_dir}")
    if not target_dir.exists():
        die(f"target dir does not exist: {target_dir}")

    issues = 0
    for required in ["README.md", "openapi.json", ".source-sha"]:
        path = target_dir / required
        if not path.exists():
            warn(f"missing: {required}")
            issues += 1
        else:
            log(f"  ✓ {required} ({path.stat().st_size} bytes)")

    docs = target_dir / "docs"
    if not docs.is_dir():
        warn("missing: docs/ tree")
        issues += 1
    else:
        n_files = sum(1 for _ in docs.rglob("*") if _.is_file())
        log(f"  ✓ docs/ ({n_files} files)")

    sha_file = target_dir / ".source-sha"
    if sha_file.exists():
        sha = sha_file.read_text().strip()
        log(f"  pinned SHA: {sha[:7] if sha else 'EMPTY'}")

    openapi = target_dir / "openapi.json"
    if openapi.exists():
        try:
            data = json.loads(openapi.read_text())
            if "info" in data and "x-source-commit" in data["info"]:
                log(f"  openapi x-source-commit: {data['info']['x-source-commit'][:7]}")
            paths = data.get("paths", {})
            log(f"  openapi declares {len(paths)} endpoints")
        except json.JSONDecodeError as e:
            warn(f"openapi.json is not valid JSON: {e}")
            issues += 1

    if issues == 0:
        log("OK: snapshot is valid")
        return 0
    log(f"FAIL: {issues} issue(s) found")
    return 2


# ── Context updates ──────────────────────────────────────────────────────────


def update_context(
    project_root: Path,
    target_sha: str,
) -> None:
    """Update project-context.json: ai.techlabAi.sourceSha + dockerImage.tag + phase P3."""
    ctx_path = project_root / "project-context.json"
    ctx = load_context(ctx_path)

    tlab = ctx.get("ai", {}).get("techlabAi")
    if not tlab:
        warn("project-context.json has no ai.techlabAi block — skipping context update")
        return

    tlab["sourceSha"] = target_sha
    docker_cfg = tlab.get("dockerImage", {})
    if docker_cfg.get("tagFromSha"):
        docker_cfg["tag"] = target_sha[:7]

    # Mark P3 as done
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for phase in ctx.get("setup", {}).get("phases", []):
        if phase.get("id") == "P3-techlab-ai-sync":
            if "startedAt" not in phase:
                phase["startedAt"] = now
            phase["completedAt"] = now
            phase["status"] = "done"
            break

    save_context(ctx_path, ctx)
    log(f"updated project-context.json (sourceSha={target_sha[:7]})")


# ── Main ─────────────────────────────────────────────────────────────────────


def _resolve_latest_sha(repo_url: str, from_local: Path | None) -> str:
    """Resolve the 'latest' sentinel to a concrete commit SHA.

    A snapshot must pin an immutable SHA (D-048); 'latest' is a convenience
    sentinel meaning 'the current default-branch HEAD', resolved here ONCE so
    the docker tag, .source-sha and project-context all record the real commit
    (never the literal string 'latest', which is not a valid git ref).
    """
    if from_local:
        cmd = ["git", "-C", str(from_local), "rev-parse", "HEAD"]
    else:
        cmd = ["git", "ls-remote", repo_url, "HEAD"]
    try:
        out = subprocess.run(
            cmd, check=True, capture_output=True, text=True).stdout
    except subprocess.CalledProcessError as e:
        die(f"could not resolve 'latest' SHA: {e.stderr or e.stdout}")
    except FileNotFoundError:
        die("git not found on PATH")
    sha = out.split()[0].strip() if out.strip() else ""
    if not sha:
        die(f"could not resolve 'latest' SHA via `{' '.join(cmd)}` (empty output)")
    return sha


def cmd_sync(args: argparse.Namespace) -> int:
    project_root = find_project_root(args.project_root)
    ctx = load_context(project_root / "project-context.json")

    tlab = ctx.get("ai", {}).get("techlabAi", {})
    target_dir = project_root / (
        args.target_dir or tlab.get("docsCloneTarget", DEFAULT_DOCS_TARGET)
    )

    target_sha = args.target_sha or tlab.get("sourceSha")
    if not target_sha or target_sha == "PENDING_FIRST_COMMIT":
        die(
            "no target SHA: pass --target-sha or set ai.techlabAi.sourceSha "
            "in project-context.json"
        )

    repo_url = args.repo_url or tlab.get("source", DEFAULT_REPO)

    # Resolve the 'latest' sentinel to a concrete SHA up front (D-048): the
    # docker tag, .source-sha and snapshot must all pin an immutable commit.
    if target_sha == "latest":
        target_sha = _resolve_latest_sha(repo_url, args.from_local)
        log(f"resolved 'latest' → {target_sha[:7]}")

    docker_cfg = tlab.get("dockerImage", {})
    # GHCR (and the OCI spec) require the repository path to be lowercase, but
    # the GitHub owner is commonly written mixed-case (DaniloAmaral-Dev). Lower
    # the image path so the pull reference is valid; the registry host is left
    # untouched.
    docker_image_path = docker_cfg.get('image', 'DaniloAmaral-Dev/techlab-ai').lower()
    docker_image_base = f"{docker_cfg.get('registry', 'ghcr.io')}/{docker_image_path}"
    docker_tag = target_sha[:7] if docker_cfg.get("tagFromSha", True) else (docker_cfg.get("tag") or "latest")
    docker_image = f"{docker_image_base}:{docker_tag}"
    docker_port = tlab.get("ports", {}).get("service", 8090)

    log(f"target SHA: {target_sha[:7]} | target dir: {target_dir.relative_to(project_root)}")

    with tempfile.TemporaryDirectory(prefix="tlab-sync-") as tmp:
        work_dir = Path(tmp)

        # Step 1: strategy C — clone repo (local or remote)
        if args.from_local:
            source_path, openapi_versioned = strategy_c_from_local(args.from_local, target_sha)
        else:
            source_path, openapi_versioned = strategy_c_from_git(repo_url, target_sha, work_dir)

        # Step 2: if openapi NOT versioned, fall back to strategy B
        openapi_bytes: bytes | None = None
        if not openapi_versioned or args.force_docker:
            if args.force_docker:
                log("--force-docker requested, using strategy B")
            else:
                log("strategy C did not yield openapi.json, falling back to strategy B")
            openapi_bytes = strategy_b_from_docker(
                docker_image, docker_port,
                allow_missing=args.allow_missing_openapi)

        # Step 3: materialize snapshot
        materialize_snapshot(source_path, target_dir, target_sha, openapi_bytes)
        if openapi_bytes is None:
            warn("snapshot materialized WITHOUT openapi.json — re-run "
                 "`sync-techlab-ai.py sync` after `docker login ghcr.io` "
                 "(or once openapi.json is versioned upstream) to complete it")

    # Step 4: update project-context.json
    update_context(project_root, target_sha)

    log("DONE")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    project_root = find_project_root(args.project_root)
    ctx = load_context(project_root / "project-context.json")
    target_dir = project_root / (
        args.target_dir
        or ctx.get("ai", {}).get("techlabAi", {}).get("docsCloneTarget", DEFAULT_DOCS_TARGET)
    )
    return verify_snapshot(target_dir)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sync-techlab-ai.py",
        description="Materialize a docs-only snapshot of techlab-ai (D-048)",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root (default: walk up to find project-context.json)",
    )

    sub = parser.add_subparsers(dest="command")

    p_sync = sub.add_parser("sync", help="Sync snapshot to a target SHA (default subcommand)")
    p_sync.add_argument("--target-sha", help="Target commit SHA (default: from project-context.json)")
    p_sync.add_argument("--repo-url", help=f"Repository URL (default: {DEFAULT_REPO})")
    p_sync.add_argument("--target-dir", help=f"Target dir within project (default: {DEFAULT_DOCS_TARGET})")
    p_sync.add_argument(
        "--from-local",
        type=Path,
        help="Use a local clone of techlab-ai instead of GitHub (dev mode)",
    )
    p_sync.add_argument(
        "--force-docker",
        action="store_true",
        help="Skip strategy C openapi versioning, always use Docker (strategy B)",
    )
    p_sync.add_argument(
        "--allow-missing-openapi",
        action="store_true",
        help="(D-294) If strategy B (Docker) can't yield openapi.json (private "
             "GHCR image / unpublished tag), warn and materialize a docs-only "
             "snapshot (README + docs/) instead of aborting. Re-sync later to "
             "complete openapi.json.",
    )
    p_sync.set_defaults(func=cmd_sync)

    p_ver = sub.add_parser("verify", help="Validate the current snapshot")
    p_ver.add_argument("--target-dir", help=f"Snapshot dir (default: from context)")
    p_ver.set_defaults(func=cmd_verify)

    # If no subcommand given, default to sync (with positional args allowed)
    return parser


def main(argv: list[str] | None = None) -> int:
    from cli_utils import force_utf8_stdio
    force_utf8_stdio()
    parser = build_parser()
    # Support invocation without a subcommand (default to sync)
    argv_list = list(argv) if argv is not None else sys.argv[1:]
    known_commands = {"sync", "verify"}
    if argv_list and argv_list[0] not in known_commands and not argv_list[0].startswith("-"):
        argv_list = ["sync"] + argv_list
    elif not argv_list or (argv_list and argv_list[0].startswith("-") and "sync" not in argv_list and "verify" not in argv_list):
        argv_list = ["sync"] + argv_list

    args = parser.parse_args(argv_list)
    if not args.command:
        args = parser.parse_args(["sync"] + argv_list)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
