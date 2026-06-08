# Plano de Execução — FE-ASST (Asset Hub · Frontend)

> Plano de ondas P1–P9 do módulo ASST FE. Âncora: `_brief.md` (Asset Hub) — repositório único de
> ativos de conteúdo do workspace, com versionamento imutável, workflow de aprovação e composição
> assistida (Asset Studio via TechLab AI, delegada pelo BE). Total: **26 issues** (20 funcionais +
> 6 integração).

## Resumo

O FE ASST dá à persona de growth (Marina) um catálogo único de assets com busca, composição assistida
(Asset Studio) e versionamento imutável; e ao aprovador (Rafael) uma fila de aprovações para
aprovar/rejeitar/publicar. Tudo escopado por empresa (sem vazamento cross-empresa — LGPD) e gated por
RBAC (`asst.*`). O Asset Studio degrada graciosamente quando a IA está indisponível (ADR-005),
preservando catálogo, versionamento e aprovação. Depende de WRKS (auth) + Access Layer (Wave 0).

## Mapa de ondas

| Onda | Escopo | Issues | Estimativa |
|---|---|---|---|
| **P1** | Foundation: contract, routes/module, Shell descriptor | FE-ASST-001..003 | ~2 d |
| **P2** | Data access: Asset/Versão/Studio/Workflow services + facades + erros | FE-ASST-004..008 | ~6 d |
| **P3** | Feature libs: library, detail, studio, approval | FE-ASST-009..015 | ~11 d |
| **P4** | Hub integrations: http-base, auth, empresa-context, access-decision, shell, error-model | INT-FE-ASST-001..006 | ~5 d |
| **P5** | Access guards | FE-ASST-016 | ~1 d |
| **P6** | Navigation / breadcrumbs | FE-ASST-017 | ~1 d |
| **P7** | UX polish (loading/empty/error) | FE-ASST-018 | ~2 d |
| **P8** | Observability | FE-ASST-019 | ~1 d |
| **P9** | e2e Playwright + hardening | FE-ASST-020 | ~3 d |

> P4 (integrations) roda **em paralelo** a P2/P3 — as facades já preveem o wiring shared. P3 pode
> paralelizar em 3 trilhas após P2: catálogo (009/010), detalhe+versões (011/012), studio (013) e
> aprovação (014/015).

## Caminho crítico

```
001 → 002 → INT-001 → 004 → 005 → 007 → 011 → 012 → 015 → 018 → 020
```
Ramo Studio: 006 → 013 (após 012). Ramo aprovação: 014 → 015.

## Riscos top-3 (de 06-risks-gaps-assumptions)

1. **R-2 — Vazamento cross-empresa** (crítico/LGPD): mitigado por INT-FE-ASST-003 (invalidação na
   troca) + FE-ASST-020 (`empresa-isolation.feature`).
2. **R-1 — Contrato BE instável** (OpenAPI do `asst-service` não materializado): `data-access` tipado
   à mão até lá; `backend-api-cross-link.md` rastreia a fonte.
3. **R-3 — Latência/timeout da IA no Studio**: degradação graciosa (ADR-005, FE-ASST-006/013); se p95
   alto, reavaliar async em novo ADR.

## Definition of Done por onda

- **P1:** `nx build asst` + `build/lint journey-os-web` verdes; módulo registrado no Shell.
- **P2:** services/facades com testes (incl. casos `503`/`409`/`404`); sem HttpClient em componente.
- **P3:** 4 features renderizam (page + components de SPEC-02); golden path navegável em dev (mock).
- **P4:** wiring shared ativo (X-Empresa-Id, sessão, AccessDecision, error-model); menu derivado de RBAC.
- **P5–P8:** guards bloqueiam rotas; breadcrumbs corretos; estados de UX consistentes; telemetria sem PII.
- **P9:** 6 specs Playwright verdes (UINV-2/4/7/8 cobertas); budget de perf respeitado.

## Approval criteria por marco

- **P3 done = MVP shippable em dev?** Sim — com o golden path (criar → compor → versão → submeter →
  aprovar → publicar) funcional sobre mock/stub do `asst-service`, mais P4 (wiring real). P9 valida
  os fluxos reais.
- **MVP completo:** P1–P9 verdes + isolamento multi-empresa testado (R-2) + degradação do Studio
  testada (R-3/ADR-005).

## Próxima ação

→ `/fe-architect-scaffold ASST` (gera `apps/asst` + `libs/asst/*` + `apps/asst-e2e` via
`@journeyos/internal:module`), depois `/fe-validator FE-ASST-001` para entrar no ciclo de implement.
