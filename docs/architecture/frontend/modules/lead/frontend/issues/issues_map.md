# Issues Map — LEAD (Frontend)

> Índice mestre do backlog FE do LEAD. Total: **22 funcionais (FE-LEAD-NNN) + 6 integração
> (INT-FE-LEAD-NNN) = 28 issues**. Cada issue ≤ 1 dia.

## Por prioridade (ondas)

| Onda | Foco | Issues |
|---|---|---|
| **P1** | Foundation (module entry + Shell descriptor) | FE-LEAD-001, 002, 003 |
| **P2** | Data access (services + facades + erros) | FE-LEAD-004, 005, 006, 007, 008 |
| **P3** | Feature libs (pages + components + score UI) | FE-LEAD-009, 010, 011, 012, 013, 014, 015, 016 |
| **P4** | Hub integrations | INT-FE-LEAD-001, 002, 003, 004, 005, 006 |
| **P5** | Access guards | FE-LEAD-017 |
| **P6** | Navigation / breadcrumbs | FE-LEAD-018 |
| **P7** | UX polish (loading/empty/error + flags + a11y) | FE-LEAD-019, 020 |
| **P8** | Observability | FE-LEAD-021 |
| **P9** | e2e + hardening | FE-LEAD-022 |

## Por SPEC de origem

| SPEC | Issues alimentadas |
|---|---|
| SPEC-01 route-map | 002, 010, 017, 018, 020 |
| SPEC-02 component-hierarchy | 009–016 |
| SPEC-03 view-models | 004–008, 009–016 |
| SPEC-04 data-access | 004, 005, 006, 007, 008, INT-001, INT-002 |
| SPEC-05 module-contract | 001, 020, INT-003, INT-004 |
| SPEC-06 shell-integration | 003, INT-005 |
| SPEC-07 error-handling | 008, 019, INT-006 |
| SPEC-08 e2e-scenarios | 022 |
| ADR-005 (Maturity Score viz) | 012, 013, 020 |

## Cobertura dos gaps do Specs-Validate (A2.5)

| Gap | Cláusula EARS | Issue(s) |
|---|---|---|
| G1 lead-not-found | `WHEN open :id non-existent → "lead não encontrado"` | FE-LEAD-019, 022 |
| G2 flag maturity-score | `WHILE flag disabled → omit route/menu` | FE-LEAD-020 |
| G3 flag qualification-rules | `WHILE flag disabled → hide "Regras"` | FE-LEAD-020 |
| G4 radar-a11y | `WHERE score-radar → accessible table` | FE-LEAD-012, 020 |
| G5 profile-refetch | `WHEN profile updated → refetch score` | FE-LEAD-004, 011, 022 |
| G6 list-error | `IF list fails → error signal (no throw)` | FE-LEAD-008, 019 |
| G7 retry-policy | `WHEN 5xx → manual retry, no auto-retry` | FE-LEAD-019 |
| G8 redirect-root | `WHEN navigate /lead → redirect /lead/leads` | FE-LEAD-002, 022 |
| G9 empresa-guard | `IF no empresa context → block routes` | FE-LEAD-017, INT-002, 022 |

## Por camada

| Camada | Issues |
|---|---|
| `libs/lead/shell-entry` | 001, 002, 003, 020, INT-005 |
| `libs/lead/data-access` | 004, 005, 006, 007, 008, 021, INT-001, INT-002, INT-006 |
| `libs/lead/feature-lead-list` | 009, 010 |
| `libs/lead/feature-lead-detail` | 011, 019 |
| `libs/lead/feature-maturity-score` | 013 |
| `libs/lead/feature-segmentation` | 014 |
| `libs/lead/feature-survey` | 015 |
| `libs/lead/feature-qualification-rules` | 016 |
| `libs/lead/ui` | 009, 012, 013, 020 |
| `libs/lead/access` | 017, INT-003 |
| `libs/lead/navigation` | 018, INT-003 |
| `libs/lead/integration` | INT-005 |
| `libs/lead/styles` | 019 |
| Access Layer wiring | INT-001, INT-002, INT-003, INT-004, INT-006 |
| `apps/journey-os-web` (Shell) | 003 |
| `apps/lead-e2e` | 022 |
| Observability | 021 |

## Caminho crítico (mais longo)

```
FE-LEAD-001 (contract)
  → FE-LEAD-002 (routes/entry)
    → INT-FE-LEAD-001 (http-base)
      → FE-LEAD-004 (lead data-access + facades)
        → FE-LEAD-008 (error mapping)
          → FE-LEAD-011 (detail page + ações)
            → FE-LEAD-012 (score breakdown/radar — ADR-005)
              → FE-LEAD-019 (UX polish)
                → FE-LEAD-020 (flags + a11y)
                  → FE-LEAD-022 (e2e + hardening)
```

Ramos paralelos (após P2): fila (009→010), maturity dashboard (013), segmentação (007→014),
surveys (005→015), regras (006→016).

## Estimativas agregadas (S/M/L)

| Tamanho | Issues | Qtd |
|---|---|---|
| S | 001, 003, 017, 018, 021, INT-001, INT-002, INT-003, INT-006 | 9 |
| M | 002, 005, 006, 007, 008, 009, 010, 014, 015, 016, 019, 021*, INT-004, INT-005 | 13 |
| L | 004, 011, 012, 013, 020, 022 | 6 |

Total estimado: ~32 dias-pessoa (sequencial); fortemente paralelizável após P2 (fila / detalhe+score /
maturity / segmentação / surveys / regras em trilhas independentes).
