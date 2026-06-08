# 06 — Risks, Gaps, Assumptions — WRKS · Frontend

## 1. Riscos

| # | Risco | Impacto | Mitigação |
|---|---|---|---|
| R-1 | **Contrato BE instável** (endpoints IAM/workspace ainda em specs) | Alto — bloqueia data-access | Gerar `data-access` a partir do contrato BE no SPEC; `contracts/backend-api-cross-link.md` rastreia a fonte. |
| R-2 | **Vazamento cross-empresa na UI** ao trocar de empresa | Crítico (LGPD) | `EmpresaContextService.switchTo` cancela in-flight + invalida cache antes de renderizar (ADR-005); teste e2e dedicado. |
| R-3 | **Race no callback OIDC** (tela protegida pisca antes da sessão resolver) | Médio (UX/segurança) | Guard de rota + estado `exchanging`; nada protegido renderiza até `authenticated`. |
| R-4 | **RBAC desatualizado em tela** após mudança de papel no BE | Médio | Consumir `modelo_acesso_versao` da AccessDecision; re-derivar navegação ao detectar bump. |
| R-5 | **Bundle size** do módulo fundação (carrega cedo) | Médio | Lazy por feature (`loadComponent`); evitar barrels que arrastam grafo (nx-boundaries). |
| R-6 | **Acoplamento acidental** a outro módulo de domínio | Alto (drift) | `@nx/enforce-module-boundaries` bloqueia PR; WRKS só importa `scope:wrks` + `scope:shared`. |

## 2. Gaps Conhecidos

- `integrations/techlab-ai/openapi.json` vazio — **não afeta WRKS** (sem IA), mas o contrato do
  próprio `wrks-service` (OpenAPI) ainda não foi materializado para gerar `data-access`.
- Toolchain Nx/CLI: scaffold (A4) depende do plugin `@journeyos/internal:module` / generators Nx estarem
  disponíveis no workspace — a verificar antes do A4 (ver memória `[[gradle-toolchain-absent]]` —
  análoga para FE).
- Wireframes/frontend-reference existem fora do repo (`techlab-ba/.../design/frontend-reference`,
  32 telas) — não versionados aqui; as telas de admin WRKS precisam ser mapeadas no SPEC.
- Estratégia de i18n ainda não fixada no Shell.

## 3. Suposições a Validar

- **A-1** A maioria dos usuários opera **1 empresa** (auto-skip da seleção é o caminho comum).
- **A-2** Tabela de usuários por empresa é pequena/média (dezenas) no MVP — virtual scroll só se
  os dados provarem o contrário.
- **A-3** Papéis são fixos canônicos (sem editor) — confirmado pelo brief BE; revisar se o produto
  pedir papéis por empresa.
- **A-4** Devices-alvo: desktop primeiro (operação/admin); responsivo, mas não mobile-first no MVP.
- **A-5** Troca de empresa é relativamente rara por sessão (não é hot path de performance extrema).

## 4. Dependências Críticas

- **BE `wrks-service`**: endpoints de login/callback, lista de empresas, `switchTo`, usuários
  (CRUD + convite + papel), workspace settings, `POST /access/evaluate`, RBAC (papéis×permissões).
- **Access Layer shared** (`auth-session`, `empresa-context`, `access-decision`, `access-http-base`)
  — precondição; precisa estar scaffolded antes do WRKS (ver master plan, Wave 0).
- **Design tokens** (`@journeyos/shared/ui-tokens`) — base visual das telas de admin.
- **Shell** (`journey-os-web`) — host lazy + topbar de troca de empresa + `NavigationService`.

---

## Referências

- `01..05` deste módulo · ADRs `adr/ADR-001..005`
- `docs/architecture/frontend/plans/architecture-master-plan.md` (Wave 0 / dependências)
- BE: `docs/architecture/backend/services/wrks-service/06-risks-gaps-assumptions.md`
