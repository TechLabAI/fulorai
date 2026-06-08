# 02 — Architecture Blueprint — SALE · Frontend

> Fronteiras de sistema, atores, fluxos golden-path e fronteiras internas de libs (module-pattern).

## 1. System Boundary

O FE SALE é um **cliente do API gateway** via `@journeyos/shared/access-http-base`. Toda chamada vai
para `/api/v1/oportunidades/**`, `/api/v1/ofertas`, `/api/v1/compras`, `/api/v1/atribuicao`,
`/api/v1/ltv` do `sale-service`, com `Authorization` (bearer JWT do WRKS), `X-Empresa-Id` e
`X-Correlation-Id` injetados pelos interceptors da Access Layer. **Sem** chamadas diretas a sistemas
legados, a gateway de pagamento ou a provider de IA — **não há IA no MVP** e a **ingestão de compras é
server-to-server** (checkout/gateway via GWY/integração com service token), nunca disparada pelo FE.

## 2. External Actors and Systems

- **Browser autenticado** (sessão via WRKS/`auth-session`); usuário com papel `SDR`, `INFOPRODUTOR`
  ou `HEAD_GROWTH`.
- **`sale-service`** (BE) através de `@journeyos/shared/access-http-base` — única fonte de dados.
- **Shell `journey-os-web`** — hospeda o módulo lazy e fornece contexto de empresa/sessão/RBAC.
- **Checkout/gateway externo** (Hotmart, link de pagamento) — **invisível ao FE**; a compra confirmada
  entra no BE de forma idempotente (server-to-server). A UI só **consulta** a compra resultante.
- **TechLab AI** — **não usada no MVP** (atribuição e LTV são determinísticos). Sem badge de assist.
- **Sem** widgets 3rd-party no MVP.

## 3. End-to-End User Flows (golden path)

**Golden path — "avançar uma oportunidade até a compra confirmada":**

```
[Pipeline — Kanban]                                    [Detalhe da oportunidade]
+-----------+-----------+-----------+-----------+      +-----------------------------------+
|   NOVA    |  CONTATO  | PROPOSTA  |   GANHA   |      | Acme Curso Pro   R$ 1.997  78%    |
|-----------|-----------|-----------|-----------|      | lead: Ana Souza  resp: Lucas      |
| [Ana 1.9k]| [Bruno 3k]| [Carla 5k]|           | -->  |-----------------------------------|
| [Davi 990]|           |           |           |abre  |  Histórico de estágio             |
|           |  ↑ drag   |           |           |      |   NOVA → CONTATO → PROPOSTA       |
|           |  Carla →  |  GANHA    |           |      |  [Ganhar]  [Perder (motivo*)]     |
+-----------+-----------+-----------+-----------+      +-----------------------------------+
   drag move estágio (optimistic + rollback)              ganhar → compra confirmada (S2S)
                                                              → receita atribuída → LTV ↑
```

**Alternativas / edge cases:**

- **Mover deal já fechado** → drag rejeitado pelo BE (`409 sale.oportunidade.ja-fechada`); o card
  **volta** para a coluna de origem (rollback) + aviso. Sem estado inconsistente na tela.
- **Perder sem motivo** → ação bloqueada com erro de formulário (espelha `422
  sale.oportunidade.motivo-obrigatorio`); só conclui com motivo.
- **Compra duplicada** (mesmo `id_externo`+`origem`, fora da UI) → a ingestão é idempotente no BE
  (`duplicada=true`); a UI nunca cria duplicado e a lista de compras mostra uma única.
- **Editar oferta** → cria **nova versão**; as versões anteriores permanecem imutáveis e listáveis.
- **Ativar modelo de atribuição** → desativa a versão anterior atomicamente e **re-atribui** as
  compras afetadas (BE); a UI destaca a versão ativa e reflete os breakdowns recalculados.
- **Estornar/cancelar compra** → ajusta a receita reconhecida + recalcula LTV no BE; o **histórico
  nunca é apagado** (a compra muda de status, não some).
- **Troca de empresa** → pipeline/listas em tela são invalidados antes de carregar os da nova empresa.
- **Sem permissão** (`accessGuard` nega) → tela de "acesso negado" do Shell; item de menu oculto via
  `NavigationService`.

