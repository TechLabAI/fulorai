# Brief — WRKS (Workspace & Identity)

> Fonte estruturada para `/be-architect-specs`, `/be-architect-backlog` e `/be-architect-scaffold`.
> Módulo de **fundação** (`type: standard`) — dono da identidade, RBAC e multi-tenancy do Journey OS.

| # | Item | Conteúdo |
|---|------|----------|
| 1 | **Nome canônico / Prefixo** | `wrks-service` / **WRKS** · pacote `com.journeyos.wrks` · Gradle `:services:wrks-service` |
| 2 | **Problema que resolve** | O Journey OS precisa de **uma única autoridade** sobre *quem pode fazer o quê, em qual workspace*. WRKS é a fundação da plataforma: é dono dos **tenants** (`empresa` / workspace), da estrutura organizacional interna (business units, teams), dos **usuários**, do modelo **RBAC canônico** (papéis, permissões) e da **identidade/sessão** (login via Keycloak OIDC, emissão de JWT, avaliação de acesso). Sem WRKS nenhum outro módulo consegue isolar dados por empresa nem aplicar autorização. |
| 3 | **Persona principal / secundária** | **Principal:** `INFOPRODUTOR` (Rafael, CEO da operação) — administra o workspace, convida a equipe, atribui papéis, configura a empresa. **Secundária:** `HEAD_GROWTH` (Marina) — gerencia sua equipe dentro de uma business unit. **Persona-máquina:** GWY (API Gateway) e **todos** os demais serviços de negócio, que dependem de WRKS para `AccessDecision` + contexto de tenant. |
| 4 | **Recorte do MVP (in)** | (a) **Workspace/empresa**: CRUD em `journeyos_global.empresa` + gatilho de provisionamento de schema (`emp_<slug>`); (b) **Org structure**: business units + teams (hierarquia dentro da empresa); (c) **Usuários**: `usuario` + associação `usuario_empresa` (com papel + data_scope); (d) **RBAC**: `papel`, `permissao`, `papel_permissao`, seed dos papéis canônicos (`INFOPRODUTOR`/`HEAD_GROWTH`/`SDR`), `modelo_acesso_versao` (cache busting); (e) **Identidade/sessão**: login (callback OIDC Keycloak → emite JWT RS256), `trocar-empresa`, `refresh` (rotation), `logout` (blacklist), `restore`; (f) **AccessDecision**: `POST /api/v1/iam/access/evaluate` com cache Redis; (g) **Session policy** por papel; (h) **Auditoria**: consumer de eventos `journey-os.*` → `journeyos_global.evento_auditoria` (índice Elastic `audit-events`). |
| 5 | **Fora de escopo (MVP)** | MFA/TOTP/WebAuthn; multi-SSO / BYOI; papéis customizados por empresa (papéis são canônicos do grupo); aprovação 2-step; emergency access; API keys com risk score; **enforcement** de restrição de IP (apenas config no MVP); self-service signup + billing; gestão de catálogos fiscais nacionais (vive no global, populado por MIG, não por WRKS). |
| 6 | **Integrações externas obrigatórias** | **Keycloak** (IdP OIDC — somente autenticação; autorização é de WRKS); **Redis/Valkey** (cache de sessão + AccessDecision + blacklist de logout); **PostgreSQL** (`journeyos_global` — único serviço de negócio que escreve nele, além de MIG); **journey-os-migrations (MIG)** (provisiona o schema `emp_<slug>` ao criar empresa); **Elasticsearch** (índice `audit-events`); **GWY** consome JWKS/chave pública de WRKS para validar JWT. |
| 7 | **TechLab AI / eventos** | **TechLab AI: nenhum** — WRKS é identidade fundacional, não consome capacidade de IA. **Produz** (event bus Kafka/AWS MSK): `journey-os.modelo.acesso.alterado` (mudança de RBAC → invalida cache em todos os serviços), `journey-os.usuario.criado`, `journey-os.empresa.provisionada`. **Consome:** todos os eventos `journey-os.*` dos demais módulos para alimentar `evento_auditoria`. **Sync (HTTP):** expõe `AccessDecision` para GWY + todos os serviços. |
| 8 | **Evento-âncora do domínio** | **"Sessão estabelecida"** (login → JWT emitido) é o heartbeat do golden path. O evento de domínio mais relevante cross-módulo é **`modelo.acesso.alterado`** (toda mudança de papel/permissão propaga invalidação de cache de autorização para a plataforma inteira). |

---

## Notas de contexto (Journey OS)

- **Stack:** Java 21 · Spring Boot 3.5.x · Gradle 8.x (Kotlin DSL) · PostgreSQL 15+ (`journeyos_global` + `emp_<slug>`) · Redis/Valkey · Keycloak (OIDC) · Kafka (AWS MSK) · Elasticsearch 9.x.
- **Multi-tenancy:** `schema-per-tenant`, schema global `journeyos_global`, termo `empresa`. WRKS **orquestra** o provisionamento de tenant (cria a linha em `empresa`, dispara MIG) e é dono do `journeyos_global` de IAM.
- **RBAC source of truth:** o **Journey OS é dono** dos papéis/permissões — Keycloak é apenas IdP de autenticação. Papéis canônicos derivam de `templates/architecture/decisions/rbac.arch.json` (D-058): `INFOPRODUTOR`, `HEAD_GROWTH`, `SDR`.
- **Type:** `standard` (autopilot) → A3 (specs-validate) **aplicável** (gerar BDD a partir das specs EARS).
- **Particularidade arquitetural:** único serviço de negócio autorizado a **escrever** em `journeyos_global` (RBAC/IAM). Demais serviços só **leem** (via `AccessDecision`/JWT). Ver `shared/modelo-dados/global-schema.md`.

## Referências canônicas consumidas

- `docs/architecture/shared/multi-empresa.md` — ADR-001 schema-per-empresa (decisão global)
- `docs/architecture/shared/rbac/{modelo,papeis,permissoes,session-policy,enforcement,data-scope,session-policy}.md`
- `docs/architecture/shared/modelo-dados/{global-schema,empresa,relacionamentos}.md`
- `docs/architecture/backend/standards/services-catalog.md` (§ WRKS)
