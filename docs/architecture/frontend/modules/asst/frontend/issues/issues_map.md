# Issues Map — ASST (Frontend)

> Índice mestre do backlog FE do ASST. Total: **20 funcionais (FE-ASST-NNN) + 6 integração
> (INT-FE-ASST-NNN) = 26 issues**. Cada issue ≤ 1 dia.

## Por prioridade (ondas)

| Onda | Foco | Issues |
|---|---|---|
| **P1** | Foundation (module entry + Shell descriptor) | FE-ASST-001, 002, 003 |
| **P2** | Data access (services + facades + erros) | FE-ASST-004, 005, 006, 007, 008 |
| **P3** | Feature libs (pages + components) | FE-ASST-009, 010, 011, 012, 013, 014, 015 |
| **P4** | Hub integrations | INT-FE-ASST-001, 002, 003, 004, 005, 006 |
| **P5** | Access guards | FE-ASST-016 |
| **P6** | Navigation / breadcrumbs | FE-ASST-017 |
| **P7** | UX polish (loading/empty/error) | FE-ASST-018 |
| **P8** | Observability | FE-ASST-019 |
| **P9** | e2e + hardening | FE-ASST-020 |

## Por SPEC de origem

| SPEC | Issues alimentadas |
|---|---|
| SPEC-01 route-map | 002, 016, 017 |
| SPEC-02 component-hierarchy | 009–015 |
| SPEC-03 view-models | 004–008, 010–015 |
| SPEC-04 data-access | 004, 005, 006, 007, 008, INT-001 |
| SPEC-05 module-contract | 001, INT-004 |
| SPEC-06 shell-integration | 003, INT-005 |
| SPEC-07 error-handling | 008, 018, INT-006 |
| SPEC-08 e2e-scenarios | 020 |
| ADR-005 (Asset Studio) | 006, 013 |

## Por camada

| Camada | Issues |
|---|---|
| `libs/asst/shell-entry` | 001, 002, 003, INT-005 |
| `libs/asst/data-access` | 004, 005, 006, 007, 008, 019, INT-001, INT-002, INT-003, INT-006 |
| `libs/asst/feature-asset-library` | 009, 010 |
| `libs/asst/feature-asset-detail` | 011, 012 |
| `libs/asst/feature-asset-studio` | 013 |
| `libs/asst/feature-approval-workflow` | 014, 015 |
| `libs/asst/ui` | 009, 010, 012 |
| `libs/asst/access` | 016, INT-002 |
| `libs/asst/navigation` | 017 |
| `libs/asst/integration` | INT-005 |
| `libs/asst/styles` | 018 |
| Access Layer wiring | INT-001, INT-002, INT-003, INT-004, INT-006 |
| `apps/journey-os-web` (Shell) | 003 |
| `apps/asst-e2e` | 020 |
| Observability | 019 |

## Caminho crítico (mais longo)

```
FE-ASST-001 (contract)
  → FE-ASST-002 (routes/module)
    → INT-FE-ASST-001 (http-base)
      → FE-ASST-004 (catalog data-access)
        → FE-ASST-005 (versões data-access)
          → FE-ASST-007 (workflow data-access)
            → FE-ASST-011 (detail page + ações)
              → FE-ASST-012 (versões timeline + nova versão)
                → FE-ASST-015 (decisão + publish)
                  → FE-ASST-018 (UX polish)
                    → FE-ASST-020 (e2e + hardening)
```

Ramo paralelo (Studio): FE-ASST-006 → FE-ASST-013 (depende de FE-ASST-012).

## Estimativas agregadas (S/M/L)

| Tamanho | Issues | Qtd |
|---|---|---|
| S | 001, 003, 016, 017, 019, INT-001, INT-002, INT-006 | 8 |
| M | 002, 004, 005, 006, 007, 008, 009, 010, 014, 018, INT-003, INT-004, INT-005 | 13 |
| L | 011, 012, 013, 015, 020 | 5 |

Total estimado: ~30 dias-pessoa (sequencial); paralelizável após P2 (catálogo / studio / aprovação
em trilhas independentes).
