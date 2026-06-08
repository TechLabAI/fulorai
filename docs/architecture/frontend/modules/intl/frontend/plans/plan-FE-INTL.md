# Plano de Execução — FE-INTL (Intelligence & Platform · Frontend)

> Plano de ondas P1–P9 do backlog FE do INTL. Fonte: `_brief.md`, `frontend/01..06`, `frontend-spec/SPEC-01..08`.
> Total: **26 issues** (20 funcionais + 6 integração). Entrada do ciclo de implement: `/fe-validator FE-INTL-001`.

## Resumo

O FE INTL entrega a **camada de inteligência** do Journey OS sobre o `intl-service`: um **AI Copilot**
conversacional com respostas fundamentadas e citadas (degradação visível quando a IA não pode
fundamentar), uma **Base de Conhecimento** curável que alimenta o copiloto, e **dashboards
analíticos** read-only (funil + uso do copiloto). Tudo escopado à empresa ativa, consumindo a Access
Layer alimentada por WRKS (auth/empresa/RBAC). O recorte FE são **3 features** —
`feature-copilot`, `feature-knowledge`, `feature-analytics` — sobre `libs/intl/{data-access,access,
integration,navigation,ui,styles}` e a entry-lib `@journeyos/intl`.

A decisão arquitetural que mais molda a UX é o **ADR-005**: como o BE expõe `perguntar` de forma
**síncrona** (200 com resposta completa, sem streaming, citações só ao final), o MVP renderiza em
**request/response com estado `pensando` otimista + cancelamento**; streaming SSE fica diferido atrás
da flag `intl.copilot-streaming`.

## Mapa P1–P9

| Onda | Foco | Issues | Estimativa |
|---|---|---|---|
| **P1** | Foundation — contract, routes, Shell descriptor | FE-INTL-001..003 | ~2 d |
| **P2** | Data access — 3 services + 3 facades + error mapper | FE-INTL-004..008 | ~5 d |
| **P3** | Feature libs — copilot, knowledge, analytics pages/components | FE-INTL-009..014 | ~8 d |
| **P4** | Hub integrations — auth/empresa/access/http-base/shell/error | INT-FE-INTL-001..006 | ~4 d |
| **P5** | Access guards | FE-INTL-015 | ~1 d |
| **P6** | Navigation / breadcrumbs | FE-INTL-016 | ~1 d |
| **P7** | UX polish — loading/empty/error | FE-INTL-017 | ~1 d |
| **P8** | Observability | FE-INTL-018 | ~1 d |
| **P9** | e2e (7 specs) + hardening | FE-INTL-019, 020 | ~3 d |

> P4 pode iniciar em paralelo a P2 (INT-FE-INTL-004 http-base é pré-requisito de P2). As 3 features
> de P3 são independentes entre si (copilot ∥ knowledge ∥ analytics).

## Caminho crítico

```
001 → 002 → INT-004 → 004 → 005 → 010 → 011 → 017 → 020 → 019
(contract → routes → http-base → copilot api → facade → conversation page →
 badges/citations → UX polish → hardening → e2e)
```

## Riscos top-3 (de `06-risks-gaps-assumptions.md`)

1. **R2 — render de resposta degradada como fato** (pior falha do módulo). Mitigação concentrada em
   FE-INTL-011 (badges + ausência de citação em estados degradados) + e2e copilot-degraded (019).
2. **R1 — latência alta/variável do Copilot.** Estado `pensando` imediato + cancelamento
   (FE-INTL-005/010); observability de p95 (FE-INTL-018).
3. **R4 — vazamento cross-empresa na troca.** Reset effect (INT-FE-INTL-002 + FE-INTL-020) + e2e
   empresa-switch-isolation (019).

## Definition of Done por onda

- **P1:** `nx build journey-os-web` verde com `INTL_MODULE_DESCRIPTOR` registrado; menu mostra "Inteligência".
- **P2:** `nx test intl-data-access` verde — otimismo/cancelamento do copiloto, indexar 202/503, error mapper.
- **P3:** 3 features renderizam (SPEC-02 no DOM); fundamentação visual correta (chips só em estado fundamentado).
- **P4:** todas as chamadas autenticadas + escopadas por empresa; menu/guards derivados de RBAC.
- **P5–P8:** guards negam/permitem corretamente; breadcrumbs resolvem; states padronizados; telemetria emitindo.
- **P9:** `nx e2e intl-e2e` verde (7 specs); a11y dos badges; reset de empresa sem vazamento.

## Approval criteria por marco

- **P3 done = MVP shippable em dev?** Sim, com mocks/fixtures do `intl-service`: copilot pergunta→resposta
  fundamentada/degradada, knowledge CRUD+indexar, analytics read-only — todos escopados à empresa.
- **P9 done = MVP pronto para validação:** fluxos e2e verdes, isolamento multi-empresa e degradação
  cobertos, observability ligada.

## Próxima ação

```
/fe-validator FE-INTL-001        (BASELINE)
ou
/fe-autopilot FE-INTL-001        (ciclo automático VO+Planner+Implement)
```
