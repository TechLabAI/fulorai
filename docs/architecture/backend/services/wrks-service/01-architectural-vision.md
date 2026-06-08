# 01 — Architectural Vision — WRKS (Workspace & Identity)

> Camada de visão (Layer 1 — Architect). Gera contratos, não código.
> Módulo: **WRKS** · serviço `wrks-service` · pacote `com.journeyos.wrks`.

## 1. Intent

WRKS é a **fundação de identidade e isolamento** do Journey OS. Estabelece a fronteira de
*workspace* (a `empresa` / tenant), modela quem são os usuários e o que cada um pode fazer
(RBAC canônico), e emite a credencial (JWT) que carrega o contexto de tenant + papel usado
por **todos** os demais módulos. É o primeiro serviço a subir e a precondição de qualquer
outra capacidade da plataforma.

## 2. Problem Statement

Operações de educação digital e infoprodutos (persona Rafael) trabalham hoje com ferramentas
fragmentadas (Hotmart + ActiveCampaign + Meta Ads + planilhas) e **sem um modelo único de
acesso**. Quando montam uma equipe (4–8 pessoas: growth, SDR, copy), não há forma confiável
de dizer "Marina vê a operação inteira, Lucas vê só a fila de leads dele". O Journey OS resolve
isso centralizando:

- **Workspace**: cada operação é uma `empresa` isolada (schema próprio, backup/retenção/LGPD por tenant).
- **Identidade**: um login único (Keycloak OIDC), com seleção de empresa quando o usuário opera várias.
- **Autorização**: papéis canônicos + permissões `<modulo>.<recurso>.<acao>`, avaliados de forma consistente em todo serviço.

Sem WRKS, cada módulo reimplementaria autenticação/autorização e o isolamento multi-tenant —
fonte garantida de vazamento cross-empresa e de regras de acesso divergentes.

## 3. Personas

| Persona | Papel canônico | Relação com WRKS |
|---|---|---|
| **Rafael — Infoprodutor / CEO** | `INFOPRODUTOR` | Persona **principal**. Administra o workspace: cria a empresa, convida usuários, atribui papéis, configura org structure e parâmetros. Controle total. |
| **Marina — Head de Growth** | `HEAD_GROWTH` | Persona **secundária**. Gerencia sua business unit/team; vê a operação consolidada da empresa. |
| **Lucas — SDR / Closer** | `SDR` | Consumidor de acesso restrito (data_scope próprio); WRKS define o que ele enxerga. |
| **Serviços do Journey OS** (GWY, LEAD, JRNY, …) | — (máquina) | Consomem `AccessDecision` + validam JWT emitido por WRKS. WRKS é a fonte da verdade de autorização. |

## 4. MVP Scope (in)

1. **Workspace/empresa**: CRUD de `empresa` em `journeyos_global`; provisionamento do schema operacional `emp_<slug>` (dispara MIG); parâmetros do tenant.
2. **Org structure**: business units e teams (hierarquia dentro da empresa); associação usuário ↔ team.
3. **Usuários**: `usuario` + `usuario_empresa` (papel + `data_scope` por associação); convite/ativação.
4. **RBAC**: `papel`, `permissao`, `papel_permissao`; seed canônico (`INFOPRODUTOR`/`HEAD_GROWTH`/`SDR`); `modelo_acesso_versao` (singleton) para invalidação de cache.
5. **Identidade/sessão**: `login` (callback OIDC Keycloak → JWT RS256), `trocar-empresa`, `refresh` (rotation), `logout` (blacklist Redis), `restore`.
6. **AccessDecision**: `POST /api/v1/iam/access/evaluate` → `AccessDecisionResponse` (papel + permissões + data_scope + versão + session policy), com cache Redis.
7. **Session policy** por papel (TTLs/idle) — config-driven.
8. **Auditoria**: consumer dos eventos `journey-os.*` → `journeyos_global.evento_auditoria` + indexação `audit-events` (Elastic).

## 5. Out of Scope (MVP)

- MFA (TOTP/WebAuthn) — apenas `mfa-required` como flag de config.
- Multi-SSO / BYOI (cada empresa com seu IdP).
- Papéis customizados por empresa (papéis são canônicos do grupo).
- Aprovação 2-step, emergency access, API keys com risk score.
- **Enforcement** de restrição de IP (apenas configurável, não aplicado no MVP).
- Self-service signup + billing.
- Catálogos fiscais nacionais (residem em `journeyos_global`, mas são populados por MIG/seed, não por WRKS).

## 6. Architectural Principles

1. **Single source of truth de autorização** — o Journey OS (WRKS) é dono de papéis/permissões; Keycloak é só IdP de autenticação.
2. **Hexagonal estrito** — domínio sem Spring/JPA; portas in/out; ArchUnit bloqueante (ver `ADR-001`).
3. **Isolamento por schema** — WRKS orquestra o provisionamento; nenhum dado operacional vaza cross-empresa (ver `ADR-004`).
4. **JWT curto + invalidação rápida** — token stateless de TTL curto; mudanças de RBAC propagam em segundos via `modelo_acesso_versao` + evento (ver `ADR-005`).
5. **Cache é otimização, nunca verdade** — Redis acelera sessão/AccessDecision; se cair, vai-se ao PostgreSQL.
6. **Auditável por design** — toda mudança de acesso e todo evento `journey-os.*` deixa trilha em `evento_auditoria`.
7. **Escrita exclusiva no global** — WRKS é o único serviço de negócio que escreve em `journeyos_global` (IAM); os demais só leem.

## 7. Success Signals

- Um usuário com acesso a N empresas troca de empresa e recebe JWT com novo `empresa_id` sem re-login.
- Mudança de permissão de um papel reflete em **todos** os serviços em < 5 s (sem invalidar tokens 1-a-1).
- Nenhuma requisição com JWT da empresa A retorna dado da empresa B (cross-empresa guard).
- Provisionar uma empresa nova cria o schema `emp_<slug>` e habilita o login dos usuários associados.
- `POST /access/evaluate` responde p95 < 30 ms com cache quente.
- 100% das cláusulas SHALL das specs viram cenário BDD (gate D-218).

---

## Referências

- ADRs: `adr/ADR-001..005`
- Brief: `_brief.md`
- Blueprint: `02-architecture-blueprint.md`
- Multi-tenancy global: `docs/architecture/shared/multi-empresa.md`
- RBAC: `docs/architecture/shared/rbac/`
