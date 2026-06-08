# Plano de Execução — FE-WRKS (Workspace & Identity · Frontend)

> Plano de ondas P1–P9 do MVP FE do WRKS. Âncora: `_brief.md` (módulo de fundação FE — login,
> seleção de empresa, administração de workspace/usuários/RBAC, multi-empresa sem reload).

## Resumo

O WRKS FE é a **fundação de identidade** do Journey OS: entrega login OIDC, seleção/troca de
empresa (sem reload), e a administração de workspace, usuários e papéis — tudo derivado da Access
Layer (`@journeyos/shared/access-*`), sem que a UI decida RBAC localmente. É precondição de toda
outra tela da plataforma. O backlog (26 issues) cobre module entry, data-access sobre `/api/v1/iam`,
5 features, integrações com a Access Layer/Shell, guards, navegação, polish, observability e e2e.

## Mapa P1–P9

| Onda | Entregável | Issues | Estimativa |
|---|---|---|---|
| P1 | Module entry + registro no Shell | FE-WRKS-001..003 | ~2 d |
| P2 | Data-access (5 resources) + erros | FE-WRKS-004..008 | ~5 d |
| P3 | Features (login, empresa-select, workspace, users, rbac) | FE-WRKS-009..015 | ~9 d |
| P4 | Integrações Access Layer + Shell | INT-FE-WRKS-001..006 | ~5 d |
| P5 | Guards (empresa/access) | FE-WRKS-016 | ~1 d |
| P6 | Navegação/breadcrumbs | FE-WRKS-017 | ~1 d |
| P7 | UX polish (states) | FE-WRKS-018 | ~1 d |
| P8 | Observability | FE-WRKS-019 | ~1 d |
| P9 | e2e Playwright + hardening | FE-WRKS-020 | ~2 d |

> P4 corre em paralelo com P3 (integrações habilitam as features). P5–P8 são incrementos sobre o MVP.

## Caminho crítico

`001 → 002 → INT-004 → 005 → 008 → 013 → 014 → INT-003 → 016 → 018 → 020`
(contrato → rotas → http-base → users data-access → erros → lista/convite → editor papel →
access-decision → guards → polish → e2e).

## Riscos top-3 (de 06-risks)

1. **R-2 Vazamento cross-empresa** (crítico/LGPD) — mitigado por ADR-005 (cancelamento + invalidação
   na troca) e e2e `empresa-switch-isolation.feature` (INT-FE-WRKS-002, FE-WRKS-020).
2. **R-1 Contrato BE instável / OpenAPI não materializado** — DTOs seguem `api-contract.md`; migrar
   para `@journeyos/shared/contracts` quando gerado.
3. **R-3 Race no callback OIDC** — guard + estado `exchanging`; nada protegido antes de `authenticated`
   (FE-WRKS-009).

## Definition of Done por onda

- **P1:** scaffold executável; module conhecida pelo Shell; `nx build wrks` + `journey-os-web` PASS.
- **P2:** facades com signals + erros mapeados; `nx test wrks-data-access` PASS.
- **P3 (marco MVP-dev):** login → seleção → dashboard/users/rbac navegáveis em dev.
- **P4:** sessão/empresa/RBAC 100% via Access Layer; troca de empresa sem reload e sem vazamento.
- **P5–P8:** guards aplicados; breadcrumbs corretos; states cobertos; telemetria emitida.
- **P9:** 5 specs Playwright PASS; hardening (token/idle/a11y/budget) ok.

## Approval criteria por marco

- **P3 done = MVP shippable em dev?** Sim, com mocks/BE disponível: login + empresa-select +
  dashboard + users (lista/convite) + rbac viewer funcionam.
- **P9 done = pronto para validação/baseline:** próxima ação é Layer 2 (`/fe-validator FE-WRKS-001`).

## Próxima ação (após scaffold A4 e gate A5)

`-> /fe-validator FE-WRKS-001` (ou `/fe-autopilot FE-WRKS-001` para o ciclo automático).
