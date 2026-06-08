# 02 — Architecture Blueprint — WRKS

> Fronteiras do sistema, atores, fluxos golden-path e camadas hexagonais.

## 1. System Boundary

`wrks-service` é um microserviço Spring Boot que expõe a API IAM sob `/api/v1/iam/**`
e é dono do subconjunto **IAM** do schema `journeyos_global`. Sua fronteira inclui:

- Identidade & sessão (login, refresh, logout, restore, trocar-empresa).
- RBAC (papéis, permissões, associações) + AccessDecision.
- Workspace (empresa) + org structure (business units, teams) + usuários.
- Trilha de auditoria consolidada (consumer de eventos).

**Fora da fronteira:** dados operacionais de qualquer empresa (`emp_<slug>.*`), catálogos
fiscais, e a autenticação primária (delegada ao Keycloak).

## 2. External Actors and Systems

| Ator / Sistema | Tipo | Interação |
|---|---|---|
| SPA `journey-os-web` | cliente | Login, seleção de empresa, telas de administração (usuários, papéis, teams). Acessa via GWY. |
| GWY (API Gateway) | serviço | Valida JWT (JWKS de WRKS) e propaga `X-Empresa-Id`/`X-Correlation-Id`; roteia `/api/v1/iam/**` para WRKS. |
| Demais serviços (LEAD, JRNY, ASST, COMM, SALE, INTL) | serviço | Chamam `POST /access/evaluate` (ou usam o claim do JWT) e cacheiam `AccessDecision`. |
| **Keycloak** | IdP | OIDC: autentica o usuário; WRKS recebe o callback e emite o JWT do Journey OS. |
| **Redis/Valkey** | infra | Cache de sessão + AccessDecision; blacklist de logout. |
| **PostgreSQL** (`journeyos_global`) | infra | Persistência IAM (source of truth). |
| **MIG** (`journey-os-migrations`) | serviço | Provisiona o schema `emp_<slug>` ao criar empresa. |
| **Kafka (AWS MSK)** | event bus | Produz `modelo.acesso.alterado`, `usuario.criado`, `empresa.provisionada`; consome `journey-os.*` para auditoria. |
| **Elasticsearch** | infra | Índice `audit-events` (domainContext WRKS). |

## 3. End-to-End Flows

### Golden path — Login + AccessDecision

```
1. Usuário → SPA → GWY → Keycloak (OIDC authorize)
2. Keycloak callback → POST /api/v1/iam/sessao/login
3. WRKS resolve usuario_empresa:
   - 1 empresa  → seleciona automaticamente
   - N empresas → retorna lista; FE mostra seletor → escolha
4. WRKS emite JWT RS256 (claims: sub, empresa_id, papel, modelo_acesso_versao, data_scope, exp)
   + grava sessão no Redis + refresh-token httpOnly
5. Serviço downstream recebe request com JWT → POST /access/evaluate (cache Redis)
   → AccessDecisionResponse (papel, permissões, data_scope, versão, session policy)
```

### Alternativa — Troca de empresa

```
POST /api/v1/iam/sessao/trocar-empresa { empresaId }
→ valida usuario_empresa(usuario, empresaId).ativo
→ emite novo JWT com empresa_id atualizado (sem re-login)
```

### Alternativa — Mudança de RBAC propaga

```
ADMIN altera papel_permissao
→ UPDATE journeyos_global.modelo_acesso_versao SET versao = versao + 1
→ publica journey-os.modelo.acesso.alterado
→ serviços invalidam cache local de AccessDecision
→ próximo request com JWT de versão antiga → 401 iam.sessao.versao-desatualizada → refresh
```

### Alternativa — Provisionar empresa

```
POST /api/v1/iam/empresa  { nome, slug, ... }
→ INSERT journeyos_global.empresa
→ dispara MIG (cria schema emp_<slug> + roda Vs)
→ publica journey-os.empresa.provisionada
```

### Alternativa — Auditoria (async)

```
qualquer journey-os.* event → @KafkaListener (WRKS) → INSERT evento_auditoria → index audit-events
```

## 4. Internal Boundaries (camadas hexagonais)

```
api/            → controllers REST /api/v1/iam/**, DTOs (records), @RestControllerAdvice (ProblemDetail)
application/     → use cases (@Service, @Transactional): Login, TrocarEmpresa, AvaliarAcesso,
                  GerenciarUsuario, GerenciarPapel, ProvisionarEmpresa, RegistrarAuditoria
  port/in       → interfaces de caso de uso
  port/out      → UsuarioRepositoryPort, PapelRepositoryPort, EmpresaRepositoryPort,
                  TokenIssuerPort, SessionCachePort, EventPublisherPort, MigrationTriggerPort,
                  IdpPort (Keycloak), AuditIndexPort (Elastic)
domain/         → model (Usuario, Papel, Permissao, Empresa, BusinessUnit, Team, Sessao,
                  AccessDecision, ModeloAcessoVersao) + domain services (regras de RBAC,
                  política de sessão, guarda de escalonamento de papel) — ZERO Spring/JPA
infrastructure/ → clients (Feign/HTTP MIG, IdP), config (DomainServiceConfig, SecurityConfig),
                  messaging (producer/consumer Kafka), persistence (entity/repository/adapter),
                  security (JWT filter, EmpresaContextHolder, CorrelationId), cache (Redis adapters)
```

## 5. Cross-cutting Concerns

- **Security**: WRKS é o emissor do JWT (RS256). Expõe JWKS para GWY/serviços. Guarda de **escalonamento de papel** (usuário não cria associação com papel acima do seu). `EmpresaContextHolder.require()` em todo application service que toca dado de empresa (RULE-07).
- **Observability**: `@Slf4j` + MDC (`empresaId`, `correlationId`, `usuarioId`); métricas Prometheus (`journey-os_iam_session_*`); auditoria consolidada.
- **Multi-tenancy**: WRKS lê/escreve `journeyos_global` (IAM) e **orquestra** a criação de `emp_<slug>`. Não acessa dados operacionais. Propagação de contexto conforme `shared/multi-empresa.md` (claim JWT sync; header `empresaId` em mensagens async).
- **Resilience**: Redis indisponível → fallback ao PostgreSQL (cache é otimização). Keycloak indisponível → login bloqueado (degradação explícita, sem bypass). Retry/circuit-breaker (Resilience4j) nas chamadas a MIG/IdP.

---

## Referências

- `01-architectural-vision.md`, `03-initial-domain-framing.md`
- `docs/architecture/backend/standards/hexagonal-patterns.md`
- `docs/architecture/shared/rbac/{modelo,session-policy}.md`
