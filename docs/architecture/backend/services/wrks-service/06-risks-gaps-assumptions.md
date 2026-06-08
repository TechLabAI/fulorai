# 06 — Risks, Gaps & Assumptions — WRKS

## 1. Riscos

| # | Risco | Impacto | Mitigação |
|---|---|---|---|
| R-1 | **Vazamento cross-empresa** (JWT de A retorna dado de B) | Crítico (segurança/LGPD) | `EmpresaContextHolder.require()` (RULE-07) + guard explícito; testes BDD de isolamento; WRKS não acessa `emp_*`. |
| R-2 | **Escalonamento de privilégio** (usuário atribui papel acima do seu) | Crítico | Domain service de anti-escalonamento (INV-1); cobertura BDD. |
| R-3 | **Cache stale** após mudança de RBAC | Alto | `modelo_acesso_versao` + evento `modelo.acesso.alterado` + 401 `versao-desatualizada` (propagação < 5s). |
| R-4 | **Keycloak indisponível** | Alto (login bloqueado) | Degradação explícita (sem bypass); circuit-breaker; health check; tokens válidos seguem funcionando até expirar. |
| R-5 | **Redis indisponível** | Médio | Fallback ao PostgreSQL (cache é otimização). Monitorar latência. |
| R-6 | **Provisionamento de empresa parcial** (INSERT ok, MIG falha) | Alto | Saga/idempotência: empresa em estado `PROVISIONANDO` até evento `empresa.provisionada`; retry MIG. |
| R-7 | **Roubo de refresh token** | Alto | Cookie httpOnly+secure+sameSite=strict; rotation; blacklist no logout. |
| R-8 | **Inconsistência de docs canônicos** (roles ERP legados em `rbac/modelo.md` §1 vs `papeis.md`) | Médio | **Fonte de verdade = `papeis.md`/`rbac.arch.json`**: `INFOPRODUTOR`/`HEAD_GROWTH`/`SDR`. Ignorar exemplos ERP/madeireira legados. |

## 2. Gaps Conhecidos

- **G-1** Org structure (business_unit/team/usuario_team) ainda não está no `global-schema.md` canônico — WRKS introduz; formalizar no data-model das specs + migrations.
- **G-2** Mecanismo exato do gatilho MIG (HTTP endpoint vs comando vs evento) não definido — decidir em specs/integration-contract.
- **G-3** Bundles de permissão por papel estão `all` (TODO em `papeis.md`) — refinar antes de produção (não bloqueia scaffold).
- **G-4** Contrato do `empresa.provisionada` e ordem de seeds dependentes (quem reage) a definir no event-catalog.
- **G-5** Transporte de mensageria: docs shared citam JMS/Artemis; `project-context.json` define **Kafka (AWS MSK)**. Adotado **Kafka**; alinhar `platform-patterns.md` se necessário.

## 3. Suposições a Validar

- **A-1** Keycloak é o IdP único do MVP (sem multi-SSO).
- **A-2** Papéis são canônicos do grupo (sem papéis custom por empresa no MVP).
- **A-3** `empresa_id` (slug) é o nome do schema e é imutável após provisionamento.
- **A-4** Todos os serviços de negócio leem autorização via AccessDecision/JWT e **não** escrevem em `journeyos_global`.
- **A-5** Auditoria consolidada em `journeyos_global.evento_auditoria` (decisão pendente em `global-schema.md` §Auditoria resolvida a favor do consolidado).
- **A-6** MFA/IP-restriction são apenas flags de config no MVP (sem enforcement).

## 4. Dependências Críticas

| Dependência | Necessária para | Status |
|---|---|---|
| **MIG** (`journey-os-migrations`) | Schema `journeyos_global` (IAM) + provisionar `emp_<slug>` | ✅ scaffolded (vision/specs/backlog/scaffold OK) |
| **REG** (Eureka) | Discovery | ✅ scaffolded |
| **GWY** | Validação de JWT na borda | ✅ scaffolded (consome JWKS de WRKS) |
| **Keycloak** | Autenticação OIDC | ⚠️ infra a prover (docker-compose dev) |
| **Redis/Valkey** | Cache sessão/access | ⚠️ infra a prover |
| **Kafka (AWS MSK)** | Eventos + auditoria | ⚠️ infra a prover (local: container) |
| **Elasticsearch** | Índice `audit-events` | ✅ overlay elastic-stack gerado (P3b) |
| **TechLab AI** | — | N/A (WRKS não usa IA) |

---

## Referências

- `01-architectural-vision.md` §7 (success signals), `adr/ADR-001..005`
- `docs/architecture/shared/rbac/`, `docs/architecture/shared/multi-empresa.md`
