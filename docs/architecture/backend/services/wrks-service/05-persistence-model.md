# 05 — Persistence Model — WRKS

> Rascunho de persistência. Refinado em `/be-architect-specs` (data-model) e materializado
> pelas migrations centralizadas em `journey-os-migrations`.

## 1. Schema Strategy

WRKS é dono do subconjunto **IAM** de `journeyos_global` (schema compartilhado, vive 1×).
**Não** possui tabelas em `emp_<slug>` — apenas **orquestra** a criação desses schemas via MIG.

| Schema | Papel de WRKS |
|---|---|
| `journeyos_global` | **Read/Write** (IAM): usuario, papel, permissao, papel_permissao, usuario_empresa, empresa, business_unit, team, modelo_acesso_versao, evento_auditoria. |
| `emp_<slug>` | **Nenhum acesso direto** — WRKS dispara o provisionamento; dados operacionais pertencem aos serviços de negócio. |
| Redis | Sessão, AccessDecision cache, blacklist (otimização, não source of truth). |

> WRKS é o **único serviço de negócio** autorizado a escrever em `journeyos_global` (além de MIG/seed). Demais serviços só leem (via AccessDecision/JWT).

## 2. Initial Entities (rascunho — DDL canônico em `journey-os-migrations`)

```
journeyos_global.usuario               (usuario_id UUID PK, email UNIQUE, nome, ativo, criado_em)
journeyos_global.empresa               (empresa_id VARCHAR(50) PK = slug 'emp_<x>', nome_fantasia,
                                        razao_social, parametros JSONB, ativo, criado_em)
journeyos_global.business_unit         (business_unit_id UUID PK, empresa_id FK, nome, ativo)
journeyos_global.team                  (team_id UUID PK, business_unit_id FK, nome, ativo)
journeyos_global.usuario_team          (usuario_id FK, team_id FK, PK(usuario_id, team_id))
journeyos_global.papel                 (papel_id UUID PK, codigo UNIQUE, nome, descricao, ativo)
journeyos_global.permissao             (permissao_id UUID PK, codigo UNIQUE, modulo, nome, descricao)
journeyos_global.papel_permissao       (papel_id FK, permissao_id FK, PK(papel_id, permissao_id))
journeyos_global.usuario_empresa       (usuario_id FK, empresa_id, papel, data_scope, ativo,
                                        PK(usuario_id, empresa_id))
journeyos_global.modelo_acesso_versao  (id INT PK DEFAULT 1 CHECK(id=1), versao BIGINT, atualizado_em)
journeyos_global.evento_auditoria      (id BIGSERIAL PK, empresa_id NULLABLE, usuario_id, evento,
                                        payload JSONB, correlation_id, timestamp, source_service)
```

Convenções (`global-schema.md`): UUID para entidades de domínio; `VARCHAR(50)` slug para `empresa_id`;
`BIGSERIAL` para auditoria; soft-delete via `ativo`; timestamps `TIMESTAMPTZ DEFAULT now()`.

> `business_unit`/`team`/`usuario_team` são **novidade** introduzida por WRKS (org structure do MVP);
> serão formalizadas no data-model das specs e nas migrations `V*__iam_*`.

## 3. Migration Strategy

- Todas as migrations vivem em `journey-os-migrations/.../db/migration/global/V<N>__iam_<descricao>.sql` (rodam 1×).
- WRKS usa `spring.jpa.hibernate.ddl-auto=validate` (schema preparado por MIG).
- Seeds canônicos: papéis (`INFOPRODUTOR`/`HEAD_GROWTH`/`SDR`) + permissões + bundles em V1 (`papeis.md` é gerado de `rbac.arch.json`).
- `spring.jpa.open-in-view=false` (RULE-08).

## 4. Data Lifecycle

- **Soft-delete** (`ativo`) em usuario/empresa/papel/business_unit/team — nunca `DELETE` físico.
- **Auditoria** (`evento_auditoria`): retenção longa; indexada em Elastic `audit-events` (consulta/observabilidade). LGPD: trilha por `empresa_id` permite expurgo por tenant.
- **Sessão/cache** (Redis): TTL por papel (session policy); blacklist com TTL = TTL restante do access token.
- **Right-to-erasure (LGPD)**: dump/erase por schema `emp_<slug>` + anonimização de `usuario` no global; trilha preserva `usuario_id` pseudonimizado.
- **Versão de acesso**: `modelo_acesso_versao` nunca decrementa; histórico de mudanças via `evento_auditoria`.

---

## Referências

- `docs/architecture/shared/modelo-dados/{global-schema,empresa,persistence-conventions,relacionamentos}.md`
- `docs/architecture/shared/rbac/{modelo,papeis,session-policy}.md`
- `ADR-004` (multi-tenancy / provisionamento), `ADR-005` (sessão)
