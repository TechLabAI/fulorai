# SPEC-06 — Security

> ADR-004 (multi-tenancy). RBAC: `shared/rbac/{modelo,permissoes,data-scope}.md`. EARS guide:
> `docs/architecture/backend/standards/ears-notation.md`.

## Objetivo

Definir autenticação (JWT WRKS), autorização (`jrny.*`), isolamento de tenant (HTTP e consume) e
proteção de dados (LGPD) em `jrny-service`.

## Escopo

- **In:** validação de JWT (JWKS WRKS), resolução de `AccessDecision`, guarda de tenant no caminho HTTP **e** no consumo de eventos, permissões por endpoint, LGPD do `snapshot_entrada`.
- **Out:** emissão de token/login (WRKS); políticas de IdP (Keycloak).

## Decisões técnicas

- Filtro de segurança valida JWT contra `WRKS_JWKS_URI`; popula `EmpresaContextHolder` a partir do claim `empresa_id`.
- **Caminho de consumo (Kafka):** o tenant é resolvido pelo `empresaId` do envelope/header do evento; `EmpresaContextHolder` é fixado antes de processar e `clear()` no `finally`.
- Autorização por `AccessDecision` (Feign WRKS), cache invalidado por `modelo.acesso.alterado`.
- `MultiTenantConnectionProvider` aplica `SET search_path TO emp_<id>, journeyos_global, public`; `empresa_id` guard explícito reforça (ADR-004).

## Permissões `jrny.*`

`jrny.jornada.criar`, `jrny.jornada.editar`, `jrny.jornada.publicar`, `jrny.jornada.arquivar`,
`jrny.jornada.ler`, `jrny.estagio.criar`, `jrny.estagio.editar`, `jrny.estagio.ler`,
`jrny.regra.criar`, `jrny.regra.editar`, `jrny.roteamento.ler`.
(Confirmar/registrar em `shared/rbac/permissoes.md`.)

## Casos de borda

- JWT de empresa A acessando jornada/inscrição de empresa B → 404 (nunca vaza existência cross-tenant).
- Evento sem `empresaId` no envelope → rejeitado/DLQ (não processa sem tenant).
- `data_scope` restrito (SDR/Lucas) → enxerga subconjunto conforme decisão de acesso.

## Critérios de aceite (EARS)

- `IF a request has no valid JWT, THEN THE SYSTEM SHALL reject with 401 error.code 'jrny.auth.token-invalido'.`
- `THE SYSTEM SHALL fix the tenant schema from the JWT empresa_id claim on the HTTP path and SHALL ignore any empresa id supplied in path/body/header for data access.`
- `WHEN a domain event is consumed, THE SYSTEM SHALL resolve the tenant from the envelope empresaId, fix EmpresaContextHolder before processing, and clear it afterwards.`
- `IF a consumed event carries no empresaId, THEN THE SYSTEM SHALL NOT process it and SHALL route it to the DLQ.`
- `IF the AccessDecision lacks the required jrny.* permission for the operation, THEN THE SYSTEM SHALL reject with 403 error.code 'jrny.acesso.permissao-negada'.`
- `THE SYSTEM SHALL never return a journey, enrolment or decision belonging to another empresa.`
- `THE SYSTEM SHALL write empresa_id = EmpresaContextHolder.require() on every persisted row (defense-in-depth tenant guard).`
- `WHEN journey-os.modelo.acesso.alterado is received, THE SYSTEM SHALL invalidate the affected cached AccessDecision before the next check.`
- `WHERE the snapshot_entrada contains personal lead attributes, THE SYSTEM SHALL apply tenant retention/anonymization preserving the decision structure (LGPD).`
- `WHERE a data_scope restriction applies to the caller, THE SYSTEM SHALL filter results accordingly.`
