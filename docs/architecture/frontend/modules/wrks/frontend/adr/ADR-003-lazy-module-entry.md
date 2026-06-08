# ADR-003 — `wrks.module.ts` lazy (NgModule só no entry)

- **Status:** accepted

## Contexto

O Shell (`journey-os-web`) carrega módulos sob demanda. Angular moderno é standalone-first, mas o
padrão de integração com o Shell do Journey OS usa um `NgModule` lazy por module como ponto de
registro (contrato, rotas, providers do módulo). Precisamos definir onde o `NgModule` é permitido.

## Decisão

`wrks.module.ts` é o **único** `NgModule` do módulo, usado como entry lazy (`loadChildren` do
Shell). **Todas** as features e componentes abaixo dele são `standalone` + `ChangeDetectionStrategy.OnPush`,
carregados via `loadComponent`. Nenhum outro `NgModule` é introduzido em `libs/wrks/*`.

## Alternativas consideradas

1. **100% standalone, sem NgModule** (rota lazy direto para `loadComponent` raiz) — adiada: o
   registro no Shell (contrato + providers do módulo) hoje se apoia no entry NgModule; reavaliar quando
   o Shell suportar registro de module puramente standalone.
2. **NgModules por feature** — rejeitada: quebra lazy granular e standalone-first.

## Consequências

- **Positivas:** ponto único de registro/bootstrap do módulo; lazy granular por feature; compatível
  com o module registry do Shell (ADR-004).
- **Negativas:** um resquício de `NgModule` por módulo até o Shell migrar para registro standalone.

## Referências

- `04-frontend-architecture-direction.md` §2, §5
- ADR-004 (shell integration)
