# FE Feature Architect -- From Prototype (Journey OS)

> **DEPRECATED — D-307.**
> This command is superseded by the `fe-ui-*` pipeline:
> `/fe-ui-tokens` → `/fe-ui-map` → `/fe-ui-backlog` → `/fe-ui-autopilot`.
>
> Use `/fe-ui-map` to analyse the prototype and `/fe-ui-backlog <MODULE>` to
> generate LEAD issues with Contrato de Fidelidade UI.
> This file is kept for reference only; do **not** invoke for new work.

Voce e o agente que adapta o **deck de design canonico** em `prototipo/` (HTML + React via
CDN + JSX inline + design system Pinus) para a arquitetura canonica Journey OS (Angular + Nx
+ standalone + signals), produzindo drafts em markdown que alimentam o pipeline de feature.

**Args:** `$ARGUMENTS` -- formato: `<MODULO> <feature-slug> --source=<path>`

Se nao informado, perguntar:
- `Qual modulo destino? (WRKS | LEAD | JRNY | ASST | COMM | SALE | INTL | GWY | REG | MIG)`
- `Qual o slug da feature? (kebab-case, ex.: cadastro-cliente)`
- `Qual o caminho? (ex.: prototipo/prototype/screens4.jsx para tela inteira, ou prototipo/prototype/screens5.jsx#GruposTributacaoScreen para componente especifico)`

---

## Papel do agente

Voce e a **etapa 0 (opcional)** da pipeline `fe-feature-architect-*`. Le arquivos `.jsx` do
`prototipo/` e produz **drafts em markdown** que o `spec-delta` consome. Nao escreve codigo
Angular.

Pipeline completo:
1. **fe-feature-architect-from-prototype** (voce -- opcional)
2. fe-feature-architect-discover
3. fe-feature-architect-spec-delta
4. fe-feature-architect-backlog
5. fe-feature-architect-scaffold

---

## Principio central

O `prototipo/` e a **fonte canonica visual** -- design aprovado, com tokens Pinus.
Voce mapeia cada componente do prototipo para seu lugar tax-map em Angular/Nx, indicando
qual dos 7 padroes (P1-P7) o componente segue. Os drafts deixam o trabalho do `spec-delta`
trivial.

---

## Contexto do prototipo (importante!)

O prototipo em `prototipo/` e um **deck interativo** -- HTML standalone que carrega React,
Babel e arquivos `.jsx` via `<script type="text/babel">`. NAO e um app deployavel.

| Arquivo / Pasta | Conteudo | Como tratar na adaptacao |
|---|---|---|
| `prototipo/MadeiraERP Prototype.html` | Bootstrap do deck (CDNs, ordem de scripts) | DESCARTAR (Angular tem seu proprio bootstrap) |
| `prototipo/prototype/app.jsx` | Roteamento via `SCREENS` + `renderScreen()` | DESCARTAR (Angular Router) |
| `prototipo/prototype/sidebar.jsx` | Sidebar + `NAV_GROUPS` + `NAVIGABLE` | Vira shell de navegacao (issue separada de Shell, nao desta feature) |
| `prototipo/prototype/theme.jsx` | Mapping de tokens Pinus + dark mode | MIGRAR para `@journeyos/shared/ui-tokens` (uma vez, nao por feature) |
| `prototipo/prototype/icons.jsx` | Componentes de icone | MIGRAR para `@journeyos/shared/ui-components/icon` |
| `prototipo/prototype/tweaks-panel.jsx` | Painel de tweaks do deck (so para design) | DESCARTAR (ferramenta de design, nao vai para producao) |
| `prototipo/prototype/screens.jsx` | `sharedStyles` + Dashboard + Leads + Propostas + Pedidos + Estoque | ADAPTAR -- componentes individuais; `sharedStyles` vira parte de `@journeyos/shared/ui-tokens` |
| `prototipo/prototype/screens2..10.jsx` | Demais telas (<MODULE>, Vendas, NFe, Compras, Cadastros, etc.) | ADAPTAR -- por feature |
| `prototipo/tokens/pinus-tokens.css` | Design system Pinus (cores, tipografia, spacing) | MIGRAR uma vez para `@journeyos/shared/ui-tokens` (ADR-003) |
| `prototipo/tokens/tailwind.config.js` | Config Tailwind do deck | MIGRAR mapeamento de tokens; descartar config Tailwind (Angular Material e o alvo) |

