# Issues Map — SALE (Frontend)

> Índice mestre do backlog FE do SALE (Sales & Revenue). Total: **23 funcionais (FE-SALE-NNN) + 6
> integração (INT-FE-SALE-NNN) = 29 issues**. Cada issue ≤ 1 dia. Módulo de domínio núcleo;
> centerpiece = Kanban de pipeline com optimistic move + rollback (ADR-005).

## Por prioridade (ondas)

| Onda | Foco | Issues |
|---|---|---|
| **P1** | Foundation (module entry + Shell descriptor + integration/bootstrap) | FE-SALE-001, 002, 003, 004 |
| **P2** | Data access (services + facades + erros) | FE-SALE-005, 006, 007, 008, 009 |
| **P3** | Feature libs (6 features + ui local + flag multi-touch) | FE-SALE-010, 011, 012, 013, 014, 015, 016, 017 |
| **P4** | Hub integrations | INT-FE-SALE-001, 002, 003, 004, 005, 006 |
| **P5** | Access guards | FE-SALE-018 |
| **P6** | Navigation / breadcrumbs | FE-SALE-019 |
| **P7** | UX polish (loading/empty/error + rollback UX + flag) + a11y/perf | FE-SALE-020, 021 |
| **P8** | Observability | FE-SALE-022 |
| **P9** | e2e + hardening | FE-SALE-023 |

## Por SPEC de origem

| SPEC | Issues alimentadas |
|---|---|
| SPEC-01 route-map | 002, 018, 019, 020, 023 |
| SPEC-02 component-hierarchy | 010–016, 021 |
| SPEC-03 view-models | 005–008, 010–016 |
| SPEC-04 data-access | 005, 006, 007, 008, 009, INT-001, INT-002 |
| SPEC-05 module-contract | 001, 017, 020, INT-003, INT-004 |
| SPEC-06 shell-integration | 003, 004, 019, INT-003 |
| SPEC-07 error-handling | 009, 020, 022, INT-005, INT-006 |
| SPEC-08 e2e-scenarios | 023 |
| ADR-005 (kanban-pipeline-rendering) | 010, 016, 020, 021, 023 |

## Cobertura dos gaps do cross-link (G1–G4)

| Gap | Item | Issue(s) |
|---|---|---|
| G1 | Endpoint funil de receita (`/receita/funil` proposto) | FE-SALE-008 (degrada), FE-SALE-015 (flag + LTV-apenas) |
| G2 | Título legível do card (`OpportunityCardVm.titulo`) | FE-SALE-005, FE-SALE-016 (fallback id) |
| G3 | Nome do responsável (`responsavelNome`) | FE-SALE-005, FE-SALE-016 (fallback id) |
| G4 | Multi-touch atrás de flag (`sale.attribution-multitouch`) | FE-SALE-001, FE-SALE-017 |

## Por camada

| Camada | Issues |
|---|---|
| `libs/sale/shell-entry` | 001, 002, 003, 017, 020 |
| `libs/sale/integration` | 004, INT-003 |
| `libs/sale/data-access` | 005, 006, 007, 008, 009, 022, INT-001, INT-002, INT-005, INT-006 |
| `libs/sale/feature-pipeline` | 010, 020, 021, 022 |
| `libs/sale/feature-opportunity` | 011, 022 |
| `libs/sale/feature-offer` | 012 |
| `libs/sale/feature-purchase` | 013, 022 |
| `libs/sale/feature-attribution` | 014, 017 |
| `libs/sale/feature-revenue-dashboard` | 015 |
| `libs/sale/ui` | 016, 021 |
| `libs/sale/access` | 018, INT-004 |
| `libs/sale/navigation` | 019, INT-004 |
| `libs/sale/styles` | 020 |
| `apps/journey-os-web` (Shell) | 003 |
| `apps/sale-e2e` | 023 |

## Caminho crítico (mais longo)

```
FE-SALE-001 (contract)
  → FE-SALE-002 (routes/entry)
    → INT-FE-SALE-001 (http-base + JWT)
      → FE-SALE-005 (oportunidade data-access + snapshot)
        → FE-SALE-010 (Kanban DnD + optimistic + rollback — ADR-005)
          → FE-SALE-020 (UX polish + rollback UX)
            → FE-SALE-021 (a11y DnD + virtual scroll)
              → FE-SALE-022 (observability)
                → FE-SALE-023 (e2e + hardening)
```

Ramos paralelos (após P2): oferta (006→012), compra (007→013), atribuição+ltv (008→014/015),
ui local (016), guards (018), navegação (019). FE-SALE-016 (ui) deve preceder as features P3.

## Estimativas agregadas (S/M/L)

| Tamanho | Issues | Qtd |
|---|---|---|
| S | 001, 003, 009, 017, 019, INT-001, INT-002, INT-003, INT-005, INT-006 | 10 |
| M | 002, 004, 006, 007, 008, 011, 012, 015, 016, 018, 022, INT-004 | 12 |
| L | 005, 010, 013, 014, 020, 021, 023 | 7 |

Total estimado: ~33 dias-pessoa (sequencial); paralelizável após P2 (oferta / compra / atribuição /
dashboard / ui / guards em trilhas independentes). Caminho crítico = Kanban (010) → rollback UX (020) →
a11y/perf (021) → e2e (023).
