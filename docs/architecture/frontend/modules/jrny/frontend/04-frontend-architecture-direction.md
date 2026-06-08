# 04 — Frontend Architecture Direction — JRNY (Journey & Routing)

> Stack, organização de libs, dependências shared, routing, estado e contrato de módulo do FE JRNY.
> module `jrny` · scope `scope:jrny`.

## 1. Stack

Angular 18+ · Nx 19+ · TypeScript strict · RxJS 7.8 **apenas na borda HTTP** + **Signals** para
estado de UI · Jest (unit) · Playwright (e2e). Sem NgRx (`ADR-002`). Sem lib de canvas pesada no MVP
(`ADR-005`).

## 2. App Boundary

`apps/jrny/` é um **host fino** (build/serve isolado + base do `apps/jrny-e2e`) que carrega o entry
como library **`@journeyos/jrny`** (`libs/jrny/shell-entry`) via `loadChildren` (`ADR-003`). Features
são **standalone** + **OnPush**; NgModule só se o entry exigir.

## 3. Library Organization (tags Nx)

| Lib | `type:` | `scope:` |
|---|---|---|
| `libs/jrny/shell-entry` | `domain` | `jrny` |
| `libs/jrny/feature-journey-list` | `feature` | `jrny` |
| `libs/jrny/feature-journey-builder` | `feature` | `jrny` |
| `libs/jrny/feature-stage-editor` | `feature` | `jrny` |
| `libs/jrny/feature-routing-engine` | `feature` | `jrny` |
| `libs/jrny/feature-decision-log` | `feature` | `jrny` |
| `libs/jrny/feature-journey-analytics` | `feature` | `jrny` |
| `libs/jrny/data-access` | `data-access` | `jrny` |
| `libs/jrny/access` | `domain` | `jrny` |
| `libs/jrny/integration` | `domain` | `jrny` |
| `libs/jrny/navigation` | `domain` | `jrny` |
| `libs/jrny/ui` | `ui` | `jrny` |
| `libs/jrny/styles` | `ui` | `jrny` |
| `apps/jrny` | `app` | `jrny` |

Direções de dependência conforme `nx-boundaries.md`. Features dependem de `data-access`/`ui`/`navigation`;
nunca de outra feature. Proibido importar `scope:` de outro módulo de domínio.

> **Facade opcional:** JRNY é complexo (builder ↔ stage-editor ↔ routing-engine compartilham a jornada
> em edição). Avaliar `libs/jrny/facade` (`type:facade` + `layer:facade`) na etapa de Specs se o estado
> de "jornada em edição" precisar ser orquestrado entre features. No MVP, começar com facade na
> `data-access` e promover só se necessário (decisão registrável em ADR de Specs).

## 4. Shared Library Dependencies

- `@journeyos/shared/access-http-base` (**obrigatório** — HTTP + interceptors JWT/empresa)
- `@journeyos/shared/access-decision` (**obrigatório** — entitlement `jrny.*`, `NavigationService`)
- `@journeyos/shared/auth-session` (**obrigatório** — bearer token/sessão)
- `@journeyos/shared/empresa-context` (**obrigatório** — empresa ativa + invalidação na troca)
- `@journeyos/shared/ui-components` · `ui-feedback` · `ui-tokens` (sempre)
- `@journeyos/shared/error-model` (mapear `ProblemDetail` → `AppError`)
- `@journeyos/shared/observability` (recomendado)
- Candidatos a **patterns shared** (sob demanda, na Specs): smart-table (jornadas/regras/decisões),
  sortable-list/stepper (estágios ordenados), timeline (decision log).

## 5. Routing Strategy

Shell → `@journeyos/jrny` via `loadChildren`; sub-rotas por feature via `loadComponent`.
`canActivate: [authGuard, empresaGuard, accessGuard('jrny.*')]`. Rotas previstas (detalhadas no SPEC-01):

```
/jrny/journeys                      -> feature-journey-list
/jrny/journeys/:id/builder          -> feature-journey-builder
/jrny/journeys/:id/stages/:stageId  -> feature-stage-editor   (ou painel dentro do builder)
/jrny/journeys/:id/rules            -> feature-routing-engine
/jrny/leads/:leadId/decisions       -> feature-decision-log
/jrny/analytics                     -> feature-journey-analytics
```

## 6. State Strategy

Signals locais nas facades (`data-access`): `signal<T>` privado + `.asReadonly()` público;
`computed()` para derivações (editável? ações disponíveis por estado+permissão; resumo de condição;
visibilidade do badge `assistIa`; funil); `effect()` para reagir à **troca de empresa** (invalidar
jornadas/builder em tela). Sem NgRx, sem `BehaviorSubject` manual. Estado transversal (sessão/empresa/
RBAC) vem de `@journeyos/shared/access-*` — não duplicado no JRNY.

## 7. Module Contract Strategy

`jrny.contract.ts` (em `shell-entry`):

- `ModuleMenuMetadata`: `key: 'jrny'`, `label: 'Jornadas'`, `route: '/jrny/journeys'`, `icon`,
  `deepLinks` (builder, regras, decisões, analytics).
- `ModulePermissionMap`: `jrny.jornada.{criar,editar,publicar,arquivar,ler}`,
  `jrny.estagio.{criar,editar,ler}`, `jrny.regra.{criar,editar}`, `jrny.roteamento.ler`.
- `ModuleFeatureFlags` (com `defaultState`): `jrny.journey-analytics` (on), `jrny.routing-rules` (on);
  candidata `jrny.journey-builder-canvas` (**off** — reservada para o canvas pós-MVP, `ADR-005`).
- `JRNY_MODULE_DESCRIPTOR` exportado para o Shell (registro efetivo = implement P1, `FE-JRNY-003`).

---

## Referências

- `02-architecture-blueprint.md` · `05-state-and-data-flow.md` · `adr/ADR-001..005`
- `docs/architecture/frontend/standards/{module-pattern,nx-boundaries,access-layer-contracts}.md`