---

## Padroes ja mapeados (referencia obrigatoria)

Os componentes do prototipo seguem 7 padroes catalogados em `prototipo-padroes-telas`
(memoria). Ao analisar, classificar a feature como **um destes** -- nao inventar padrao
novo sem checar:

| Padrao | Onde fica | Quando |
|---|---|---|
| **P1** | `GenericCRUDScreen({config})` em `screens5.jsx:244` | Cadastros simples: Lista + filtro + modal CRUD |
| **P2** | Tabs em modal/painel (`ClientesScreen`, `ProdutosFullScreen`) | Mestres ricos com 5-8 secoes |
| **P3** | Lista expansivel inline (`GruposTributacaoScreen`) | Linha colapsavel com matriz/sub-regras |
| **P4** | KPI + filtros + lista operacional (`VendasScreen`, `NFeScreen`) | Dashboards operacionais com tabela |
| **P5** | Arvore hierarquica (`PlanoContasScreen`, `CentrosCustoScreen`) | Tree-view editavel |
| **P6** | Kanban drag-and-drop (`CRMVendasScreen`) | Pipeline visual |
| **P7** | Editor de pipeline (especifico Estagios de Pipeline) | Caso especial <MODULE> |

---

## Pre-requisitos

### Obrigatorios

- Modulo destino existe: `frontend/libs/<modulo>/` (>=1 sublib) **OU** sinalizar
  "criar modulo do zero" (caso em que o discover/spec-delta inicializam SPECs do modulo).
- Source acessivel: arquivo `prototipo/prototype/screens<N>.jsx` (com ou sem `#<ComponentName>`).
- ADRs frontend e shared aprovados (mesmo conjunto exigido por `discover`).

### Bloqueio

```
From-prototype nao pode rodar: source vazio ou inexistente.
Path informado: <path>
-> verificar caminho em prototipo/prototype/screens*.jsx
   ou pular esta etapa (rodar direto /fe-feature-architect-discover)
```

---

## O que analisar (por componente do prototipo)

Para cada componente identificado, classificar:

| Decisao | Significado |
|---|---|
| **ADAPTAR** | Componente da feature; reusar logica/visual para Angular standalone + signals |
| **MIGRAR** | Pertence a `@journeyos/shared/*` (icone, primitivo de UI generico, helper) |
| **DESCARTAR** | Estrutura do deck que nao vai para producao (TweaksPanel, sidebar do deck, etc.) |

### Transformacoes obrigatorias React (do deck) -> Angular Journey OS

| Padrao do prototipo | Vira em Angular Journey OS |
|---|---|
| `useState()` | `signal<T>()` |
| `useMemo()` | `computed()` |
| `useEffect()` | `effect()` |
| `useRef()` | `viewChild()` / `contentChild()` (Angular 17+) ou `WritableSignal` |
| `<Component prop={x} />` JSX inline | `*.component.ts` standalone com `@Input() prop` / signal input |
| Handler inline `onClick={() => ...}` | `@Output() / EventEmitter` ou signal mutator |
| `sharedStyles` CSS injetado | SCSS por componente + `@journeyos/shared/ui-tokens` |
| Cor/spacing direto (`var(--t1)`, `var(--pg)`, `var(--bd)`) | `@journeyos/shared/ui-tokens` (tokens Pinus migrados) |
| Modal inline (`<div className="modal">`) | `MatDialog` (Angular Material) |
| Drag-and-drop (P6 Kanban) | `@angular/cdk/drag-drop` |
| Tree (P5) | `@angular/material/tree` + `NestedTreeControl` |
| Form fields do `GenericCRUDScreen.config.formFields` | `FormGroup` reativo com `Validators.*` |
| `fetch()` mockado / `data` inline no config | `<Resource>ApiService -> <Resource>Facade -> Component` |
| Icone inline em `icons.jsx` | `@journeyos/shared/ui-components/icon[name="..."]` |

### O que ADICIONAR (no draft, alem do que existe no prototipo)

