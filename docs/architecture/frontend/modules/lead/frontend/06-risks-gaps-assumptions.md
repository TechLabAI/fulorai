# 06 — Risks, Gaps and Assumptions — LEAD · Frontend

## 1. Riscos

| # | Risco | Impacto | Mitigação |
|---|---|---|---|
| R1 | **Score determinístico (assist IA off) lido como erro/score "pior".** A UI pode dar a impressão de degradação de qualidade quando a IA cai. | Confiança no produto | Badge neutro **"score determinístico"** (não vermelho/erro); copy explicativa; nunca toast de erro para `lead.ia.indisponivel`. Concentrar verificação no e2e `maturity-score-degradation`. |
| R2 | **Performance de listas grandes** (bases com dezenas de milhares de leads). | TTI/INP da fila | Paginação server-side (Elastic), virtual scroll na tabela, colunas mínimas na fila; detalhe carrega breakdown sob demanda. |
| R3 | **Bundle size do módulo** (radar/chart + 6 features). | TTI | Lazy por rota (`loadComponent`); chart/radar como componente leve (sem libs de chart pesadas se evitável) ou import dinâmico; orçamento de bundle por feature no SPEC. |
| R4 | **Acessibilidade do Maturity Score** (cor como único canal). | A11y/compliance | Rótulo textual + número sempre presentes; contraste AA; radar com tabela alternativa (screen reader). |
| R5 | **Contratos BE instáveis** (campos do breakdown/`assistIa`/dimensões podem mudar). | Retrabalho | Tipos derivados de `@journeyos/shared/contracts` (OpenAPI) quando expostos; cross-link BE↔FE no SPEC; adaptador no `data-access` isola mudanças. |
| R6 | **Semântica do predicado de segmento** (validação client vs server divergente). | UX de erro | Validação client-side só de forma; veredito final do BE (`422 predicado-invalido`) mapeado ao campo; não inventar gramática própria. |
| R7 | **LGPD na UI** (PII exposta após anonimização, ou ação destrutiva acidental). | Compliance/dados | PII suprimida quando `ANONIMIZADO`; expurgo/anonimização exigem confirmação explícita + permissão; e2e cobrindo o trava-edição. |
| R8 | **Vazamento cross-empresa** ao trocar de empresa sem invalidar estado. | Isolamento/LGPD | Effect que limpa fila/seleção na troca de empresa antes de novo fetch; e2e `empresa-switch-isolation`. |

## 2. Gaps Conhecidos

- **`@journeyos/shared/contracts` (OpenAPI do LEAD) ainda não publicado** → tipos de VM provisórios no
  `data-access` até o BE expor o contrato (alinhar no A2/specs).
- **Patterns shared `smart-table` / `chart-radar` podem não existir** → começam em `libs/lead/ui` e são
  candidatos a promoção (asset-driven-ui).
- **Dimensões 6D são "propostas a validar"** no brief BE (`PERFIL/ENGAJAMENTO/INTENCAO/CAPACIDADE/
  URGENCIA/ADERENCIA`) — confirmar os rótulos finais no SPEC contra o `lead-service` antes do scaffold.
- **Distribuição/dashboard** depende de agregações que o BE pode ainda não expor como endpoint dedicado
  → no MVP pode derivar do `GET /leads` paginado/facetado; confirmar no A2.

## 3. Suposições a Validar

- Volume típico de leads por empresa no MVP (centenas a dezenas de milhares?) → dimensiona paginação/virtual scroll.
- Frequência de uso da fila (SDR usa muitas vezes ao dia) → justifica a fila como rota default do módulo.
- Devices alvo majoritariamente desktop (operação de growth/SDR) → layout otimizado para desktop, responsivo mínimo.
- O breakdown 6D vem **completo** em `GET /leads/{id}` (não exige chamada extra por dimensão).
- `assistIa` é um campo de primeira classe na resposta do score (não inferido pelo FE).

## 4. Dependências Críticas

- **BE `lead-service`**: `/leads/**`, `/surveys`, `/qualification`, `/segments` + breakdown 6D + `assistIa`.
- **WRKS** (via Access Layer): sessão/JWT, empresa ativa, `AccessDecision` para `lead.*`.
- **Shared libs**: `access-http-base`, `auth-session`, `empresa-context`, `access-decision`,
  `ui-tokens/ui-components/ui-feedback`, `error-model`, `observability`.
- **Shell `journey-os-web`**: registro do `LEAD_MODULE_DESCRIPTOR` (deferido para o implement P1, como nos demais módulos).
- **Design tokens** (`@journeyos/shared/ui-tokens`): paleta acessível para faixas de score/dimensões.

---

## Referências

- `01-architectural-vision.md` · `04-frontend-architecture-direction.md` · `05-state-and-data-flow.md`
- ADR-005 (visualização do Maturity Score) · BE `contracts/api-contract.md`
