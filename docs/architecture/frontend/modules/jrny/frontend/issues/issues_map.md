# Issues Map — JRNY (Frontend)

> Índice mestre do backlog FE do JRNY. Total: **22 funcionais (FE-JRNY-NNN) + 6 integração
> (INT-FE-JRNY-NNN) = 28 issues**. Cada issue ≤ 1 dia. Módulo orquestrador (o mais complexo).

## Por prioridade (ondas)

| Onda | Foco | Issues |
|---|---|---|
| **P1** | Foundation (module entry + Shell descriptor) | FE-JRNY-001, 002, 003 |
| **P2** | Data access (services + facades + erros) | FE-JRNY-004, 005, 006, 007, 008 |
| **P3** | Feature libs (pages + components + ui) | FE-JRNY-009, 010, 011, 012, 013, 014, 015, 016 |
| **P4** | Hub integrations | INT-FE-JRNY-001, 002, 003, 004, 005, 006 |
| **P5** | Access guards | FE-JRNY-017 |
| **P6** | Navigation / breadcrumbs | FE-JRNY-018 |
| **P7** | UX polish (loading/empty/error + flags + a11y) | FE-JRNY-019, 020 |
| **P8** | Observability | FE-JRNY-021 |
| **P9** | e2e + hardening | FE-JRNY-022 |

## Por SPEC de origem

| SPEC | Issues alimentadas |
|---|---|
| SPEC-01 route-map | 002, 017, 018, 019, 022 |
| SPEC-02 component-hierarchy | 009–016 |
| SPEC-03 view-models | 004–007, 009–016 |
| SPEC-04 data-access | 004, 005, 006, 007, 008, INT-001, INT-002 |
| SPEC-05 module-contract | 001, 020, INT-003, INT-005 |
| SPEC-06 shell-integration | 003, INT-005 |
| SPEC-07 error-handling | 008, 019, INT-006 |
| SPEC-08 e2e-scenarios | 022 |
| ADR-005 (canvas-builder-rendering) | 010, 014, 015, 016, 020 |

## Cobertura dos gaps do Specs-Validate (A2.5) + cross-link

| Gap | Cláusula / origem | Issue(s) |
|---|---|---|
| G-a empresaGuard sem-empresa | `IF no empresa context → block /jrny` | FE-JRNY-017, INT-FE-JRNY-002, 022 |
| G-b condicaoResumo render | `THE SYSTEM SHALL render condicaoResumo` | FE-JRNY-012, 020 |
| G-c canvas-flag-enabled | `WHERE canvas enabled → lazy; else structured` | FE-JRNY-020 (pós-MVP) |
| G-d reorder-failure rollback | `IF reorder PATCH fails → rollback + toast` | FE-JRNY-016 |
| G-e read-failure retry | `IF read fails → error state + retry manual` | FE-JRNY-008, 019 |
| G1 analytics endpoint (cross-link) | endpoint funil proposto | FE-JRNY-014 (flag + degrada) |
| G2 asset label (cross-link) | `assetRefId → label` | FE-JRNY-011 |
| G3 temRegrasSaindo (cross-link) | derivar client-side | FE-JRNY-005, 010 |
| G4 reorder batch (cross-link) | sem endpoint batch | FE-JRNY-016 |

## Por camada

| Camada | Issues |
|---|---|
| `libs/jrny/shell-entry` | 001, 002, 020, INT-005 |
| `libs/jrny/data-access` | 004, 005, 006, 007, 008, 021, INT-001, INT-002, INT-006 |
| `libs/jrny/feature-journey-list` | 009 |
| `libs/jrny/feature-journey-builder` | 010, 016 |
| `libs/jrny/feature-stage-editor` | 011 |
| `libs/jrny/feature-routing-engine` | 012, 020 |
| `libs/jrny/feature-decision-log` | 013 |
| `libs/jrny/feature-journey-analytics` | 014 |
| `libs/jrny/ui` | 015, 020 |
| `libs/jrny/access` | 017, INT-003, INT-004 |
| `libs/jrny/navigation` | 018, INT-003 |
| `libs/jrny/integration` | INT-005 |
| `libs/jrny/styles` | 019 |
| Access Layer wiring | INT-001, INT-002, INT-003, INT-004, INT-006 |
| `apps/journey-os-web` (Shell) | 003 |
| `apps/jrny-e2e` | 022 |
| Observability | 021 |

## Caminho crítico (mais longo)

```
FE-JRNY-001 (contract)
  → FE-JRNY-002 (routes/entry)
    → INT-FE-JRNY-001 (http-base)
      → FE-JRNY-004 (journey data-access + facades)
        → FE-JRNY-005 (stage data-access)
          → FE-JRNY-010 (builder + máquina de estados)
            → FE-JRNY-016 (sortable a11y + rollback — ADR-005)
              → FE-JRNY-019 (UX polish)
                → FE-JRNY-020 (flags + a11y)
                  → FE-JRNY-022 (e2e + hardening)
```

Ramos paralelos (após P2): lista (009), stage-editor (011), regras (006→012),
decision-log (007→013), analytics (014), ui (015).

## Estimativas agregadas (S/M/L)

| Tamanho | Issues | Qtd |
|---|---|---|
| S | 001, 003, 018, 021, INT-001, INT-002, INT-003, INT-004, INT-006 | 9 |
| M | 002, 006, 007, 008, 009, 011, 014, 015, 017, 019, INT-005 | 11 |
| L | 004, 005, 010, 012, 013, 016, 020, 022 | 8 |

Total estimado: ~34 dias-pessoa (sequencial); paralelizável após P2 (builder+stage / regras /
decision-log / analytics em trilhas independentes). Caminho crítico = builder + sortable + polish.
