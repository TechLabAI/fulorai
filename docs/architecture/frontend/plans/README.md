# Plans — Journey OS Frontend

> Planos de implementação por módulo + plano mestre de arquitetura FE.

## Arquivos

| Arquivo | Conteúdo |
|---------|----------|
| [`architecture-master-plan.md`](./architecture-master-plan.md) | **Plano mestre de arquitetura FE** — status por módulo + checklists `Etapa A1..A5/B` + log. Mantido automaticamente pelo `/fe-architecture-autopilot`. Fonte única de progresso da Layer 1. |
| [`framework-improvements.md`](./framework-improvements.md) | **Retrospectiva acionável** da 1ª corrida do pipeline (WRKS) — gaps encontrados, decisões e backlog de melhoria do framework (comandos, gerador, skeleton). |
| `plan-FE-<PREFIX>.md` | Plano de implementação por módulo — gerado por `/fe-architect-backlog <PREFIX>` (vive em `modules/<module>/frontend/plans/`) |

## Ordem de execução recomendada

```
Wave 0: WRKS
Wave 1: ASST + INTL  (paralelo)
Wave 2: LEAD + COMM  (paralelo)
Wave 3: JRNY + SALE  (paralelo)
```

Módulos **GWY, REG, MIG** são backend-only — sem plano FE.

Cada `plan-<PREFIX>.md` é gerado pelo `/fe-architect-backlog <PREFIX>` e atualizado
continuamente pelo `/fe-planner <PREFIX>` durante o ciclo de desenvolvimento.
