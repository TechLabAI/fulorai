# 06 — Risks, Gaps, Assumptions — ASST · Frontend

## 1. Riscos

| # | Risco | Impacto | Mitigação |
|---|---|---|---|
| R-1 | **Contrato BE instável** (`/api/v1/assets/**` ainda em specs; OpenAPI não materializado) | Alto — bloqueia `data-access` | Gerar `data-access` a partir do contrato BE no SPEC; `contracts/backend-api-cross-link.md` rastreia a fonte (`asst-service/contracts/api-contract.md`). |
| R-2 | **Vazamento cross-empresa no catálogo** ao trocar de empresa | Crítico (LGPD) | `EmpresaContextService.switchTo` cancela in-flight + invalida catálogo/detalhe antes de renderizar (ADR-005 multi-empresa); teste e2e dedicado. |
| R-3 | **Asset Studio: latência/timeout da IA** (composição pode demorar; `503` quando indisponível) | Médio (UX) | Estado `composing` com loading explícito + timeout; `503 ia-indisponivel` → degradação graciosa, nunca bloqueia CRUD/aprovação (ADR-005 Asset Studio). |
| R-4 | **Ações de workflow fora de estado** (UI oferece transição inválida) | Médio | Botões derivam do estado atual (UINV-5); BE é autoridade (`409 transicao-invalida`); e2e cobre cada transição. |
| R-5 | **Conteúdo de versão heterogêneo** por `tipoAsset` (e-mail ≠ landing ≠ roteiro) | Médio | MVP edita conteúdo estruturado/texto simples; renderização específica por tipo fica para SPEC/implement; rich-text é out-of-scope. |
| R-6 | **Modelagem de binário por URL** (sem upload) confunde usuário acostumado a anexar arquivo | Baixo/Médio (UX) | Deixar explícito na UI ("referência por URL"); upload é roadmap pós-MVP (ver Gaps). |
| R-7 | **Acoplamento acidental** a outro módulo de domínio (ex.: COMM querer importar tipos ASST) | Alto (drift) | `@nx/enforce-module-boundaries` bloqueia PR; ASST só importa `scope:asst` + `scope:shared`; consumo cross-módulo é via BE. |
| R-8 | **Bundle size** de features pesadas (catálogo + studio + aprovação) | Médio | Lazy por feature (`loadComponent`); evitar barrels que arrastam grafo. |

## 2. Gaps Conhecidos

- `integrations/techlab-ai/openapi.json` ainda **vazio** (P3 pendente do sync upstream) — não bloqueia
  o FE diretamente (o FE chama o BE, não a TechLab AI), mas os campos exatos de `/studio/compose`
  podem refinar no SPEC quando o contrato BE estabilizar.
- OpenAPI do próprio `asst-service` ainda não materializado para gerar `data-access` tipado.
- **Upload de binário** está fora do MVP (referência por URL). Quando entrar no roadmap, exigirá ADR
  próprio (chunked-upload, object storage S3, progress UX) — o master plan pré-brief já antecipava
  isso como `feature-asset-upload`/`chunked-upload-strategy`, agora deferido para pós-MVP.
- Patterns shared (`smart-table`, `approval-widget`, `timeline`) ainda não confirmados como libs
  `@journeyos/shared/*` — se ausentes, ASST hospeda em `libs/asst/ui` e promove depois.
- Estratégia de i18n ainda não fixada no Shell.

## 3. Suposições a Validar

- **A-1** Volume de assets por empresa é pequeno/médio (dezenas a baixas centenas) no MVP — virtual
  scroll/paginação server-side só se os dados provarem necessário.
- **A-2** A maioria das composições do Asset Studio completa em poucos segundos (síncrono com loading
  é aceitável); se a latência p95 for alta, reavaliar async/polling em ADR futuro.
- **A-3** Conteúdo de versão no MVP é texto/estruturado simples; editores ricos por tipo são pós-MVP.
- **A-4** Aprovação single-step atende o MVP (um aprovador `INFOPRODUTOR` por empresa).
- **A-5** Devices-alvo: desktop primeiro (operação de conteúdo); responsivo, não mobile-first no MVP.
- **A-6** Binários relevantes ao MVP são acessíveis por URL externa estável (Drive/Canva/etc.).

## 4. Dependências Críticas

- **BE `asst-service`**: endpoints de CRUD, versões (`/{id}/versoes`, `/{id}/published`), Asset Studio
  (`/{id}/studio/compose`), workflow (`/submit`, `/approve`, `/publish`), busca (`GET /?q=`), e os
  códigos de erro `asst.*` (`409`, `503`, `422`, `404`).
- **WRKS** (fundação): sessão/JWT + `AccessDecision` com permissões `asst.*` — precondição de UI.
- **Access Layer shared** (`auth-session`, `empresa-context`, `access-decision`, `access-http-base`)
  — precondição; já scaffolded na Wave 0 do master plan.
- **Design tokens** (`@journeyos/shared/ui-tokens`) — base visual.
- **Shell** (`journey-os-web`) — host lazy + registro do módulo (`@journeyos/asst`) + `NavigationService`.

---

## Referências

- `01..05` deste módulo · ADRs `adr/ADR-001..005`
- `docs/architecture/frontend/plans/architecture-master-plan.md` (Wave 1 / dependências)
- BE: `docs/architecture/backend/services/asst-service/06-risks-gaps-assumptions.md`