**Fluxos de gestão (Marina/Rafael):**

- *Atribuição*: `/sale/atribuicao` → listar versões → criar versão (inativa) → **ativar** → re-atribuição
  de afetadas (BE) → abrir compra → ver breakdown por touchpoint.
- *Oferta*: `/sale/ofertas` → criar/editar (nova versão) → desativar.
- *Receita*: `/sale/receita` → funil por origem/período + LTV dos top contatos (read-only).

## 4. Internal Boundaries (estrutura de libs — module-pattern)

```
apps/sale/                                  # host fino lazy (type:app, scope:sale)
libs/sale/
+-- shell-entry/        (type:app)          # entry como library @journeyos/sale (ADR-003/004):
|                                           #   contract, routes, bootstrap, permission-map,
|                                           #   feature-flags, nav.config, descriptor
+-- feature-pipeline/   (type:feature)      # Kanban de oportunidades por estágio + drag move (ADR-005)
+-- feature-opportunity/(type:feature)      # detalhe + histórico de estágio + ganhar/perder
+-- feature-offer/      (type:feature)      # catálogo de ofertas versionadas (CRUD + desativar)
+-- feature-purchase/   (type:feature)      # lista/detalhe de compras + breakdown + estornar/cancelar
+-- feature-attribution/(type:feature)      # versões de modelo + ativar + breakdown de uma compra
+-- feature-revenue-dashboard/(type:feature)# funil de receita por origem/período + LTV (read-only)
+-- data-access/        (type:data-access)  # OportunidadeApiService, OfertaApiService, CompraApiService,
|                                           #   AtribuicaoApiService, LtvApiService + facades de signal
+-- access/             (type:domain)       # guards específicos (ex.: saleDataScopeGuard)
+-- integration/        (type:domain)       # SaleShellIntegrationService
+-- navigation/         (type:domain)       # breadcrumb/menu state
+-- ui/                 (type:ui)           # kanban-board, kanban-column, opportunity-card,
|                                           #   stage-history-timeline, attribution-breakdown,
|                                           #   revenue-funnel-chart, ltv-table (promovíveis a shared)
+-- styles/             (type:ui)           # SCSS isolado (consome @journeyos/shared/ui-tokens)
```

Direções permitidas (nx-boundaries): `feature → data-access | ui | access | shared/*`;
`data-access → shared/{contracts,access-http-base,empresa-context,error-model}`;
`access → shared/{access-decision,auth-session}`. **Proibido** importar `scope:<outro-módulo>` —
SALE lê LEAD/INTL **só via API BE** (nunca `scope:lead`/`scope:intl`).

## 5. Cross-cutting Concerns

- **Auth/entitlement** — `authGuard` + `empresaGuard` + `accessGuard('sale.*')` via
  `AccessDecisionService`; visibilidade de menu/ações via `NavigationService` + `computed()` de permissão
  (ex.: ganhar/perder gated por `sale.oportunidade.fechar`; ativar modelo por `sale.atribuicao.ativar`).
- **Observability** — `@journeyos/shared/observability`: latência do Kanban, tempo até ganho/perda,
  taxa de estorno/cancelamento, latência das consultas de receita; erros por código.
- **Design tokens** — `@journeyos/shared/ui-tokens`; cores de estágio/origem com contraste acessível
  (estágio/origem não podem depender só de cor — usar rótulo + valor).
- **i18n** — `pt-BR` como locale humano primário (estágios, estados, moeda `BRL`, base legal); textos
  técnicos/erros mapeados de `error.code` via `error-model`. Valores monetários formatados por locale.
- **LGPD** — `compra` carrega PII do comprador (`contatoRef`); `base_legal`/consentimento sempre visível
  no detalhe; ações de ajuste (estornar/cancelar) gated + confirmação explícita.

---

## Referências

- `01-architectural-vision.md` · `03-domain-framing-frontend.md` · `04-frontend-architecture-direction.md`
- BE: `docs/architecture/backend/services/sale-service/contracts/api-contract.md`
- `docs/architecture/frontend/standards/nx-boundaries.md` · `access-layer-contracts.md`
