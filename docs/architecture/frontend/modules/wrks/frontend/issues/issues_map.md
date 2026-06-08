# Issues Map — WRKS (Frontend)

> Índice mestre do backlog FE do WRKS. Total: **20 funcionais (FE-WRKS-NNN) + 6 integração
> (INT-FE-WRKS-NNN) = 26 issues**. Cada issue ≤ 1 dia.

## Por prioridade (ondas)

| Onda | Foco | Issues |
|---|---|---|
| **P1** | Foundation (module entry + Shell descriptor) | FE-WRKS-001, 002, 003 |
| **P2** | Data access (services + facades + erros) | FE-WRKS-004, 005, 006, 007, 008 |
| **P3** | Feature libs (pages + components) | FE-WRKS-009, 010, 011, 012, 013, 014, 015 |
| **P4** | Hub integrations | INT-FE-WRKS-001, 002, 003, 004, 005, 006 |
| **P5** | Access guards | FE-WRKS-016 |
| **P6** | Navigation / breadcrumbs | FE-WRKS-017 |
| **P7** | UX polish (loading/empty/error) | FE-WRKS-018 |
| **P8** | Observability | FE-WRKS-019 |
| **P9** | e2e + hardening | FE-WRKS-020 |

## Por SPEC de origem

| SPEC | Issues alimentadas |
|---|---|
| SPEC-01 route-map | 002, 016, 017 |
| SPEC-02 component-hierarchy | 009–015 |
| SPEC-03 view-models | 004–007, 011–015 |
| SPEC-04 data-access | 004, 005, 006, 007, 008, INT-004 |
| SPEC-05 module-contract | 001, INT-003 |
| SPEC-06 shell-integration | 003, INT-005 |
| SPEC-07 error-handling | 008, 018, INT-006 |
| SPEC-08 e2e-scenarios | 020 |

## Por camada

| Camada | Issues |
|---|---|
| `apps/wrks` <module>-module | 001, 002, 003, INT-005 |
| `libs/wrks/data-access` | 004, 005, 006, 007, 008, INT-002, INT-004 |
| `libs/wrks/feature-*` | 009–015, 018 |
| `libs/wrks/access` | 016 |
| `libs/wrks/navigation` | 017 |
| `libs/wrks/integration` | INT-005 |
| Access Layer wiring | INT-001, INT-002, INT-003, INT-004, INT-006 |
| `apps/wrks-e2e` | 020 |
| Observability | 019 |

## Caminho crítico (mais longo)

```
FE-WRKS-001 (contract)
  → FE-WRKS-002 (routes/module)
    → INT-FE-WRKS-004 (http-base)
      → FE-WRKS-005 (users data-access)
        → FE-WRKS-008 (error mapping)
          → FE-WRKS-013 (users list+invite)
            → FE-WRKS-014 (role editor)
              → INT-FE-WRKS-003 (access-decision)
                → FE-WRKS-016 (guards)
                  → FE-WRKS-018 (UX polish)
                    → FE-WRKS-020 (e2e + hardening)
```

## Estimativas agregadas (S/M/L)

| Tamanho | Issues | Qtd |
|---|---|---|
| S | 001, 003, 006, 007, 015, 016, 017, 019, INT-001, INT-004, INT-006 | 11 |
| M | 002, 004, 005, 008, 009, 010, 011, 012, 018, INT-002, INT-003, INT-005 | 12 |
| L | 013, 014, 020 | 3 |

Total estimado: ~26 dias-pessoa (sequencial); paralelizável após P2.
