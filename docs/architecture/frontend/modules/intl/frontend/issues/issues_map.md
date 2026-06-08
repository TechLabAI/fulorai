# Issues Map — INTL (Frontend)

> Índice mestre do backlog FE do INTL. Total: **20 funcionais (FE-INTL-NNN) + 6 integração
> (INT-FE-INTL-NNN) = 26 issues**. Cada issue ≤ 1 dia.

## Por prioridade (ondas)

| Onda | Foco | Issues |
|---|---|---|
| **P1** | Foundation (module entry + Shell descriptor) | FE-INTL-001, 002, 003 |
| **P2** | Data access (services + facades + erros) | FE-INTL-004, 005, 006, 007, 008 |
| **P3** | Feature libs (pages + components) | FE-INTL-009, 010, 011, 012, 013, 014 |
| **P4** | Hub integrations | INT-FE-INTL-001, 002, 003, 004, 005, 006 |
| **P5** | Access guards | FE-INTL-015 |
| **P6** | Navigation / breadcrumbs | FE-INTL-016 |
| **P7** | UX polish (loading/empty/error) | FE-INTL-017 |
| **P8** | Observability | FE-INTL-018 |
| **P9** | e2e + hardening | FE-INTL-019, 020 |

## Por SPEC de origem

| SPEC | Issues alimentadas |
|---|---|
| SPEC-01 route-map | 002, 015, 016 |
| SPEC-02 component-hierarchy | 009–014 |
| SPEC-03 view-models | 005, 006, 007, 009–014 |
| SPEC-04 data-access | 004, 005, 006, 007, 008, INT-004 |
| SPEC-05 module-contract | 001, INT-003 |
| SPEC-06 shell-integration | 003, INT-005 |
| SPEC-07 error-handling | 008, 017, INT-006 |
| SPEC-08 e2e-scenarios | 019 |

## Por camada

| Camada | Issues |
|---|---|
| `libs/intl/shell-entry` (module entry) | 001, 002, 003*, INT-005 |
| `libs/intl/data-access` | 004, 005, 006, 007, 008, 018, 020, INT-001, INT-002, INT-004, INT-006 |
| `libs/intl/feature-copilot` | 009, 010, 011 |
| `libs/intl/feature-knowledge` | 012, 013 |
| `libs/intl/feature-analytics` | 014 |
| `libs/intl/ui` | 011, 014 |
| `libs/intl/access` | 015, INT-003 |
| `libs/intl/navigation` | 016, INT-003 |
| `libs/intl/integration` | 003, INT-005 |
| `apps/journey-os-web` (Shell) | 003 |
| `apps/intl-e2e` | 019 |
| Observability | 018 |

## Caminho crítico (mais longo)

```
FE-INTL-001 (contract)
  → FE-INTL-002 (routes/entry)
    → INT-FE-INTL-004 (http-base)
      → FE-INTL-004 (copilot api)
        → FE-INTL-005 (copilot facade: otimismo/cancelamento)
          → FE-INTL-010 (conversation page)
            → FE-INTL-011 (badges + citations — fundamentação visual)
              → FE-INTL-017 (UX polish)
                → FE-INTL-020 (hardening: reset + status defensivo)
                  → FE-INTL-019 (e2e + a11y)
```

## Estimativas agregadas (S/M/L)

| Tamanho | Issues | Qtd |
|---|---|---|
| S | 001, 002, 007, 016, 018, INT-001, INT-002, INT-003, INT-004, INT-006 | 10 |
| M | 003, 004, 006, 008, 009, 012, 014, 015, 017, 020, INT-005 | 11 |
| L | 005, 010, 011, 013, 019 | 5 |

Total estimado: ~26 dias-pessoa (sequencial); paralelizável após P2 (features independentes:
copilot ∥ knowledge ∥ analytics).

> **Nota de escopo:** `feature-event-platform` e `feature-integrations` (citadas no rascunho do
> master plan) ficam **fora do MVP FE** — governança Elastic e Integration Hub não têm UI de
> domínio no MVP (ver `_brief.md` §5 e `01-architectural-vision.md` §5).
