# 06 — Risks, Gaps and Assumptions — SALE · Frontend

## 1. Riscos

| # | Risco | Impacto | Mitigação |
|---|---|---|---|
| R1 | **Drag-and-drop inconsistente** (card "preso" na coluna errada quando o `PATCH` falha sem rollback). | Confiança no pipeline / dados | Optimistic move **com rollback obrigatório** (ADR-005); estado de "moving" por card; e2e `pipeline-drag-rollback` cobrindo `409 ja-fechada` e falha de rede. |
| R2 | **Performance do Kanban com muitos cards** (pipelines com centenas de oportunidades por coluna). | TTI/INP do board | Virtual scroll por coluna (CDK), colunas com paginação/lazy de cards, card leve; `GET /oportunidades` paginado/filtrado server-side. |
| R3 | **Bundle size do módulo** (CDK DragDrop + chart de funil + 6 features). | TTI | Lazy por rota (`loadComponent`); chart de funil leve (SVG/CSS próprio) ou import dinâmico; CDK DragDrop só no `feature-pipeline`; orçamento de bundle por feature no SPEC. |
| R4 | **Atribuição lida como caixa-preta** (UI mostrando só o total atribuído). | Confiança / valor p/ growth | Breakdown por touchpoint + versão de modelo **sempre** visível (ADR-005); conservação de receita verificada na UI; e2e `attribution-breakdown-explainable`. |
| R5 | **Compra confirmada parece "criável" pela UI** (expectativa de tela de registro). | Escopo/UX | Deixar explícito que a ingestão é **server-to-server** — a UI só consulta + estorna/cancela; nenhum botão "registrar compra" no FE no MVP. |
| R6 | **Contratos BE instáveis** (campos de breakdown/estágios/estado podem mudar). | Retrabalho | Tipos derivados de `@journeyos/shared/contracts` (OpenAPI) quando expostos; cross-link BE↔FE no SPEC; adaptador no `data-access` isola mudanças. |
| R7 | **Efeitos colaterais não refletidos** (ativar modelo re-atribui afetadas; estorno recalcula LTV) sem feedback claro. | UX/correção percebida | Após ativar/estornar, refetch + indicação de "re-atribuição/recálculo em andamento"; versão ativa destacada; não usar optimistic nessas ações. |
| R8 | **Vazamento cross-empresa** ao trocar de empresa sem invalidar estado. | Isolamento/LGPD | Effect que limpa board/seleção/listas na troca de empresa antes de novo fetch; e2e `empresa-switch-isolation`. |
| R9 | **LGPD na compra** (PII do comprador exposta / ajuste destrutivo acidental). | Compliance/dados | `base_legal`/consentimento visíveis no detalhe; estornar/cancelar exigem confirmação + permissão; histórico append-only (nunca apagar). |

## 2. Gaps Conhecidos

- **`@journeyos/shared/contracts` (OpenAPI do SALE) ainda não publicado** → tipos de VM provisórios no
  `data-access` até o BE expor o contrato (alinhar no A2/specs).
- **Patterns shared `smart-table` / `timeline` / `kanban-board` podem não existir** → começam em
  `libs/sale/ui` e são candidatos a promoção (asset-driven-ui). O **kanban-board com CDK DragDrop** é
  novo no monorepo — avaliar promoção a shared se JRNY/outros precisarem de board.
- **Estágios do pipeline são configuráveis** (`NOVA/CONTATO/PROPOSTA/GANHA/PERDIDA` é exemplo) →
  confirmar se as colunas vêm do BE (config por empresa) ou são fixas no MVP, antes do scaffold.
- **Funil de receita/LTV** depende de agregações Elastic (`revenue-events`/`campaign-events`) que o BE
  pode ainda não expor como endpoint dedicado → no MVP pode derivar de `GET /ltv` + agregação de
  `GET /compras`; confirmar no A2.
- **`contatoRef`** (identificador do comprador na compra/LTV) — formato e ligação com `lead`/contato a
  confirmar no contrato BE (afeta navegação compra ↔ lead, que é cross-módulo via API).

## 3. Suposições a Validar

- Volume típico de oportunidades por pipeline/coluna no MVP (dezenas a centenas?) → dimensiona virtual
  scroll/paginação por coluna no Kanban.
- Frequência de uso do pipeline (SDR usa muitas vezes ao dia) → justifica o Kanban como rota default do módulo.
- Devices alvo majoritariamente desktop (operação de closer/growth) → layout do Kanban otimizado para
  desktop; drag-and-drop touch é nice-to-have, não requisito MVP.
- O **histórico de estágio** vem **completo** em `GET /oportunidades/{id}` (não exige chamada extra).
- O **breakdown de atribuição** vem completo em `GET /compras/{id}` (e/ou `GET /compras/{id}/atribuicao`),
  com a `versaoModelo` como campo de primeira classe (não inferido pelo FE).
- O FE **nunca** precisa registrar compra (ingestão 100% server-to-server no MVP).

## 4. Dependências Críticas

- **BE `sale-service`**: `/oportunidades/**`, `/ofertas`, `/compras`, `/atribuicao`, `/ltv` + histórico
  de estágio + breakdown de atribuição + funil/LTV.
- **WRKS** (via Access Layer): sessão/JWT, empresa ativa, `AccessDecision` para `sale.*`.
- **LEAD / INTL** (soft, **só via API BE**): a oportunidade nasce de `lead.qualificado` (não pela UI);
  analytics de receita pode apoiar-se em INTL — **sem** import `scope:lead`/`scope:intl` no FE.
- **`@angular/cdk/drag-drop`**: base do Kanban (ADR-005).
- **Shared libs**: `access-http-base`, `auth-session`, `empresa-context`, `access-decision`,
  `ui-tokens/ui-components/ui-feedback`, `error-model`, `observability`.
- **Shell `journey-os-web`**: registro do `SALE_MODULE_DESCRIPTOR` (deferido para o implement P1, como
  nos demais módulos).
- **Design tokens** (`@journeyos/shared/ui-tokens`): paleta acessível para estágios/origens/moeda.

---

## Referências

- `01-architectural-vision.md` · `04-frontend-architecture-direction.md` · `05-state-and-data-flow.md`
- ADR-005 (Kanban + optimistic move) · BE `contracts/api-contract.md`
