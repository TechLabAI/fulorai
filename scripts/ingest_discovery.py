#!/usr/bin/env python3
"""ingest_discovery.py — Discovery → project-context.json ingestion (D-073).

Reads a discovery directory (the user's Business Analysis output: lean-business-
case, technical-framing, ADRs, glossary, wireframe, etc.) and derives a
populated `project-context.json` ready for /new-project P0.

Strategy: rules + heuristics (regex / headers / sections). No LLM. Markdown
input is structured enough — when a field can't be confidently extracted, it
lands in `unresolved_questions` for the user to fill in.

Canonical discovery directory shape (see exemplos_bosq/ for reference):

    <discovery>/
    ├── business/
    │   ├── lean-business-case.md      (REQUIRED)
    │   ├── glossary.md                 (REQUIRED)
    │   ├── stakeholders.md             (recommended)
    │   ├── technical-framing.md        (recommended — extracts many fields)
    │   ├── success-metrics.md          (optional)
    │   └── constraints.md              (optional)
    ├── architecture/
    │   └── adr/
    │       ├── ADR-001-*.md            (≥1 REQUIRED)
    │       └── ADR-NNN-*.md
    └── design/                          (optional)
        ├── ui-concept.md
        ├── wireframe.md
        └── prototype-*                  (excess — referenced, NOT parsed)

The orchestrator is `ingest_discovery(path) → (context_dict, unresolved_list,
adr_files_list)`. Callers (cmd_bootstrap in new-project.py) write the dict +
unresolved questions + copy ADRs into the target.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ── Small text utilities ─────────────────────────────────────────────────────


def _slugify(text: str) -> str:
    """'BOSQ Lean OS' → 'bosq-lean-os'; '.ai' suffix dropped; ASCII only."""
    s = text.lower().strip()
    s = s.replace(".ai", "").replace(".com", "")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s


def _codename(text: str) -> str:
    """Identifier-safe form: lowercase, alphanumerics only (no hyphen/dot/_).

    'sped-map-elastic' → 'spedmapelastic'. Used as fallback to derive Java
    packageBase (`com.<codeName>`), npm scope (`@<codeName>`) and Postgres
    globalSchema (`<codeName>_global`) — the kebab-case name is NOT valid in
    a Java package (hyphen). A human-chosen codeName in the handoff (e.g.
    'spedmap') overrides this fallback.
    """
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _h1(text: str) -> str | None:
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else None


def _section(text: str, heading_pattern: str) -> str | None:
    """Return body of a section (`## <heading_pattern>`) until next `## ` line."""
    rx = re.compile(rf"^##\s+{heading_pattern}.*?$\n(.*?)(?=^##\s+|\Z)",
                    re.MULTILINE | re.DOTALL)
    m = rx.search(text)
    return m.group(1).strip() if m else None


def _first_paragraph(text: str) -> str | None:
    """First non-quote, non-blank paragraph of a section body."""
    for raw_para in text.split("\n\n"):
        para = raw_para.strip()
        if not para or para.startswith(">"):
            continue
        # Skip bullet lists, headers, code fences.
        if para.startswith(("#", "-", "*", "```", "|")):
            continue
        # Strip markdown emphasis for cleaner output.
        cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", para)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip()
    return None


# ── Parser functions (one per artifact type) ─────────────────────────────────


@dataclass
class IngestionResult:
    """Output of the full ingestion run.

    `context` is a partial project-context.json — keys present are confidently
    extracted; missing keys are filled by `merge_into_context` from defaults
    (or surfaced as unresolved questions).

    `aspect_overrides` is a dict[aspect_name → partial_dict] meant to be
    written to `<target>/arch/overrides/<aspect>.partial.json` (D-074). P2
    deep-merges each partial onto the workspace's default aspect before
    pinning the snapshot.
    """
    context: dict[str, Any] = field(default_factory=dict)
    unresolved: list[str] = field(default_factory=list)
    adr_files: list[Path] = field(default_factory=list)
    sources: dict[str, str] = field(default_factory=dict)
    aspect_overrides: dict[str, dict[str, Any]] = field(default_factory=dict)
    """Per-field provenance: 'project.name' → 'business/lean-business-case.md'."""


def parse_lean_business_case(path: Path) -> dict[str, Any]:
    """Extract project.name, displayName, description, and classification hints.

    Patterns expected:
      - H1: '# Lean Business Case — <product>'
      - blockquote: '> **Produto:** <product>'
      - blockquote: '> **Classificação:** Produto SaaS B2B externo / ...'
        → drives multi_tenancy.mode hint (D-076)
      - section '## 1. Executive Summary' first paragraph → description
    """
    text = _read(path)
    out: dict[str, Any] = {}

    # Classification → mode hint (D-076). Prefer the explicit
    # '> **Classificação:**' blockquote; fall back to the product prose
    # (executive summary / pitch) so the hint is not lost when the LBC author
    # didn't use the exact blockquote format. Without this, a clearly
    # SaaS-B2B-multi-tenant product silently lost its mode hint, letting a
    # non-canonical handoff mode go unnormalized (breaks P2 rendering).
    m_cls = re.search(r">\s*\*\*Classifica[çc][ãa]o:\*\*\s*(.+?)\s*$",
                      text, re.MULTILINE)
    cls_text = m_cls.group(1).lower() if m_cls else text.lower()
    if "saas b2b" in cls_text or "saas multi" in cls_text \
            or "multi-tenant" in cls_text or "multitenant" in cls_text:
        out["mt_mode_hint"] = "multi-tenant"
    elif "interno" in cls_text or "internal" in cls_text \
            or "multi-empresa" in cls_text:
        out["mt_mode_hint"] = "multi-empresa"

    # Product display name: H1 dash-delimited tail, or **Produto:** blockquote.
    display = None
    h1 = _h1(text)
    if h1 and "—" in h1:
        display = h1.split("—", 1)[1].strip()
    if display is None:
        m = re.search(r">\s*\*\*Produto:\*\*\s*(.+?)\s*$", text, re.MULTILINE)
        if m:
            display = m.group(1).strip()
    if display:
        out["displayName"] = display
        out["name"] = _slugify(display)

    # Description: first real paragraph of §1 Executive Summary (or any §1).
    body = _section(text, r"1\.\s+Executive Summary") or _section(text, r"1\.")
    if body:
        para = _first_paragraph(body)
        if para:
            # Trim ridiculously long paragraphs to a sentence.
            if len(para) > 280:
                cut = para[:280].rfind(". ")
                if cut > 100:
                    para = para[:cut + 1]
            out["description"] = para

    return out


def parse_handoff_executables(path: Path) -> dict[str, Any]:
    """Parse the handoff §7.1 / 'Passo 0' executable YAML block.

    `handoff-package.md` (root of the discovery dir) carries a fenced code
    block with the project-context fields that are NOT auto-extractable from
    prose: codeName, segment, rigorLevel, issuePrefix, the FULL stack (incl.
    searchEngine/messaging), globalSchema and the module registry (domains,
    with 3-5 letter prefixes). Human-curated → consumed with highest
    precedence in the orchestrator. Decouples the ingestor from prose
    section numbers (fixes the 'Elasticsearch vanishes' / 'modules polluted'
    / 'invalid packageBase' classes of bug).
    """
    text = _read(path)
    out: dict[str, Any] = {}

    block = None
    for b in re.findall(r"```(?:ya?ml)?\s*\n(.*?)```", text, re.DOTALL):
        if ("project.codeName" in b or "modules.registry" in b
                or "stack.searchEngine" in b
                or "stack.elastic.indices" in b):    # D-305
            block = b
            break
    if not block:
        return out

    def scalar(key: str) -> str | None:
        m = re.search(rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", block, re.MULTILINE)
        if not m:
            return None
        v = re.split(r"\s+#", m.group(1))[0].strip().strip('"').strip("'")
        if not v or v.lower().startswith("n/a") or v.startswith("<"):
            return None
        return v

    for key, dst in (
        ("project.codeName", "codeName"),
        ("project.segment", "segment"),
        ("project.rigorLevel", "rigorLevel"),
        ("project.issuePrefix", "issuePrefix"),
        ("stack.backend.packageBase", "packageBase"),
        ("stack.frontend.npmScope", "npmScope"),
        ("stack.database", "database"),
        ("stack.searchEngine", "searchEngine"),
        ("stack.messaging", "messaging"),
        ("stack.ai", "ai"),
        ("multiTenancy.mode", "mt_mode"),
        ("multiTenancy.globalSchema", "globalSchema"),
    ):
        v = scalar(key)
        if v is not None:
            out[dst] = v

    mods: list[dict[str, str]] = []
    for m in re.finditer(
            r"-\s*\{\s*prefix:\s*([A-Za-z0-9]+)\s*,\s*displayName:\s*"
            r"\"([^\"]+)\"\s*,\s*description:\s*\"([^\"]*)\"\s*\}", block):
        mods.append({"prefix": m.group(1).strip(),
                     "displayName": m.group(2).strip(),
                     "description": m.group(3).strip()})
    if mods:
        out["modules_registry"] = mods

    # D-305: parse stack.elastic.indices entries.
    # Format: - { slug: "name", displayName: "Label", class: "fact"|"dimension",
    #             domainContext: "MODULE", status: "declared" }
    def _kv(key: str, inner: str) -> str:
        km = re.search(rf'{key}\s*:\s*"([^"]*)"', inner)
        if km:
            return km.group(1).strip()
        km = re.search(rf'{key}\s*:\s*([^\s,}}]+)', inner)
        return km.group(1).strip() if km else ""

    idx_list: list[dict[str, str]] = []
    in_idx = False
    for line in block.splitlines():
        if re.match(r"\s*stack\.elastic\.indices\s*:", line):
            in_idx = True
            continue
        if in_idx:
            stripped = line.strip()
            if stripped and not stripped.startswith("-") and ":" in stripped and "{" not in stripped:
                break  # hit the next top-level key
            m = re.search(r"-\s*\{([^}]+)\}", line)
            if not m:
                continue
            inner = m.group(1)
            slug = _kv("slug", inner).lower()
            if not slug:
                continue
            idx_list.append({
                "slug":          slug,
                "displayName":   _kv("displayName", inner),
                "class":         _kv("class", inner),
                "domainContext": _kv("domainContext", inner),
                "status":        _kv("status", inner) or "declared",
            })
    if idx_list:
        out["elastic_indices"] = idx_list

    return out


_MODULE_HEADING_RE = re.compile(r"^###\s+(?:\d+\.\d+\s+)?([A-Z][\w\s\-&]+?)\s*$",
                                re.MULTILINE)


def parse_technical_framing(path: Path) -> dict[str, Any]:
    """Extract module candidates from §4 'Domínios Funcionais' ONLY.

    Modules = functional DOMAINS (§4). Components (§6) are classes/services
    *inside* a module, NOT modules — including them would pollute the registry
    with the same thing at two granularities (e.g. 'Ingestão' §4 and
    'SpedIngestionPipeline' §6). Each candidate has `displayName` but NO
    `prefix` (the 3-5 letter prefix is a human decision, surfaced as
    unresolved — or already provided by the handoff §7.1 registry).

    Stack is NOT parsed here anymore — it lives in ADRs (parse_adr) and is
    consolidated in the handoff §7.1. The old coupling to a prose '§15 Stack
    Recomendada' section was fragile (most framings don't have a §15) and made
    a primary engine like Elasticsearch silently vanish from the context.
    """
    text = _read(path)
    out: dict[str, Any] = {}
    candidates: list[dict[str, str]] = []
    seen: set[str] = set()

    body = _section(text, r"4\.\s+Domínios Funcionais") or ""
    for m in _MODULE_HEADING_RE.finditer(body):
        name = m.group(1).strip()
        # Drop trailing 'Service' for cleaner display.
        display = re.sub(r"\s+Service\s*$", "", name).strip()
        key = display.lower()
        if key in seen:
            continue
        seen.add(key)
        candidates.append({"displayName": display})

    if candidates:
        out["module_candidates"] = candidates

    return out


def parse_adr(path: Path) -> dict[str, Any]:
    """Extract decision from a single ADR file.

    Recognises common decisions and maps to project-context fields:
      - Backend language: 'Java 21', 'Kotlin', 'Python', 'Go'
      - Multi-tenancy isolation strategy
      - Frontend framework + monorepo tool
      - AI service strategy
    """
    text = _read(path)
    out: dict[str, Any] = {"_adr_id": path.stem, "_path": str(path)}

    # Title for surfacing in unresolved questions.
    h1 = _h1(text)
    if h1:
        out["_title"] = h1

    # The 'Decisão' section body is short — usually a single line of the form:
    #   Escolhida: **Opção A — Java 21 sobre JVM**.
    decision_body = _section(text, r"Decisão") or ""
    chosen = re.search(r"Escolhida:?\s*\*\*([^*]+)\*\*", decision_body)
    decision_text = chosen.group(1) if chosen else decision_body[:200]
    out["_decision"] = decision_text.strip()

    # Pattern-match the decision text against known keywords.
    # Use word-boundary regex so 'go' doesn't match 'hexagonal' (caught in
    # smoke testing).
    low = decision_text.lower()

    backend_patterns = [
        (r"\bjava\s+21\b", "java", "21"),
        (r"\bjava\s+17\b", "java", "17"),
        (r"\bkotlin\b", "kotlin", "1.9"),
        (r"\bpython\b", "python", "3.11"),
        (r"\bgo\b", "go", "1.21"),
    ]
    for pattern, lang, version in backend_patterns:
        if re.search(pattern, low):
            out["backend_language"] = lang
            out["backend_version"] = version
            break

    # Spring Boot mentioned anywhere in the ADR is a strong signal.
    if "spring boot" in text.lower():
        out["backend_framework"] = "spring-boot"

    # Multi-tenancy.
    if "schema-per-" in low or "schema per " in low:
        out["multi_tenancy_isolation"] = "schema-per-tenant"
        # If the title/text uses 'empresa', surface the term preference.
        if "empresa" in (h1 or "").lower() or "empresa" in decision_text.lower():
            out["multi_tenancy_term_hint"] = "empresa"
    elif "database-per-" in low:
        out["multi_tenancy_isolation"] = "database-per-tenant"
    elif "discriminator" in low or "tenant_id" in low or "tenant-id" in low:
        out["multi_tenancy_isolation"] = "tenant-id-column"

    # Hexagonal — flag for ADR generation downstream; no project-context field.
    if "hexagonal" in low or "ports & adapters" in low or "ports e adapters" in low:
        out["adopts_hexagonal"] = True

    # Frontend framework / monorepo.
    if "angular" in low:
        out["frontend_framework"] = "angular"
    elif "react" in low and "next" not in low:
        out["frontend_framework"] = "react"
    elif "next" in low:
        out["frontend_framework"] = "nextjs"
    if "nx " in low or "nx monorepo" in low or " nx" in low:
        out["frontend_monorepo"] = "nx"

    # AI service.
    if "techlab-ai" in text.lower() or "serviço dedicado" in low:
        out["has_ai_service"] = True

    # Stack engines — decisions live in ADRs (not in a prose stack section).
    # Scan the whole ADR text so a dedicated ADR (e.g. ADR-006 Elasticsearch)
    # is captured even when the keyword isn't in the one-line decision.
    full = text.lower()
    if "postgresql" in full or "postgres" in full:
        out["database_engine"] = "postgresql"
    elif "mysql" in full:
        out["database_engine"] = "mysql"
    elif "mongodb" in full or "mongo db" in full:
        out["database_engine"] = "mongodb"
    if "elasticsearch" in full or "elastic search" in full:
        out["search_engine"] = "elasticsearch"
    elif "opensearch" in full:
        out["search_engine"] = "opensearch"
    if "pgvector" in full:
        out["has_pgvector"] = True
    if "kafka" in full:
        out["messaging_engine"] = "kafka"
    elif "rabbitmq" in full or "rabbit mq" in full:
        out["messaging_engine"] = "rabbitmq"
    elif "activemq" in full:
        out["messaging_engine"] = "activemq"

    return out


_GLOSSARY_DOMAIN_HEADING_RE = re.compile(
    r"^##\s+Termos de domínio operacional\s*$\n(.*?)(?=^##\s+|\Z)",
    re.MULTILINE | re.DOTALL,
)


def parse_glossary(path: Path) -> dict[str, Any]:
    """Extract domain-operational vocabulary as candidates for ubiquitous
    language references. Doesn't directly populate project-context; surfaced
    as a comment in UNRESOLVED_QUESTIONS for the user to weigh into module
    naming.
    """
    text = _read(path)
    out: dict[str, Any] = {}

    m = _GLOSSARY_DOMAIN_HEADING_RE.search(text)
    if not m:
        return out
    body = m.group(1)
    # Each '### Term' becomes one entry.
    terms = re.findall(r"^###\s+(.+?)\s*$", body, re.MULTILINE)
    if terms:
        out["domain_vocabulary"] = [t.strip() for t in terms]
    return out


_STAKEHOLDER_HEADING_RE = re.compile(r"^###\s+([^\n]+?)\s*$", re.MULTILINE)


def parse_stakeholders(path: Path) -> dict[str, Any]:
    """Extract role identifiers from the 'Mapa de stakeholders' section.

    Returns `stakeholder_roles` — a list of clean role names (Sponsor,
    Arquiteto, Product Manager, ...). NOT applied to rbac.arch.json directly
    (that would be too aggressive — RBAC roles are domain-operational, not
    project-stakeholder); surfaced as a soft hint.
    """
    text = _read(path)
    body = _section(text, r"Mapa de stakeholders") or ""
    if not body:
        return {}
    roles: list[str] = []
    for m in _STAKEHOLDER_HEADING_RE.finditer(body):
        raw = m.group(1).strip()
        # Strip everything after a '/' to keep canonical form (e.g.
        # "Sponsor / Decisor principal" → "Sponsor").
        primary = raw.split("/")[0].strip()
        if primary and primary not in roles:
            roles.append(primary)
    return {"stakeholder_roles": roles} if roles else {}


_PERSONA_HEADING_RE = re.compile(
    r"^###\s+\d+\.\d+\s+Persona\s+\d+\s+[—-]\s+(.+?)\s*$", re.MULTILINE)


def parse_lbc_personas(path: Path) -> dict[str, Any]:
    """Extract LBC §4 personas as RBAC role candidates.

    LBC personas are the END USERS of the product (Diretor Industrial,
    Gerente de Produção, Coordenador Lean, Supervisor), distinct from
    stakeholders.md which captures PROJECT-MANAGEMENT roles (Sponsor, PM,
    BA). Personas map naturally to rbac.roles seeds for the GENERATED
    project — stakeholders do NOT.

    Returns `lbc_personas`: list[{role_code, role_name, description}].

    Naming convention for role_code: PT-BR title → SCREAMING_SNAKE,
    keeping the first canonical noun. Examples:
      "Diretor Industrial / Operações" → DIRETOR_INDUSTRIAL
      "Gerente de Produção / Obra / Operação" → GERENTE_PRODUCAO
      "Coordenador Lean / Melhoria Contínua" → COORDENADOR_LEAN
      "Supervisor / Líder de Turno" → SUPERVISOR_TURNO
    """
    text = _read(path)
    out: dict[str, Any] = {}
    personas: list[dict[str, str]] = []

    def _ascii(s: str) -> str:
        return (s.lower()
                .replace("ã", "a").replace("á", "a").replace("â", "a")
                .replace("é", "e").replace("ê", "e")
                .replace("í", "i")
                .replace("ó", "o").replace("ô", "o").replace("õ", "o")
                .replace("ú", "u").replace("ç", "c"))

    # Slash-tail folds drive the role_code tokens; the FULL title is kept as
    # role_name (so "Controller / Head de Compliance" isn't truncated). The
    # description comes from the persona BODY, not the heading (avoids a
    # description that just repeats role_name).
    matches = list(_PERSONA_HEADING_RE.finditer(text))
    for i, m in enumerate(matches):
        raw = m.group(1).strip()
        primary = raw.split("/")[0].strip()
        raw_ascii = _ascii(raw)
        primary_ascii = _ascii(primary)
        primary_tokens = [t for t in re.split(r"\s+", primary_ascii)
                          if t and t not in ("de", "do", "da", "dos", "das",
                                             "para", "e", "/")]
        if not primary_tokens:
            continue

        # Description from the persona body (until the next ## section).
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        nxt = re.search(r"^##\s", text[start:end], re.MULTILINE)
        body = text[start:start + nxt.start()] if nxt else text[start:end]
        desc = None
        mex = re.search(r"\*\*Exemplo[^:*]*:\*\*\s*(.+)", body)
        if mex:
            desc = mex.group(1)
        if not desc:
            desc = _first_paragraph(body)
        if not desc:
            # Body is all bold labels + bullets (no plain paragraph): take the
            # content of the first labelled block (Objetivo/Responsabilidades/…)
            # so the description doesn't just repeat role_name.
            mlab = re.search(
                r"\*\*(?:Objetivo|Responsabilidades|Dores|Contexto)[^\n]*\*\*\s*"
                r"(.+?)(?=\n\s*\*\*|\Z)", body, re.DOTALL)
            if mlab:
                chunk = re.sub(r"(?m)^[\s>\-*•]+", "", mlab.group(1))
                desc = re.sub(r"\s+", " ", chunk).strip() or None
        if not desc:
            desc = raw
        desc = re.sub(r"\*\*([^*]+)\*\*", r"\1", desc)
        desc = re.sub(r"\s+", " ", desc).strip()[:240]

        # Heuristic codes — order matters; first match wins.
        if "turno" in raw_ascii:
            tokens = ["supervisor", "turno"]
        elif "lean" in raw_ascii:
            tokens = ["coordenador", "lean"]
        elif "industrial" in raw_ascii:
            tokens = ["diretor", "industrial"]
        elif "producao" in raw_ascii:
            tokens = ["gerente", "producao"]
        else:
            tokens = primary_tokens[:2]
        role_code = "_".join(
            re.sub(r"[^a-z0-9]", "", t).upper() for t in tokens
            if re.sub(r"[^a-z0-9]", "", t))
        # Trim decorative tails ("(corporativo …)", "— *âncora MVP*", "⭐") but
        # KEEP slash alternates (e.g. "Controller / Head de Compliance").
        role_name = re.split(r"\s+\(|\s+[—-]\s+\*|\s+⭐", raw)[0].strip() or raw
        personas.append({
            "role_code": role_code,
            "role_name": role_name,
            "description": desc,
        })

    if personas:
        out["lbc_personas"] = personas
    return out


def parse_constraints(path: Path) -> dict[str, Any]:
    """Flag compliance topics declared in constraints.md (LGPD, retention).

    Adds `compliance.lgpd = True` and similar flags. Not a current schema
    field — surfaced as a project metadata extension for future
    compliance.arch.json aspect.
    """
    text = _read(path)
    out: dict[str, Any] = {}
    if re.search(r"REG-001.*LGPD|Lei 13\.709", text, re.IGNORECASE):
        out.setdefault("compliance", {})["lgpd"] = True
    if re.search(r"reten[çc][ãa]o.*\d+\s*anos", text, re.IGNORECASE):
        m = re.search(r"reten[çc][ãa]o.*?(\d+)\s*anos", text, re.IGNORECASE)
        if m:
            out.setdefault("compliance", {})["retention_years"] = int(m.group(1))
    return out


def parse_wireframe(path: Path) -> dict[str, Any]:
    """Detect screens declared in wireframe.md.

    Returns `wireframe_metadata` with screen count + flag that frontend is
    in scope. Does NOT enumerate components yet (Phase 2 of ingestion).

    Heuristics for screen count (first match wins):
      1. Explicit numeric mention: "12 telas" / "10 telas operacionais"
      2. Headers `### Tela <N>` or `## Tela <N>`
      3. Fallback: None — surface as unresolved.
    """
    text = _read(path)
    screen_count: int | None = None

    m = re.search(r"\b(\d+)\s+telas?\s+(?:operacionais?|principal|principais)?",
                  text, re.IGNORECASE)
    if m:
        screen_count = int(m.group(1))
    else:
        n = len(re.findall(r"^###?\s+Tela\s+\d+", text, re.MULTILINE))
        if n > 0:
            screen_count = n

    metadata: dict[str, Any] = {"path": str(path)}
    if screen_count is not None:
        metadata["screen_count"] = screen_count
    return {
        "wireframe_metadata": metadata,
        "has_frontend_design": True,
    }


# ── Orchestration ────────────────────────────────────────────────────────────


def derive_aspect_overrides(
    lbc_personas: list[dict[str, str]] | None = None,
) -> dict[str, dict[str, Any]]:
    """D-074: derive aspect overrides from discovery output.

    Currently produces:
      - `rbac` partial: `roles` replaced with LBC personas. enforcement +
        data_scope are NOT touched (those are conventions, not project data).

    NOT derived here (deferred to P2's `_resolve_decisions` which has access
    to the final `project-context.modules.registry`):
      - permission-catalogue.modules — derived from modules.registry
      - events.modules / error-model.modules / entity-scope.scopes —
        zeroed out (empty arrays) so the project starts with a clean slate
    """
    out: dict[str, dict[str, Any]] = {}

    if lbc_personas:
        roles: list[dict[str, Any]] = []
        for p in lbc_personas:
            roles.append({
                "code": p["role_code"],
                "name": p["role_name"],
                "description": p.get("description", p["role_name"]),
                "category": "default",
                "active": True,
                "data_scope_tipo": None,
                "permission_bundle": {
                    "kind": "all",
                    "note": ("TODO: refine permissions — defaulted to `all` "
                             "because per-role authority is not declared in "
                             "discovery. Edit before going to production."),
                },
            })
        out["rbac"] = {"roles": roles}

    return out


def _find(discovery_root: Path, rel: str) -> Path | None:
    p = discovery_root / rel
    return p if p.is_file() else None


def ingest_discovery(discovery_root: Path) -> IngestionResult:
    """Top-level orchestrator. Walks the canonical discovery layout, runs
    each parser, merges results into a project-context.json dict, records
    unresolved questions and ADR file paths.

    Raises FileNotFoundError for missing REQUIRED inputs:
      - business/lean-business-case.md
      - business/glossary.md
      - architecture/adr/ (must contain ≥1 ADR-NNN-*.md)
    """
    discovery_root = discovery_root.resolve()
    if not discovery_root.is_dir():
        raise FileNotFoundError(f"discovery directory not found: {discovery_root}")

    # Required gates.
    lbc = _find(discovery_root, "business/lean-business-case.md")
    if not lbc:
        raise FileNotFoundError(
            f"required input missing: {discovery_root}/business/lean-business-case.md")
    glossary = _find(discovery_root, "business/glossary.md")
    if not glossary:
        raise FileNotFoundError(
            f"required input missing: {discovery_root}/business/glossary.md")
    adr_dir = discovery_root / "architecture" / "adr"
    adr_files = sorted(adr_dir.glob("ADR-*.md")) if adr_dir.is_dir() else []
    if not adr_files:
        raise FileNotFoundError(
            f"required input missing: ≥1 ADR-NNN-*.md under {discovery_root}/architecture/adr/")

    result = IngestionResult(adr_files=adr_files)

    # Run parsers.
    lbc_out = parse_lean_business_case(lbc)
    personas_out = parse_lbc_personas(lbc)
    glossary_out = parse_glossary(glossary)
    adr_outs = [parse_adr(p) for p in adr_files]

    tf = _find(discovery_root, "business/technical-framing.md")
    tf_out = parse_technical_framing(tf) if tf else {}

    st = _find(discovery_root, "business/stakeholders.md")
    st_out = parse_stakeholders(st) if st else {}

    cs = _find(discovery_root, "business/constraints.md")
    cs_out = parse_constraints(cs) if cs else {}

    wf = _find(discovery_root, "design/wireframe.md")
    wf_out = parse_wireframe(wf) if wf else {}

    # Handoff §7.1 executable block (root of the discovery dir) — authoritative
    # source for codeName/segment/rigorLevel/issuePrefix/stack/globalSchema/modules.
    hf = _find(discovery_root, "handoff-package.md")
    hf_out = parse_handoff_executables(hf) if hf else {}

    # ── Merge into project-context shape ────────────────────────────────────

    ctx: dict[str, Any] = {
        "version": "v1.0",
        "generatedBy": "techlab-architecture /new-project (ingest_discovery, D-073)",
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "lastUpdatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "locale": {
            "primary": "pt-BR",
            "technicalDocs": "en-US",
            "humanFacingDocs": "pt-BR",
        },
    }

    # project.*
    project: dict[str, Any] = {}
    if "name" in lbc_out:
        project["name"] = lbc_out["name"]
        result.sources["project.name"] = "business/lean-business-case.md"
    if "displayName" in lbc_out:
        project["displayName"] = lbc_out["displayName"]
        result.sources["project.displayName"] = "business/lean-business-case.md"
    if "description" in lbc_out:
        project["description"] = lbc_out["description"]
        result.sources["project.description"] = "business/lean-business-case.md"
    # segment / rigorLevel / issuePrefix are not auto-extracted (see unresolved).
    if project:
        ctx["project"] = project

    # stack.* — aggregate hints from ADRs.
    stack: dict[str, Any] = {"backend": {}, "frontend": {}, "database": {},
                              "search": {}, "messaging": {}}
    for adr in adr_outs:
        for src, dest in [
            ("backend_language", ("backend", "language")),
            ("backend_version", ("backend", "version")),
            ("backend_framework", ("backend", "framework")),
            ("frontend_framework", ("frontend", "framework")),
            ("frontend_monorepo", ("frontend", "monorepoTool")),
        ]:
            if src in adr:
                stack[dest[0]][dest[1]] = adr[src]
                key = f"stack.{dest[0]}.{dest[1]}"
                result.sources[key] = f"architecture/adr/{Path(adr['_path']).name}"
    if any(adr.get("frontend_framework") for adr in adr_outs):
        stack["frontend"]["enabled"] = True
    elif wf_out.get("has_frontend_design"):
        stack["frontend"]["enabled"] = True
        result.sources["stack.frontend.enabled"] = "design/wireframe.md"

    # Stack engines (database / search / messaging) come from ADRs — stack
    # decisions live in ADR files, not in a prose section.
    for adr in adr_outs:
        nm = f"architecture/adr/{Path(adr['_path']).name}"
        if adr.get("database_engine") and not stack["database"].get("engine"):
            stack["database"]["engine"] = adr["database_engine"]
            result.sources["stack.database.engine"] = nm
        if adr.get("search_engine") and not stack["search"].get("engine"):
            stack["search"]["engine"] = adr["search_engine"]
            result.sources["stack.search.engine"] = nm
        if adr.get("messaging_engine") and not stack["messaging"].get("enabled"):
            stack["messaging"]["enabled"] = True
            stack["messaging"]["engine"] = adr["messaging_engine"]
            result.sources["stack.messaging.enabled"] = nm

    # Drop empty stack subsections.
    stack_clean = {k: v for k, v in stack.items() if v}
    if stack_clean:
        ctx["stack"] = stack_clean

    # multiTenancy.* — D-076: mode and term decoupled. Resolution order:
    #   - mode: LBC classification (SaaS B2B → multi-tenant) wins; otherwise
    #           ADR-003 'empresa' hint suggests multi-empresa.
    #   - term: ADR-003 hint (e.g. 'empresa') always wins when present —
    #           independent of mode. This lets BOSQ Lean OS be
    #           mode=multi-tenant + term=empresa.
    mt: dict[str, Any] = {}
    adr_term_hint: str | None = None
    for adr in adr_outs:
        if "multi_tenancy_isolation" in adr:
            mt["isolationStrategy"] = adr["multi_tenancy_isolation"]
            result.sources["multiTenancy.isolationStrategy"] = \
                f"architecture/adr/{Path(adr['_path']).name}"
        if "multi_tenancy_term_hint" in adr and adr_term_hint is None:
            adr_term_hint = adr["multi_tenancy_term_hint"]
            result.sources["multiTenancy.term"] = \
                f"architecture/adr/{Path(adr['_path']).name}"

    # Mode resolution: LBC classification > ADR term hint > default.
    lbc_mode = lbc_out.get("mt_mode_hint")
    if lbc_mode:
        mt["mode"] = lbc_mode
        result.sources["multiTenancy.mode"] = "business/lean-business-case.md"
    elif adr_term_hint:
        # ADR-003 mentions 'empresa' but LBC doesn't classify as SaaS → fall
        # back to multi-empresa (internal group model).
        mt["mode"] = "multi-empresa"
        result.sources["multiTenancy.mode"] = "architecture/adr/(term hint)"

    # Term: independent of mode. Set if ADR provides it.
    if adr_term_hint:
        mt["term"] = adr_term_hint
        # Naïve plural: most pt-BR + en-US terms end in -a or consonant — just
        # add 's'. User overrides via project-context when irregular.
        mt["termPlural"] = adr_term_hint + "s"

    if mt:
        ctx["multiTenancy"] = mt

    # ai.*
    if any(adr.get("has_ai_service") for adr in adr_outs):
        ctx["ai"] = {"hasAi": True}
        result.sources["ai.hasAi"] = "architecture/adr/(IA service ADR)"

    # Project-level extensions (non-schema today).
    extensions: dict[str, Any] = {}
    if cs_out.get("compliance"):
        extensions["compliance"] = cs_out["compliance"]
        result.sources["_extensions.compliance"] = "business/constraints.md"
    if wf_out.get("wireframe_metadata"):
        extensions["wireframe"] = wf_out["wireframe_metadata"]
        result.sources["_extensions.wireframe"] = "design/wireframe.md"
    if tf_out.get("module_candidates"):
        extensions["module_candidates"] = tf_out["module_candidates"]
        result.sources["_extensions.module_candidates"] = \
            "business/technical-framing.md"
    if glossary_out.get("domain_vocabulary"):
        extensions["domain_vocabulary"] = glossary_out["domain_vocabulary"]
        result.sources["_extensions.domain_vocabulary"] = "business/glossary.md"
    if st_out.get("stakeholder_roles"):
        extensions["stakeholder_roles"] = st_out["stakeholder_roles"]
        result.sources["_extensions.stakeholder_roles"] = "business/stakeholders.md"
    if personas_out.get("lbc_personas"):
        extensions["lbc_personas"] = personas_out["lbc_personas"]
        result.sources["_extensions.lbc_personas"] = "business/lean-business-case.md"
    # Frontend-reference folder (tokens + screens HTML/CSS) — input for the
    # fe-prototype-analyzer (D-289..D-292). Surface it instead of ignoring it.
    fr_dir = discovery_root / "design" / "frontend-reference"
    if fr_dir.is_dir():
        extensions["frontend_reference"] = {
            "path": str(fr_dir),
            "screen_count": len(sorted(fr_dir.glob("*-screen-*.html"))),
            "has_tokens": (fr_dir / "00-tokens.css").is_file(),
            "css_files": len(list(fr_dir.glob("*.css"))),
        }
        result.sources["_extensions.frontend_reference"] = "design/frontend-reference/"
    if extensions:
        ctx["_extensions"] = extensions

    # ── Handoff §7.1 executable values (highest precedence — human-curated) ──
    if hf_out:
        proj = ctx.setdefault("project", {})
        for k in ("codeName", "segment", "rigorLevel", "issuePrefix"):
            if hf_out.get(k):
                proj[k] = hf_out[k]
                result.sources[f"project.{k}"] = "handoff-package.md"
        stk = ctx.setdefault("stack", {})
        if hf_out.get("packageBase"):
            stk.setdefault("backend", {})["packageBase"] = hf_out["packageBase"]
            result.sources["stack.backend.packageBase"] = "handoff-package.md"
        if hf_out.get("npmScope"):
            fe = stk.setdefault("frontend", {})
            fe["npmScope"] = hf_out["npmScope"]
            fe.setdefault("enabled", True)
            result.sources["stack.frontend.npmScope"] = "handoff-package.md"
        if hf_out.get("database"):
            stk.setdefault("database", {})["engine"] = hf_out["database"]
            result.sources["stack.database.engine"] = "handoff-package.md"
        if hf_out.get("searchEngine"):
            stk.setdefault("search", {})["engine"] = hf_out["searchEngine"]
            result.sources["stack.search.engine"] = "handoff-package.md"
        if hf_out.get("messaging"):
            ms = stk.setdefault("messaging", {})
            ms["enabled"] = True
            ms["engine"] = hf_out["messaging"]
            result.sources["stack.messaging.enabled"] = "handoff-package.md"
        if hf_out.get("ai"):
            ai = ctx.setdefault("ai", {})
            ai["hasAi"] = True
            ai["service"] = hf_out["ai"]
            result.sources["ai.hasAi"] = "handoff-package.md"
        if hf_out.get("mt_mode"):
            mt_ctx = ctx.setdefault("multiTenancy", {})
            raw_mode = hf_out["mt_mode"].strip()
            canonical_modes = {"multi-empresa", "multi-tenant", "single"}
            if raw_mode in canonical_modes:
                mt_ctx["mode"] = raw_mode
                result.sources["multiTenancy.mode"] = "handoff-package.md"
            else:
                # D-293: the handoff authored a non-canonical mode that
                # conflates the isolation strategy with the tenant term
                # (e.g. 'schema-per-empresa'). Decouple it per D-076: derive
                # isolationStrategy + term from the value, and resolve the real
                # mode from the LBC classification hint (multi-tenant for SaaS
                # B2B). The canonical modes are {multi-empresa, multi-tenant,
                # single}; an isolation value is NOT a mode and would break P2
                # (multi-empresa.md.j2 selectattr → 'sequence was empty').
                m_iso = re.match(
                    r"^(schema|database|tenant[-_ ]?id)[-_ ]?per[-_ ](\w+)$",
                    raw_mode, re.IGNORECASE)
                if m_iso:
                    strat = re.sub(r"[-_ ]", "", m_iso.group(1).lower())
                    term = m_iso.group(2).lower()
                    iso_map = {"schema": "schema-per-tenant",
                               "database": "database-per-tenant",
                               "tenantid": "tenant-id-column"}
                    mt_ctx.setdefault(
                        "isolationStrategy",
                        iso_map.get(strat, "schema-per-tenant"))
                    mt_ctx.setdefault("term", term)
                    mt_ctx.setdefault("termPlural", term + "s")
                    resolved_mode = lbc_out.get("mt_mode_hint") or (
                        "multi-empresa" if term == "empresa"
                        else "multi-tenant")
                    mt_ctx["mode"] = resolved_mode
                    result.sources["multiTenancy.mode"] = (
                        "handoff-package.md (D-293 normalized: isolation/term "
                        "decoupled, mode from LBC classification)")
                    result.sources.setdefault(
                        "multiTenancy.isolationStrategy",
                        "handoff-package.md (D-293 derived)")
                    result.sources.setdefault(
                        "multiTenancy.term", "handoff-package.md (D-293 derived)")
                # else: unrecognized non-canonical value → leave mode unset so
                # it surfaces as an unresolved question below.
        if hf_out.get("globalSchema"):
            ctx.setdefault("multiTenancy", {})["globalSchema"] = hf_out["globalSchema"]
            result.sources["multiTenancy.globalSchema"] = "handoff-package.md"
        if hf_out.get("modules_registry"):
            ctx["modules"] = {"registry": hf_out["modules_registry"]}
            result.sources["modules.registry"] = "handoff-package.md"
        if hf_out.get("elastic_indices"):   # D-305
            ctx.setdefault("stack", {}).setdefault("elastic", {})["indices"] = hf_out["elastic_indices"]
            result.sources["stack.elastic.indices"] = "handoff-package.md"

    # ── Aspect overrides (D-074) ────────────────────────────────────────────
    result.aspect_overrides = derive_aspect_overrides(
        lbc_personas=personas_out.get("lbc_personas"),
    )

    # ── Unresolved questions ────────────────────────────────────────────────

    unresolved = result.unresolved

    if "name" not in (ctx.get("project") or {}):
        unresolved.append(
            "**project.name** (slug, lowercase) — could not extract from LBC H1. "
            "Set this in `project-context.json` before running P0.")
    if "segment" not in (ctx.get("project") or {}):
        unresolved.append(
            "**project.segment** — not auto-extractable. "
            "Common values: `civil-construction`, `industrial-ops`, `retail`, "
            "`erp-finance`, `saas-generic`. Pick one based on LBC §4 "
            "'Público-Alvo e Personas'.")
    if "rigorLevel" not in (ctx.get("project") or {}):
        unresolved.append(
            "**project.rigorLevel** — `lean`, `medium`, or `complete-bosq`. "
            "Picks docs/architecture/ depth in P2. For a product like this, "
            "`complete-bosq` is the typical choice.")
    if "issuePrefix" not in (ctx.get("project") or {}):
        unresolved.append(
            "**project.issuePrefix** (3-5 upper alpha, e.g. `BOSQ`) — used in "
            "git commit scopes and issue IDs.")
    # codeName drives identifier-safe derivations (no hyphen in Java package).
    _proj = ctx.get("project") or {}
    cn = _codename(_proj.get("codeName") or _proj.get("name", "project"))
    if "packageBase" not in (ctx.get("stack", {}).get("backend") or {}):
        unresolved.append(
            f"**stack.backend.packageBase** — Java root package "
            f"(e.g. `com.{cn}` — note: the kebab-case name is NOT valid, hyphens "
            f"are illegal in Java packages). Generated entities inherit as "
            f"`com.{cn}.<module>`.")
    if "npmScope" not in (ctx.get("stack", {}).get("frontend") or {}):
        if ctx.get("stack", {}).get("frontend", {}).get("enabled"):
            unresolved.append(
                f"**stack.frontend.npmScope** — Nx workspace npm scope "
                f"(e.g. `@{cn}`).")
    if "mode" not in (ctx.get("multiTenancy") or {}):
        unresolved.append(
            "**multiTenancy.mode** — `multi-empresa` (group internal, same "
            "economic group), `multi-tenant` (SaaS B2B with external "
            "clients), or `single`. If the product is SaaS B2B with external "
            "construction companies as clients, `multi-tenant` is more "
            "accurate even when the term `empresa` is used internally.")
    if "globalSchema" not in (ctx.get("multiTenancy") or {}):
        unresolved.append(
            f"**multiTenancy.globalSchema** — Postgres schema name for shared "
            f"catalogues (e.g. `{cn}_global`).")
    if extensions.get("module_candidates") and not (ctx.get("modules") or {}).get("registry"):
        names = ", ".join(c["displayName"] for c in extensions["module_candidates"][:5])
        unresolved.append(
            f"**modules.registry** — candidates extracted from "
            f"technical-framing §4 ({names}, ...). Each needs: 3-5 letter "
            f"prefix (e.g. `LOSS`, `KAIZEN`, `IAM`), displayName, "
            f"description. See _extensions.module_candidates in this "
            f"project-context.json for the full list. (If a handoff §7.1 "
            f"`modules.registry` is provided, this is resolved automatically.)")
    # D-305: surface missing elastic indices when search engine is elasticsearch.
    search_engine = (ctx.get("stack") or {}).get("search", {}).get("engine", "")
    elastic_indices = (ctx.get("stack") or {}).get("elastic", {}).get("indices", [])
    if search_engine.lower() == "elasticsearch" and not elastic_indices:
        unresolved.append(
            "**stack.elastic.indices** — Elasticsearch detected but no index registry "
            "declared. Add `stack.elastic.indices` to the handoff §7.1 YAML block with "
            "one entry per index. Example:\n"
            "  stack.elastic.indices:\n"
            "    - { slug: \"entities\", displayName: \"Entities\", class: \"dimension\", "
            "domainContext: \"MODULE\" }\n"
            "    - { slug: \"events\", displayName: \"Events\", class: \"fact\", "
            "domainContext: \"MODULE\" }\n"
            "Required fields: slug (kebab-case), displayName, class (dimension|fact). "
            "When present, P2 emits index-design-<slug>.md + query-capability-<slug>.md "
            "per index automatically (D-303).")

    result.context = ctx
    return result


def render_unresolved_questions_md(result: IngestionResult,
                                    discovery_root: Path) -> str:
    """Render the human-readable `_inbox/UNRESOLVED_QUESTIONS.md` file."""
    lines: list[str] = []
    lines.append("# Unresolved questions — discovery ingestion (D-073)")
    lines.append("")
    lines.append(f"> Source: `{discovery_root}`")
    lines.append(f"> Generated at: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append("")
    lines.append("The discovery ingestion populated `project-context.json` with the "
                 "fields it could extract confidently. The items below need human "
                 "input before running `/new-project P1`. Edit `project-context.json` "
                 "directly, then proceed.")
    lines.append("")
    lines.append("## Open items")
    lines.append("")
    if not result.unresolved:
        lines.append("_(no unresolved items — every required field was extracted)_")
    else:
        for i, q in enumerate(result.unresolved, 1):
            lines.append(f"{i}. {q}")
            lines.append("")
    lines.append("## Field provenance")
    lines.append("")
    lines.append("Which input file each extracted field came from:")
    lines.append("")
    if not result.sources:
        lines.append("_(no fields extracted)_")
    else:
        for field, source in sorted(result.sources.items()):
            lines.append(f"- `{field}` ← `{source}`")
    lines.append("")
    lines.append("## ADRs preserved")
    lines.append("")
    lines.append(f"{len(result.adr_files)} ADR file(s) copied verbatim to "
                 f"`_inbox/adr/` as discovery history. The framework's own "
                 f"ADR generation produces a parallel set under "
                 f"`docs/architecture/backend/adr/` in P2.")
    lines.append("")
    for p in result.adr_files:
        lines.append(f"- `_inbox/adr/{p.name}`")
    return "\n".join(lines) + "\n"


# ── CLI for standalone smoke testing ─────────────────────────────────────────


def _main(argv: list[str] | None = None) -> int:
    import argparse
    import json

    from cli_utils import force_utf8_stdio
    force_utf8_stdio()

    parser = argparse.ArgumentParser(
        description="Discovery → project-context.json ingestion (D-073)")
    parser.add_argument("--discovery", type=Path, required=True,
                        help="Discovery directory (with business/, "
                             "architecture/adr/, optionally design/)")
    parser.add_argument("--print-context", action="store_true",
                        help="Print the produced context JSON to stdout")
    parser.add_argument("--report", action="store_true",
                        help="Dry-run preview: print the produced context JSON "
                             "followed by unresolved questions + field "
                             "provenance + ADR inventory. Writes nothing. "
                             "Backs the /discovery command (D-288).")
    args = parser.parse_args(argv)

    try:
        result = ingest_discovery(args.discovery)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if args.report:
        # Preview/dry-run: full picture in one shot, no side effects.
        print("=== project-context.json (preview — NOT written) ===")
        print(json.dumps(result.context, indent=2, ensure_ascii=False))
        print()
        print(render_unresolved_questions_md(result, args.discovery.resolve()))
    elif args.print_context:
        print(json.dumps(result.context, indent=2, ensure_ascii=False))
    else:
        print(f"OK: extracted {sum(1 for _ in result.sources)} field(s), "
              f"{len(result.unresolved)} unresolved, "
              f"{len(result.adr_files)} ADR(s)")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
