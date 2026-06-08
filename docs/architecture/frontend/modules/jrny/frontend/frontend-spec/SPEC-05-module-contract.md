# SPEC-05 — Module Contract — JRNY · Frontend

> Conteúdo de `libs/jrny/shell-entry/jrny.contract.ts` (+ permission-map, feature-flags). Espelha o
> `module_contract` do `generator-config.yml`.

```typescript
export const MODULE_KEY = 'jrny';

export const MODULE_MENU_METADATA: ModuleMenuMetadata = {
  key: MODULE_KEY,
  label: 'Jornadas',
  route: '/jrny/journeys',
  icon: 'account_tree',
  deepLinks: [
    { label: 'Jornadas',  route: '/jrny/journeys',  permission: 'jrny.jornada.ler' },
    { label: 'Analytics', route: '/jrny/analytics',  permission: 'jrny.roteamento.ler', flag: 'jrny.journey-analytics' },
    // Builder/Regras/Decisões são deep links contextuais (dependem de :id/:leadId) — não no menu raiz.
  ],
};

export const MODULE_PERMISSION_MAP: ModulePermissionMap = {
  'jrny.jornada.ler':       ['HEAD_GROWTH', 'INFOPRODUTOR', 'SDR'],
  'jrny.jornada.criar':     ['HEAD_GROWTH', 'INFOPRODUTOR'],
  'jrny.jornada.editar':    ['HEAD_GROWTH', 'INFOPRODUTOR'],
  'jrny.jornada.publicar':  ['INFOPRODUTOR'],                 // autoridade de publicação
  'jrny.jornada.arquivar':  ['INFOPRODUTOR'],
  'jrny.estagio.ler':       ['HEAD_GROWTH', 'INFOPRODUTOR', 'SDR'],
  'jrny.estagio.criar':     ['HEAD_GROWTH', 'INFOPRODUTOR'],
  'jrny.estagio.editar':    ['HEAD_GROWTH', 'INFOPRODUTOR'],
  'jrny.regra.criar':       ['HEAD_GROWTH', 'INFOPRODUTOR'],
  'jrny.regra.editar':      ['HEAD_GROWTH', 'INFOPRODUTOR'],
  'jrny.roteamento.ler':    ['HEAD_GROWTH', 'INFOPRODUTOR', 'SDR'],
};

export const MODULE_FEATURE_FLAGS: ModuleFeatureFlags = {
  'jrny.journey-analytics':       { defaultState: 'enabled'  },
  'jrny.journey-builder-canvas':  { defaultState: 'disabled' },
};
```

## Justificativa das permissões

> Os papéis são **referenciais** (o RBAC efetivo vive no WRKS/`AccessDecisionService`; a UI apenas
> reflete). Espelham o api-contract do BE (`jrny.<recurso>.<acao>`).

| Permissão | Por quê | Personas (ref.) |
|---|---|---|
| `jrny.jornada.ler` / `jrny.estagio.ler` / `jrny.roteamento.ler` | leitura de jornadas, estágios e estado/decisões — base de toda a UI | Marina, Rafael, Lucas |
| `jrny.jornada.criar` / `jrny.jornada.editar` | desenhar/editar jornadas (rascunho) | Marina, Rafael |
| `jrny.jornada.publicar` / `jrny.jornada.arquivar` | **autoridade de publicação** da estratégia de funil | Rafael (INFOPRODUTOR) |
| `jrny.estagio.criar` / `jrny.estagio.editar` | montar os estágios da jornada | Marina, Rafael |
| `jrny.regra.criar` / `jrny.regra.editar` | versionar regras de roteamento | Marina, Rafael |

## Justificativa das flags

| Flag | default | Por quê |
|---|---|---|
| `jrny.journey-analytics` | `enabled` | analytics de jornada (read-only) — desligável por tenant; endpoint ainda **proposto** (SPEC-04 gap), degrada para vazio. |
| `jrny.journey-builder-canvas` | `disabled` | **reservada** para o canvas drag-and-drop visual **pós-MVP** (ADR-005). No MVP o builder é o editor estruturado; ligar a flag carregaria a lib de canvas por import dinâmico. |

> **`routing-rules` não é flag** — é núcleo do MVP (o Routing Engine é a razão de ser do módulo).

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL expose the JRNY menu entry "Jornadas" routed to /jrny/journeys gated by jrny.jornada.ler.`
- `WHILE jrny.journey-analytics is disabled, THE SYSTEM SHALL hide the "Analytics" deep link and omit its route.`
- `WHERE jrny.journey-builder-canvas is enabled, THE SYSTEM SHALL load the canvas builder lazily; otherwise THE SYSTEM SHALL render the structured stage editor.`
- `THE SYSTEM SHALL gate publish/archive affordances behind jrny.jornada.publicar / jrny.jornada.arquivar.`
- `THE SYSTEM SHALL filter menu deep links by permission via NavigationService + AccessDecisionService.`

## Referências
- `04-frontend-architecture-direction.md` §7 · `generator-config.yml` (`module_contract`) · `adr/ADR-004`, `ADR-005`