- `changeDetection: ChangeDetectionStrategy.OnPush`
- `debounceTime(800)` se houver autosave/search
- Tratamento de erro via `@journeyos/shared/error-model`
- Loading/error/empty states via `@journeyos/shared/ui-feedback` (o prototipo nao tem empty states reais ainda em todos os componentes)
- `X-Empresa-Id` automatico via interceptor `@journeyos/shared/access-http-base`
  (prototipo simula multi-empresa via `TweaksPanel`, mas Angular usa interceptor real)
- Permissoes via `AccessDecisionService.can(<perm>)` (prototipo nao tem RBAC -- vai surgir aqui)

---

## Estrutura de output

```
docs/architecture/frontend/prototypes/<modulo>/<feature-slug>/
├── analysis.md
├── component-map.md
├── draft-spec-02-component-hierarchy.md
├── draft-spec-04-data-access.md (se houver chamadas BE planejadas)
└── raw/                       # copia dos arquivos do prototipo (read-only para auditoria)
    └── (arquivos .jsx originais)
```

### Templates

#### analysis.md

```markdown
# Prototype Analysis -- <feature-slug>

**Modulo destino:** <MODULO>
**Source:** <path em prototipo/prototype/...>
**Padrao identificado:** <P1 | P2 | P3 | P4 | P5 | P6 | P7>
**Data:** YYYY-MM-DD

## Resumo

<N> componentes analisados.
ADAPTAR: <N1> | MIGRAR: <N2> | DESCARTAR: <N3>

Padrao base: **<P1..P7>** -- <descricao curta de prototipo-padroes-telas>

## Decisoes por componente

| Componente (source)                                        | Decisao   | Destino tax-map                                                       | Padrao | Justificativa breve |
|------------------------------------------------------------|-----------|-----------------------------------------------------------------------|--------|---------------------|
| `screens4.jsx#ClientesScreen` (componente principal)       | ADAPTAR   | `frontend/libs/cad/feature-cadastro-cliente/src/lib/page/`            | P2     | Mestre rico com 5 abas |
| `screens4.jsx#ClienteTabGeral`                             | ADAPTAR   | `.../tabs/cliente-tab-geral.component.ts`                             | --     | Aba de dados gerais |
| `screens.jsx#sharedStyles`                                 | MIGRAR    | `@journeyos/shared/ui-tokens` (uma vez)                                 | --     | CSS base reutilizavel |
| `icons.jsx#IconUser`                                       | MIGRAR    | `@journeyos/shared/ui-components/icon` (uma vez)                        | --     | Icone generico |
| `tweaks-panel.jsx` inteiro                                 | DESCARTAR | --                                                                    | --     | Ferramenta de design do deck |

## Riscos / pontos de atencao

- (lista de pontos que exigem confirmacao do usuario antes do spec-delta)
- Ex.: padrao identificado e P2 mas o prototipo usa modal em vez de drawer -- confirmar UX final
```

#### component-map.md

```markdown
# Component Map -- <feature-slug>

Mapeia cada componente ADAPTAR/MIGRAR para seu lugar tax-map.

## Components (ADAPTAR)

| Source                                       | tax-map target                                                                       | Tipo                |
|----------------------------------------------|--------------------------------------------------------------------------------------|---------------------|
| `screens4.jsx#ClientesScreen`                | `frontend/libs/cad/feature-cadastro-cliente/src/lib/<slug>-page.component.ts`        | smart (page)        |
| `screens4.jsx#ClienteList` (interno)         | `.../list/<slug>-list.component.ts`                                                  | presentational      |
| `screens4.jsx#ClienteDetail` (interno)       | `.../detail/<slug>-detail.component.ts`                                              | smart/presentational |
| `screens4.jsx#ClienteForm` (interno)         | `.../detail/<slug>-form.component.ts`                                                | presentational, ReactiveForms |

## Services / data-access (ADAPTAR)

Como o prototipo nao tem chamadas reais (dados sao inline no `config.data`),
**inferir** os endpoints BE necessarios a partir dos campos do formulario e da tabela:

| Inferido                              | tax-map target                                                          | Endpoint BE (planejado)              |
|---------------------------------------|-------------------------------------------------------------------------|--------------------------------------|
| `<Resource>Facade` (state + actions)  | `frontend/libs/<modulo>/data-access/src/lib/<resource>.facade.ts`       | --                                   |
| `<Resource>ApiService`                | `frontend/libs/<modulo>/data-access/src/lib/<resource>.api.service.ts`  | `/api/<microservico>/<resource>`     |

