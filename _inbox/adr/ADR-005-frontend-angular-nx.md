# ADR-005 — Frontend em Angular (monorepo Nx)

> **Data:** 2026-06-04
> **Status:** draft (BA)
> **Decisor:** Arquiteto (Danilo Amaral) + Designer — pendente de promoção

---

## Contexto

O Journey OS tem um wireframe rico (20+ telas: Dashboard, Leads, Journey
Builder, Automation Builder, Asset Studio, Copilot Chat, CRM, Analytics,
Importação — design/wireframe.md), com builders complexos em canvas full-width,
navegação contextual (Lead/Journey/Asset Context) e um AI Copilot acessível de
forma transversal. O frontend precisa: roteamento real com deep-link (compartilhar
"este lead"/"esta jornada"), modularização por feature para escalar das 34 telas
P0 até o produto completo, e estado global mínimo (workspace ativo, contexto do
Copilot).

O PRD original (§10) propunha **Next.js/React**; descartado (EXC-001) por
TECH-002, que impõe **Angular em monorepo Nx** (padrão do framework). A decisão é
documentar **por que** Angular/Nx serve ao Journey OS, não apenas que é o default.

---

## Opções consideradas

### Opção A — Angular Nx monorepo, multi-route SPA com feature libs (DECIDIDA)
- **Vantagens:**
  - Cada tela vira **page** em uma **feature lib** Nx; roteamento real e
    deep-link (`/leads/:id`, `/journeys/:id`); lazy loading por feature.
  - Boundaries Nx evitam acoplamento entre features (escala das 34 telas P0).
  - AI Copilot como componente do shell (fora do `<router-outlet>`), persistente
    e contextual à rota — diferencial central do produto (wireframe §AI Copilot).
  - Cumpre TECH-002; templates/scaffold Angular do framework prontos.
- **Desvantagens:**
  - Boilerplate inicial (rotas, lazy loaders, libs).
  - Curva de Nx (~1 semana) para devs novos.
- **Custo:** baixo — suportado nativamente pelo framework.

### Opção B — Next.js / React — stack do PRD §10
- **Vantagens:**
  - SSR/SEO de fábrica; ecossistema vasto; alinhado ao PRD original.
- **Desvantagens:**
  - Fora do framework `techlab-architecture` — sem templates/scaffold; retrabalho.
  - SEO/SSR irrelevante para app **interno multi-tenant** atrás de login (o
    Journey OS é cockpit operacional, não site público).
  - Viola TECH-002.
- **Custo:** alto (reescrever ferramental de frontend do framework) — EXC-001.

### Opção C — Angular monolito (sem Nx)
- **Vantagens:**
  - Setup mais simples no início.
- **Desvantagens:**
  - Não escala bem com 20+ features distintas; sem boundary enforcement.
  - Quebra alinhamento com o framework.
- **Custo:** médio (perde ferramental Nx).

---

## Decisão

Escolhida: **Opção A — Angular Nx monorepo, multi-route SPA com features
modulares**.

---

## Justificativa

1. **O produto é um cockpit operacional logado, não um site público.** SSR/SEO
   (vantagem do Next.js) não agregam; o que importa é deep-link, navegação
   client-side fluida e estado contextual — onde a SPA Angular com roteamento
   real entrega diretamente.

2. **AI Copilot transversal exige um shell persistente.** O Copilot e os
   contextos (Lead/Journey/Asset) precisam sobreviver à navegação. No shell
   Angular, o painel é montado uma vez fora do router-outlet e lê signal de
   contexto da rota ativa — sem forçar tela única.

3. **Modularização para escalar das 34 telas P0.** Nx feature libs + boundaries
   permitem crescer tela a tela sem acoplamento, essencial dado o tamanho do
   inventário (LBC §7.1) e o time enxuto (ORG-001).

4. **Cumpre TECH-002 com ferramental pronto** (gerador Angular/Nx do framework).

---

## Trade-offs aceitos

- **Perdemos:** SSR/SEO de fábrica do Next.js. Justificativa: app interno logado;
  irrelevante.
- **Perdemos:** a stack React do PRD §10 e a "transição direta do protótipo".
  Justificativa: o protótipo HTML é descartável (regra do framework); o produto é
  reimplementado a partir do wireframe persistente.
- **Perdemos:** simplicidade do monólito Angular. Justificativa: não escala para
  o nº de telas; Nx gera a estrutura, custo marginal baixo.

---

## Como reverter se a decisão se mostrar errada

**Para Angular monolito (sem Nx):** mover libs para dentro do app, remover Nx.
**Custo:** 1-2 semanas, perde boundary enforcement.

**Para React/Next.js:** reescrita do frontend + adaptar framework para suportar
React. **Custo:** 3-6 meses, alto risco. Como ainda **não há frontend de
produção** (Estágio 0), reverter hoje é barato; o custo cresce a cada feature lib
implementada.

---

## Sinais que indicariam que está errada

- Bundle inicial degradando UX (>5MB mesmo com lazy loading).
- Time com dificuldade crônica em manter boundaries entre features.
- Surgir requisito forte de SSR/SEO (ex.: páginas públicas) que o Funnel Builder
  (V2) traria — reavaliar então, não no MVP.

---

## Consequências

- **Em código:** Nx monorepo Angular; feature lib por tela/agrupamento; shared-ui,
  shared-data, shared-state; `npmScope = @journeyos`; AI Copilot no shell.
- **Em deploy:** SPA com bundles por rota (lazy loading); deploy estático.
- **Em time:** dev frontend precisa de Nx + signals + lazy routing.

---

## Referências

- LBC §7.1 (34 telas P0), §5.3 (Copilot diferencial)
- Framing §5.1 (Experience Layer Angular Nx), §11 (stack, npmScope)
- Constraints: TECH-002, EXC-001, ORG-001
- design/wireframe.md (telas, shell, AI Copilot transversal); design/ui-concept.md
- ADRs relacionados: ADR-002 (Copilot consumido pelo frontend)
