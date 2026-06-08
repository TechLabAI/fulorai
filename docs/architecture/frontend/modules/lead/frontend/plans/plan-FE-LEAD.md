# Plano de Execução — FE-LEAD (Lead Intelligence & Qualification)

> Plano de implementação do FE do módulo **LEAD**, ancorado no `_brief.md` e nas SPEC-01..08.
> Backlog: **28 issues** (22 funcionais + 6 integração) em 9 ondas (P1..P9).

## Resumo

O FE LEAD entrega a **superfície explicável e acionável** dos leads de cada `empresa`: uma fila
priorizada por Maturity Score, um detalhe que desdobra o score nas **6 dimensões** (com versão de
regra e badge de assist IA), um dashboard de distribuição/saúde da base, e as telas de governança —
segmentos, surveys e regras de qualificação versionadas. O coração arquitetural é o **ADR-005**
(visualização do Maturity Score: nunca caixa-preta; degradação graciosa do assist de IA, que é
BE-side e apenas refletido na UI). LEAD depende de WRKS (auth/empresa/RBAC) e é consumido a jusante
por JRNY e SALE (via eventos do BE, não pela UI).

## Mapa de ondas (estimativa por onda)

| Onda | Foco | Issues | Estimativa |
|---|---|---|---|
| P1 | Foundation (entry + descriptor + Shell) | FE-LEAD-001..003 | ~2 dias |
| P2 | Data access (4 recursos + erros) | FE-LEAD-004..008 | ~5 dias |
| P3 | Feature libs (6 features + score UI) | FE-LEAD-009..016 | ~10 dias |
| P4 | Hub integrations | INT-FE-LEAD-001..006 | ~4 dias |
| P5 | Access guards | FE-LEAD-017 | ~1 dia |
| P6 | Navigation/breadcrumbs | FE-LEAD-018 | ~1 dia |
| P7 | UX polish (states + flags + a11y) | FE-LEAD-019, 020 | ~3 dias |
| P8 | Observability | FE-LEAD-021 | ~1 dia |
| P9 | e2e + hardening | FE-LEAD-022 | ~3 dias |

Total: **~30 dias-pessoa** (sequencial); paralelizável após P2.

## Caminho crítico

```
001 → 002 → INT-001 → 004 → 008 → 011 → 012 → 019 → 020 → 022
```

`012` (ScoreBreakdown/Radar — ADR-005) é o nó de maior risco/valor: é o que cumpre o princípio
"score explicável". Ramos paralelos após P2: fila (009/010), maturity dashboard (013),
segmentação (014), surveys (015), regras (016).

## Riscos top-3 (de `06-risks-gaps-assumptions.md`)

1. **R1 — assist IA off lido como erro/score pior.** Mitigação concentrada em FE-LEAD-012/020 +
   e2e `maturity-score-degradation`: badge neutro, nunca toast de erro.
2. **R3 — bundle size** (radar/chart + 6 features). Lazy por rota + componentes de score leves
   (SVG/CSS), orçamento verificado em FE-LEAD-022.
3. **R5 — contratos BE instáveis** (breakdown/`assistIa`/dimensões). DTOs provisórios em
   `data-access`; substituir por `@journeyos/shared/contracts` quando o BE expor OpenAPI.

## Definition of Done por onda

- **P1:** `nx build/lint journey-os-web` verdes com `LEAD_MODULE_DESCRIPTOR` registrado; menu "Leads" visível.
- **P2:** facades expõem signals; `nx test/lint/build lead-data-access` PASS; refetch de score e invalidação por empresa cobertos.
- **P3:** 6 features renderizam com dados; score sempre com breakdown 6D + versão + badge; `nx test/lint/build` das features PASS.
- **P4:** auth/empresa/RBAC/erro integrados; gating de ações por permissão.
- **P5–P6:** guards e breadcrumbs por rota.
- **P7:** states loading/empty/error + lead-not-found + flags + a11y (fecha gaps G1–G4,G6,G7).
- **P8:** telemetria sem PII.
- **P9:** `nx e2e lead-e2e` PASS (9 fluxos + gaps G5/G8/G9), perf budget + axe.

## Approval criteria por marco

- **P3 done = MVP shippable em dev?** Sim para o golden path (fila → detalhe → breakdown → requalificar)
  + segmentação/surveys/regras navegáveis. Governança fina e hardening completam-se em P4–P9.
- **P9 done = módulo pronto para validação.** Cobertura EARS→Gherkin fechada (incluindo os 9 gaps do
  specs-validate), perf e a11y dentro do orçamento.

## Próxima ação

→ `/fe-architect-scaffold LEAD` (gera `apps/lead` + `libs/lead/*` + `apps/lead-e2e` via
`@journeyos/internal:module`). Implementação iterativa via `/fe-validator FE-LEAD-001` →
`/fe-autopilot FE-LEAD-001`.