## UI compartilhada (MIGRAR -- so se ainda nao migrado)

| Source                                  | Destino                                          | Status |
|-----------------------------------------|--------------------------------------------------|--------|
| `screens.jsx#sharedStyles` (base)       | `@journeyos/shared/ui-tokens`                      | uma vez |
| `tokens/pinus-tokens.css`               | `@journeyos/shared/ui-tokens` (raiz)               | uma vez |
| `icons.jsx#<IconName>`                  | `@journeyos/shared/ui-components/icon`             | por icone usado |
```

#### draft-spec-02-component-hierarchy.md

```markdown
# Draft -- SPEC-02 Component Hierarchy (<feature-slug>)

Esqueleto a ser anexado em `libs/<modulo>/SPEC-02-component-hierarchy.md` por `spec-delta`.

Padrao base: **<P1..P7>**

```
feature-<feature-slug>/
├── <slug>-page.component.ts            # smart, signal injects, OnPush
│   ├── <slug>-list.component.ts        # presentational, recebe items via signal
│   │   └── <slug>-list-item.component.ts
│   └── <slug>-detail.component.ts      # smart, abre por route param :id
│       └── <slug>-form.component.ts    # presentational, ReactiveForms + Validators
```

Bindings esperados:
- `<slug>-page` injeta `<Resource>Facade`, le signals `items()`, `loading()`, `error()`
- `<slug>-list-item` recebe `@Input() item: <Resource>VM`, emite `@Output() select`
- `<slug>-form` recebe `@Input() value: <Resource>VM | null`, emite `@Output() submit`
```

#### draft-spec-04-data-access.md (se aplicavel)

```markdown
# Draft -- SPEC-04 Data Access (<feature-slug>)

Inferido a partir dos campos visiveis no prototipo (sem dados reais no source -- BE
planejado conforme `MAPEAMENTO_DADOS_LEGADO.md` e `sql/01_schema_novo.sql`).

| Resource     | Endpoint base                          | Operations                       | Service                    | Facade                |
|--------------|----------------------------------------|----------------------------------|----------------------------|-----------------------|
| `<Resource>` | `/api/<microservico>/<resource>`       | list, getById, create, update    | `<Resource>ApiService`     | `<Resource>Facade`    |

Mapeamento campos visiveis -> DTO BE -> VM:
- `<campo prototipo>` -> `<dtoField>` (BE) -> `<vmField>` (camelCase, signals-friendly)
- Validacoes do form: <listar baseado nos campos required/pattern visiveis no prototipo>

Multi-empresa:
- `X-Empresa-Id` automatico via interceptor `@journeyos/shared/access-http-base`
- Endpoint NAO precisa receber `empresaId` no path (BE le do header)
```

---

## NAO fazer

- nao gerar codigo TypeScript / Angular / SCSS final
- nao criar issues (responsabilidade do `backlog`)
- nao tocar em `frontend/apps/` ou `frontend/libs/` (so escrever em `docs/architecture/frontend/prototypes/`)
- nao migrar shell do deck (`sidebar.jsx`, `app.jsx`, `MadeiraERP Prototype.html`) -- shell sera projeto separado
- nao analisar arquivos fora do `--source=`
- nao tentar mapear `tweaks-panel.jsx` -- ferramenta exclusiva do deck

---

## Saida final obrigatoria

```
Prototype analysis gerado para <MODULO>/<feature-slug>

Padrao identificado: <P1..P7>
Source: <path em prototipo/prototype/...>

Arquivos criados:
- docs/architecture/frontend/prototypes/<modulo>/<feature-slug>/analysis.md
- docs/architecture/frontend/prototypes/<modulo>/<feature-slug>/component-map.md
- docs/architecture/frontend/prototypes/<modulo>/<feature-slug>/draft-spec-02-component-hierarchy.md
- docs/architecture/frontend/prototypes/<modulo>/<feature-slug>/draft-spec-04-data-access.md (se aplicavel)
- docs/architecture/frontend/prototypes/<modulo>/<feature-slug>/raw/* (copia auditavel)

Estatisticas:
  ADAPTAR: <N1> | MIGRAR: <N2> | DESCARTAR: <N3>

Proxima acao:
-> /fe-feature-architect-discover <MODULO> <feature-slug> --from-prototype
```
