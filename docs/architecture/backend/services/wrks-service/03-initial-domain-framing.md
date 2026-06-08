# 03 — Initial Domain Framing — WRKS

> Rascunho inicial do domínio. Refinado em `/be-architect-specs` (data-model + event-contracts).

## 1. Ubiquitous Language

| Termo | Definição |
|---|---|
| **Empresa (Workspace)** | Tenant isolado; uma operação/cliente. `empresa_id` = nome do schema (`emp_<slug>`). |
| **Business Unit** | Subdivisão organizacional dentro de uma empresa (ex.: "Aquisição", "Produto"). |
| **Team** | Grupo de usuários dentro de uma business unit. |
| **Usuário** | Pessoa física que faz login. Global ao grupo; opera N empresas. |
| **Associação (usuario_empresa)** | Vínculo usuário↔empresa que carrega o **papel** e o **data_scope**. |
| **Papel (Role)** | Conjunto canônico de permissões: `INFOPRODUTOR`, `HEAD_GROWTH`, `SDR`. Do grupo, não da empresa. |
| **Permissão** | Autorização atômica `<modulo>.<recurso>.<acao>` (ex.: `lead.lead.qualificar`). |
| **AccessDecision** | Resultado da avaliação de acesso de um usuário numa empresa (papel + permissões + scope). |
| **Sessão** | Estado de autenticação ativo (access token + refresh token + idle). |
| **Modelo de Acesso (versão)** | Contador singleton; bump invalida caches de AccessDecision em toda a plataforma. |
| **Data Scope** | Restrição de linhas que um usuário enxerga (ex.: `SDR` vê só seus leads). |

## 2. Aggregates and Entities (rascunho inicial)

| Aggregate root | Entidades / VOs | Invariantes-chave |
|---|---|---|
| **Empresa** | BusinessUnit, Team, parâmetros (jsonb) | slug único; provisionamento idempotente; soft-delete (`ativo`). |
| **Usuario** | Associacao (usuario_empresa) | email único; ≥1 associação ativa para logar; não pode auto-escalar papel. |
| **Papel** | PapelPermissao (N:N permissão) | código único canônico; bundle de permissões explícito (sem wildcard). |
| **Permissao** | — | código `<modulo>.<recurso>.<acao>` único. |
| **Sessao** | RefreshToken, Blacklist entry | TTL por papel (session policy); refresh com rotation; idle timeout. |
| **ModeloAcessoVersao** | — | singleton (`id = 1`); monotônico crescente. |

> `Empresa`, `Usuario`, `Papel`, `Permissao` vivem em `journeyos_global`. `Sessao`/cache vivem em Redis (otimização) com source of truth no Postgres/JWT.

## 3. Domain Events (inicial)

| Evento | Quando | Tipo |
|---|---|---|
| `journey-os.modelo.acesso.alterado` | papel/permissão/associação muda | **âncora de integração** (invalida cache) |
| `journey-os.usuario.criado` | novo usuário ativado | notificação |
| `journey-os.usuario.empresa.associado` | usuário vinculado a empresa com papel | notificação |
| `journey-os.empresa.provisionada` | schema `emp_<slug>` criado | notificação (dispara seeds dependentes) |
| `journey-os.sessao.estabelecida` | login bem-sucedido (JWT emitido) | heartbeat (golden path) |
| `journey-os.sessao.encerrada` | logout / idle / forced | notificação |

> WRKS **consome** todos os eventos `journey-os.*` (qualquer módulo) para `evento_auditoria`.

## 4. State Transitions (alto nível)

**Sessão:**
```
[ANÔNIMO] --login(OIDC ok)--> [AUTENTICADO]
[AUTENTICADO] --trocar-empresa--> [AUTENTICADO (nova empresa)]
[AUTENTICADO] --access-token expira--> [EXPIRADO] --refresh(rotation)--> [AUTENTICADO]
[AUTENTICADO|EXPIRADO] --logout|idle|versao-stale--> [ENCERRADO]
```

**Empresa:**
```
[SOLICITADA] --INSERT empresa--> [PROVISIONANDO (MIG)] --schema criado--> [ATIVA]
[ATIVA] --soft-delete--> [INATIVA]
```

**Usuário↔Empresa:**
```
[CONVIDADO] --ativação--> [ATIVO(papel)] --alterar papel (sem escalonar)--> [ATIVO(papel')]
[ATIVO] --desativar--> [INATIVO]
```

## 5. Invariants

- **INV-1** Usuário não pode criar/alterar associação com papel hierarquicamente acima do seu (anti-escalonamento).
- **INV-2** Login exige ≥1 `usuario_empresa.ativo = true`.
- **INV-3** Bundle de permissões de um papel é explícito — nunca wildcard `*.*`.
- **INV-4** `modelo_acesso_versao` é monotônico; todo mutate de RBAC o incrementa na mesma transação.
- **INV-5** `empresa.slug` único e imutável após provisionamento (é o nome do schema).
- **INV-6** Nenhuma resposta retorna dado de empresa diferente do `empresa_id` do JWT (cross-empresa guard).
- **INV-7** Refresh token é rotacionado a cada uso; o antigo é invalidado.
- **INV-8** Papéis são canônicos do grupo; a empresa nunca define papel próprio (MVP).

---

## Referências

- `docs/architecture/shared/rbac/{modelo,papeis,permissoes,data-scope}.md`
- `docs/architecture/shared/modelo-dados/{global-schema,empresa}.md`
- `05-persistence-model.md`
