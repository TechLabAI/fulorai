# Issues Map — COMM (Frontend)

> Índice mestre do backlog FE do COMM. Total: **20 funcionais (FE-COMM-NNN) + 6 integração
> (INT-FE-COMM-NNN) = 26 issues**. Cada issue ≤ 1 dia.

## Por prioridade (ondas)

| Onda | Foco | Issues |
|---|---|---|
| **P1** | Foundation (module entry + Shell descriptor) | FE-COMM-001, 002, 003 |
| **P2** | Data access (services + facades + erros) | FE-COMM-004, 005, 006, 007, 008 |
| **P3** | Feature libs (pages + components) | FE-COMM-009, 010, 011, 012, 013, 014, 015 |
| **P4** | Hub integrations | INT-FE-COMM-001, 002, 003, 004, 005, 006 |
| **P5** | Access guards | FE-COMM-016 |
| **P6** | Navigation / breadcrumbs | FE-COMM-017 |
| **P7** | UX polish (loading/empty/error + tokens) | FE-COMM-018 |
| **P8** | Observability | FE-COMM-019 |
| **P9** | e2e + hardening | FE-COMM-020 |

## Por SPEC de origem

| SPEC | Issues alimentadas |
|---|---|
| SPEC-01 route-map | 002, 016, 017 |
| SPEC-02 component-hierarchy | 009–015 |
| SPEC-03 view-models | 004–008, 010–015 |
| SPEC-04 data-access | 004, 005, 006, 007, 008, INT-001 |
| SPEC-05 module-contract | 001, 017, INT-004 |
| SPEC-06 shell-integration | 003, INT-005 |
| SPEC-07 error-handling | 008, 018, INT-006 |
| SPEC-08 e2e-scenarios | 020 |
| ADR-005 (delivery tracking / polling) | 007, 014 |

## Por camada

| Camada | Issues |
|---|---|
| `libs/comm/shell-entry` | 001, 002, 003, INT-004, INT-005 |
| `libs/comm/data-access` | 004, 005, 006, 007, 008, 019, INT-001, INT-006 |
| `libs/comm/feature-template-catalog` | 009, 010 |
| `libs/comm/feature-template-studio` | 011 |
| `libs/comm/feature-routing-rules` | 012 |
| `libs/comm/feature-messages` | 013, 014 |
| `libs/comm/feature-channel-config` | 015 |
| `libs/comm/ui` | 009, 014, 018 |
| `libs/comm/access` | 016, INT-002, INT-003 |
| `libs/comm/navigation` | 017, INT-004 |
| `libs/comm/integration` | INT-005 |
| `libs/comm/styles` | 018 |
| Access Layer wiring | INT-001, INT-002, INT-003, INT-004, INT-006 |
| `apps/journey-os-web` (Shell) | 003 |
| `apps/comm-e2e` | 020 |
| Observability | 019 |

## Caminho crítico (mais longo)

```
FE-COMM-001 (contract)
  → FE-COMM-002 (routes/lazy)
    → INT-FE-COMM-001 (http-base)
      → FE-COMM-007 (message data-access + polling)
        → FE-COMM-013 (messages list + dispatch)
          → FE-COMM-014 (detail + timeline/polling)
            → FE-COMM-018 (UX polish)
              → FE-COMM-020 (e2e + hardening)
```

Ramos paralelos (após P2):
- Templates: FE-COMM-004 → 009 → 010 → (Studio) 005 → 011
- Roteamento: FE-COMM-006 → 012
- Canais: FE-COMM-008 → 015

## Cobertura dos gaps do specs-validate (A2.5)

| Gap | Issue(s) |
|---|---|
| C-05.4 (delivery-tracking flag off → refresh manual) | FE-COMM-014, FE-COMM-020 |
| C-06.4 (parar polling no destroy/navigate-away) | FE-COMM-007, FE-COMM-014, INT-FE-COMM-005, FE-COMM-020 |

## Estimativas agregadas (S/M/L)

| Tamanho | Issues | Qtd |
|---|---|---|
| S | 001, 003, 016, 017, 019, INT-001, INT-002, INT-004, INT-006 | 9 |
| M | 002, 004, 005, 006, 008, 009, 012, 015, 018, INT-003, INT-005 | 11 |
| L | 007, 010, 011, 013, 014, 020 | 6 |

Total estimado: ~30 dias-pessoa (sequencial); paralelizável após P2 (templates / studio / roteamento /
mensagens / canais em trilhas independentes).
