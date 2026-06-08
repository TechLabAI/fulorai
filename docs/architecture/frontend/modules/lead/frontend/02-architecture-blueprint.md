# 02 — Architecture Blueprint — LEAD · Frontend

> Fronteiras de sistema, atores, fluxos golden-path e fronteiras internas de libs (module-pattern).

## 1. System Boundary

O FE LEAD é um **cliente do API gateway** via `@journeyos/shared/access-http-base`. Toda chamada vai
para `/api/v1/leads/**`, `/api/v1/surveys`, `/api/v1/qualification`, `/api/v1/segments` do
`lead-service`, com `Authorization` (bearer JWT do WRKS), `X-Empresa-Id` e `X-Correlation-Id`
injetados pelos interceptors da Access Layer. **Sem** chamadas diretas a sistemas legados, a provider
de IA ou à TechLab AI — o assist de qualificação é resolvido **inteiramente pelo BE**.

## 2. External Actors and Systems

- **Browser autenticado** (sessão via WRKS/`auth-session`); usuário com papel `HEAD_GROWTH`, `SDR`
  ou `INFOPRODUTOR`.
- **`lead-service`** (BE) através de `@journeyos/shared/access-http-base` — única fonte de dados.
- **Shell `journey-os-web`** — hospeda o módulo lazy e fornece contexto de empresa/sessão/RBAC.
- **TechLab AI** — **invisível ao FE**; atua apenas dentro do BE (capacidade `qualification`). A UI
  só observa o efeito (`assist_ia=true|false`).
- **Sem** widgets 3rd-party no MVP.

## 3. End-to-End User Flows (golden path)

**Golden path — "entender e agir sobre um lead qualificado":**

```
[Fila priorizada]                         [Detalhe do lead]
+-------------------------------+         +-----------------------------------+
| Leads (ordenados por score)   |         | Ana Souza   score 82  [IA ✓]      |
| filtro: [segmento ▾][estado ▾]| --abre> | estado: EM_QUALIFICACAO           |
|-------------------------------|         |-----------------------------------|
| �* Ana Souza      82  Quente   |         |  Maturity Score (6D)              |
|   Bruno Lima      67  Morno    |         |     PERFIL      ███████░  78      |
|   Carla Dias      54  Morno    |         |     ENGAJAMENTO ████░░░░  41      |
|   ...                          |         |     INTENCAO    ████████  90      |
|   [paginação]                  |         |     CAPACIDADE  ██████░░  64      |
+-------------------------------+         |     URGENCIA    ███████░  75      |
                                          |     ADERENCIA   █████░░░  55      |
                                          |  regra v7 · assist IA: sim        |
                                          |  [Editar perfil][Requalificar]    |
                                          |  [Anonimizar][Expurgar]           |
                                          +-----------------------------------+
```

**Alternativas / edge cases:**

- **IA indisponível** → o detalhe mostra o score com badge **"score determinístico"** (sem `[IA ✓]`);
  nenhuma quebra. Espelha `lead.ia.indisponivel` (não é erro HTTP).
- **Sem regra ativa** → ação "Requalificar" desabilitada com aviso (espelha `409
  lead.qualification.sem-regra-ativa`); a fila ainda lista leads já pontuados.
- **Lead `ANONIMIZADO`** → PII suprimida, edição/qualify desabilitados; só leitura agregada.
- **Troca de empresa** → fila/segmentos em tela são invalidados antes de carregar os da nova empresa.
- **Sem permissão** (`accessGuard` nega) → tela de "acesso negado" do Shell; item de menu oculto via
  `NavigationService`.
- **Captura duplicada** (fora da UI, via integração) → ao reabrir, o lead aparece único com merge;
  a UI nunca cria duplicado.

**Fluxos de gestão (Marina):**

- *Segmento*: `/lead/segments` → criar/editar predicado → prévia de contagem → salvar → navegar à fila
  do segmento.
- *Regra*: `/lead/qualification` → criar versão (inativa) → **ativar** → recálculo de afetados (BE).
- *Survey*: `/lead/surveys` → definir survey/perguntas; responder por lead atualiza perfil.

## 4. Internal Boundaries (estrutura de libs — module-pattern)

```
apps/lead/                                  # host fino lazy (type:app, scope:lead)
libs/lead/
+-- shell-entry/        (type:domain)       # entry como library @journeyos/lead (ADR-003/004):
|                                           #   contract, routes, bootstrap, permission-map,
|                                           #   feature-flags, nav.config, descriptor
+-- feature-lead-list/  (type:feature)      # fila priorizada + filtros + busca + paginação
+-- feature-lead-detail/(type:feature)      # perfil + breakdown 6D + ações LGPD/qualify
+-- feature-maturity-score/(type:feature)   # radar 6D + dashboard de distribuição/saúde da base
+-- feature-segmentation/(type:feature)     # CRUD de segmentos + prévia de contagem
+-- feature-survey/     (type:feature)      # definição de survey/perguntas + captura de respostas
+-- feature-qualification-rules/(type:feature) # versões de regra + ativação + recálculo
+-- data-access/        (type:data-access)  # LeadApiService, SurveyApiService, QualificationApiService,
|                                           #   SegmentApiService + facades de signal
+-- access/             (type:domain)       # guards específicos do módulo (ex.: leadDataScopeGuard)
+-- integration/        (type:domain)       # LeadShellIntegrationService
+-- navigation/         (type:domain)       # breadcrumb/menu state
+-- ui/                 (type:ui)           # score-radar, dimension-bar, score-badge, lead-state-chip,
|                                           #   maturity-distribution-chart (opcional → promovível a shared)
+-- styles/             (type:ui)           # SCSS isolado (consome @journeyos/shared/ui-tokens)
```

Direções permitidas (nx-boundaries): `feature → data-access | ui | access | shared/*`;
`data-access → shared/{contracts,access-http-base,empresa-context,error-model}`;
`access → shared/{access-decision,auth-session}`. **Proibido** importar `scope:<outro-módulo>`.

## 5. Cross-cutting Concerns

- **Auth/entitlement** — `authGuard` + `empresaGuard` + `accessGuard('lead.*')` via
  `AccessDecisionService`; visibilidade de menu/ações via `NavigationService` + `computed()` de permissão.
- **Observability** — `@journeyos/shared/observability`: latência da fila, tempo até `qualify`, taxa de
  uso de assist IA, erros por código.
- **Design tokens** — `@journeyos/shared/ui-tokens`; cores das dimensões/score com contraste acessível
  (a faixa de score não pode depender só de cor — usar rótulo + número).
- **i18n** — `pt-BR` como locale humano primário (labels de dimensão, estados, base legal); textos
  técnicos/erros mapeados de `error.code` via `error-model`.
- **LGPD** — base legal/consentimento sempre visíveis no detalhe; PII suprimida quando `ANONIMIZADO`.

---

## Referências

- `01-architectural-vision.md` · `03-domain-framing-frontend.md` · `04-frontend-architecture-direction.md`
- BE: `docs/architecture/backend/services/lead-service/contracts/api-contract.md`
- `docs/architecture/frontend/standards/nx-boundaries.md` · `access-layer-contracts.md`
