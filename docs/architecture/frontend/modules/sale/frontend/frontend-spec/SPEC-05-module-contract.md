# SPEC-05 — Module Contract — SALE · Frontend

> Conteúdo de `libs/sale/shell-entry/sale.contract.ts` (+ permission-map, feature-flags). Espelha o
> `module_contract` do `generator-config.yml`.

```typescript
export const MODULE_KEY = 'sale';

export const MODULE_MENU_METADATA: ModuleMenuMetadata = {
  key: MODULE_KEY,
  label: 'Vendas',
  route: '/sale/pipeline',
  icon: 'monetization_on',
  deepLinks: [
    { label: 'Pipeline',   route: '/sale/pipeline',     permission: 'sale.oportunidade.read' },
    { label: 'Ofertas',    route: '/sale/offers',        permission: 'sale.oferta.read' },
    { label: 'Compras',    route: '/sale/purchases',     permission: 'sale.compra.read' },
    { label: 'Atribuição', route: '/sale/attribution',   permission: 'sale.atribuicao.read' },
    { label: 'Receita',    route: '/sale/dashboard',     permission: 'sale.ltv.read', flag: 'sale.revenue-dashboard' },
    // Detalhe de oportunidade/oferta/compra são deep links contextuais (dependem de :id) — não no menu raiz.
  ],
};

export const MODULE_PERMISSION_MAP: ModulePermissionMap = {
  'sale.oportunidade.read':    ['SDR', 'INFOPRODUTOR', 'HEAD_GROWTH'],
  'sale.oportunidade.criar':   ['SDR', 'INFOPRODUTOR', 'HEAD_GROWTH'],
  'sale.oportunidade.mover':   ['SDR', 'INFOPRODUTOR', 'HEAD_GROWTH'],
  'sale.oportunidade.fechar':  ['SDR', 'INFOPRODUTOR'],
  'sale.oferta.read':          ['SDR', 'INFOPRODUTOR', 'HEAD_GROWTH'],
  'sale.oferta.criar':         ['INFOPRODUTOR', 'HEAD_GROWTH'],
  'sale.oferta.editar':        ['INFOPRODUTOR', 'HEAD_GROWTH'],
  'sale.oferta.desativar':     ['INFOPRODUTOR'],
  'sale.compra.read':          ['INFOPRODUTOR', 'HEAD_GROWTH'],
  'sale.compra.estornar':      ['INFOPRODUTOR'],
  'sale.compra.cancelar':      ['INFOPRODUTOR'],
  'sale.atribuicao.read':      ['HEAD_GROWTH', 'INFOPRODUTOR'],
  'sale.atribuicao.criar':     ['HEAD_GROWTH'],
  'sale.atribuicao.ativar':    ['HEAD_GROWTH'],
  'sale.ltv.read':             ['INFOPRODUTOR', 'HEAD_GROWTH'],
};

export const MODULE_FEATURE_FLAGS: ModuleFeatureFlags = {
  'sale.revenue-dashboard':       { defaultState: 'enabled'  },
  'sale.attribution-multitouch':  { defaultState: 'disabled' },
};
```

> **`sale.compra.registrar` NÃO está no mapa do FE** — a ingestão de compra é server-to-server
> (checkout/gateway via GWY com service token); não existe ação de UI que a exija.

## Justificativa das permissões

> Os papéis são **referenciais** (o RBAC efetivo vive no WRKS/`AccessDecisionService`; a UI apenas
> reflete). Espelham o api-contract do BE (`sale.<recurso>.<acao>`).

| Permissão | Por quê | Personas (ref.) |
|---|---|---|
| `sale.oportunidade.read` / `.criar` / `.mover` | operar o pipeline Kanban (ler/criar/mover deals) — base da persona SDR | Lucas, Rafael, Marina |
| `sale.oportunidade.fechar` | autoridade de **ganhar/perder** (fechamento terminal) | Lucas, Rafael |
| `sale.oferta.read` | ler o catálogo (necessário ao pipeline/compras) | Lucas, Rafael, Marina |
| `sale.oferta.criar` / `.editar` / `.desativar` | governar o catálogo versionado | Rafael, Marina |
| `sale.compra.read` | consultar receita confirmada + breakdown | Rafael, Marina |
| `sale.compra.estornar` / `.cancelar` | **ajustes de receita** (recalculam LTV) — alto impacto | Rafael |
| `sale.atribuicao.read` / `.criar` / `.ativar` | governar modelos de atribuição (ROI por origem) | Marina (HEAD_GROWTH) |
| `sale.ltv.read` | ler dashboard de receita/LTV | Rafael, Marina |

## Justificativa das flags

| Flag | default | Por quê |
|---|---|---|
| `sale.revenue-dashboard` | `enabled` | dashboard de receita (read-only, Elastic-backed) — desligável por tenant; endpoint de funil ainda **proposto** (SPEC-04 gap G1), degrada para LTV-apenas/vazio. |
| `sale.attribution-multitouch` | `disabled` | **reservada** para modelos de atribuição multi-touch (FIRST_TOUCH/LINEAR configuráveis). No MVP o default é **last-touch** determinístico; ligar a flag habilita a configuração multi-touch na tela de atribuição. |

> **`pipeline` (Kanban) não é flag** — é o núcleo do MVP (a razão de ser operacional do SALE).

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL expose the SALE menu entry "Vendas" routed to /sale/pipeline gated by sale.oportunidade.read.`
- `WHILE sale.revenue-dashboard is disabled, THE SYSTEM SHALL hide the "Receita" deep link and omit its route.`
- `WHERE sale.attribution-multitouch is enabled, THE SYSTEM SHALL expose multi-touch model configuration; otherwise THE SYSTEM SHALL default attribution to last-touch.`
- `THE SYSTEM SHALL gate win/lose, refund/cancel and model-activation affordances behind sale.oportunidade.fechar, sale.compra.estornar/cancelar and sale.atribuicao.ativar respectively.`
- `THE SYSTEM SHALL filter menu deep links by permission via NavigationService + AccessDecisionService.`

## Referências
- `04-frontend-architecture-direction.md` §7 · `generator-config.yml` (`module_contract`) · `adr/ADR-004`, `ADR-005`
