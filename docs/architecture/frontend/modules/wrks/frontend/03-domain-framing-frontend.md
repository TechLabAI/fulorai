# 03 — Domain Framing (Frontend) — WRKS

> Espelho do domínio BE (`wrks-service/03-initial-domain-framing.md`) **sem redefinir** termos.
> Aqui mapeamos View Models, UI Events, transições de estado de UI e invariantes client-side.

## 1. Ubiquitous Language (referência ao BE — não redefinir)

Os termos canônicos vivem no BE (`_brief.md` + `03-initial-domain-framing.md` do `wrks-service`).
Resumo dos que a UI manipula diretamente:

| Termo | Uso na UI |
|---|---|
| **Empresa (Workspace)** | Item selecionável na seleção de empresa; contexto ativo no Shell. |
| **Business Unit / Team** | Nós da org structure em `feature-workspace` (settings). |
| **Usuário** | Linha na tabela de `feature-users`. |
| **Associação (usuario_empresa)** | Combinação usuário × empresa que carrega **papel** + **data_scope** (editável no convite/edição). |
| **Papel (Role)** | Valor canônico (`INFOPRODUTOR`/`HEAD_GROWTH`/`SDR`) exibido e atribuído. |
| **Permissão** | `<modulo>.<recurso>.<acao>` — usada por `AccessDecisionService.can()`; exibida (leitura) no RBAC viewer. |
| **AccessDecision** | Resultado consumido pela Access Layer; o FE **não** o calcula, apenas consome. |
| **Sessão** | Estado de `auth-session` (autenticado/expirado); dirige guards e topbar. |
| **Data Scope** | Campo do convite/edição; o FE só o transmite — o enforcement de linhas é BE. |

## 2. View Models (rascunho por tela)

> VMs são contratos de UI; serão refinados em `/fe-architect-specs` (SPEC-03 / vm-contracts).

```ts
// Seleção de empresa
EmpresaOptionVM   { empresaId: string; nome: string; papel: PapelCodigo; ativa: boolean }

// Sessão (derivada de auth-session — read-only para features)
SessionVM         { userId: string; nome: string; email: string; autenticado: boolean; mfaRequired: boolean }

// Workspace dashboard
WorkspaceVM       { empresaId: string; nome: string; slug: string; totalUsuarios: number;
                    businessUnits: number; parametros: Record<string, unknown> }

// Org structure (settings)
BusinessUnitVM    { id: string; nome: string; teams: TeamVM[] }
TeamVM            { id: string; nome: string; totalMembros: number }

// Gestão de usuários
UserRowVM         { usuarioId: string; nome: string; email: string; papel: PapelCodigo;
                    dataScope: string; status: 'ativo' | 'inativo' | 'convidado' }
InviteUserForm    { email: string; papel: PapelCodigo; dataScope: string }

// RBAC viewer (leitura)
RoleVM            { codigo: PapelCodigo; rotulo: string; permissoes: string[] }
```

## 3. UI Events (disparados pelo usuário → mudam state)

| Evento de UI | Origem | Efeito |
|---|---|---|
| `login.requested` | botão "Entrar" | redirect OIDC |
| `oidc.callback.received` | rota de callback | exchange → sessão autenticada |
| `empresa.selected` | cartão de empresa | `switchTo(empresaId)` → novo JWT + contexto |
| `empresa.switch.requested` | topbar (Shell) | troca de empresa em runtime |
| `user.invite.submitted` | form de convite | POST convite |
| `user.role.changed` | edição de usuário | PATCH papel (sujeito a anti-escalonamento) |
| `user.toggled` | switch ativar/desativar | PATCH status |
| `workspace.settings.saved` | form settings | PUT parâmetros/org structure |
| `logout.requested` | menu do usuário | logout (blacklist BE) + limpa contexto |

## 4. State Transitions (nível de UI)

**Sessão (FE):**
```
[anônimo] --login--> [redirecting] --callback--> [exchanging] --ok--> [autenticado]
[autenticado] --token expira--> [refreshing] --ok--> [autenticado] | --falha--> [anônimo]
[autenticado] --logout/idle--> [anônimo]
```

**Contexto de empresa (FE):**
```
[sem-contexto] --N=1 auto | seleção--> [contexto(empresa)]
[contexto(A)] --switchTo(B)--> [trocando] --ok--> [contexto(B)]   (cancela in-flight de A)
```

**Carregamento de qualquer tela de dados (padrão):**
```
[idle] --load--> [loading] --ok--> [success] | --erro--> [error(AppError)]
```

## 5. Invariants (client-side)

- **UINV-1** Nenhuma rota protegida renderiza sem sessão autenticada **e** (quando aplicável)
  empresa ativa — garantido por `authGuard` + `empresaGuard`.
- **UINV-2** A UI **nunca** decide RBAC localmente: visibilidade de menu/ação só via
  `AccessDecisionService.can(<perm>)` / `NavigationService`.
- **UINV-3** `empresaId` lido **somente** de `EmpresaContextService` — nunca do JWT decodificado
  nem de storage.
- **UINV-4** Formulário de convite/edição **não permite** selecionar papel acima do papel do
  usuário atual (reflexo client-side de INV-1 do BE; a decisão final é do BE).
- **UINV-5** Campos obrigatórios validados síncronamente: `email` (formato), `papel` (enum),
  `nome da empresa` (não vazio); validações de unicidade são assíncronas (resposta do BE).
- **UINV-6** Troca de empresa **invalida** dados em tela da empresa anterior antes de mostrar os
  novos (sem "piscar" dado cross-empresa).
- **UINV-7** Sessão/credenciais **nunca** em `localStorage`/`sessionStorage` direto — só via
  `@journeyos/shared/auth-session`.

---

## Referências

- BE: `docs/architecture/backend/services/wrks-service/03-initial-domain-framing.md`
- `docs/architecture/shared/rbac/` (papéis, permissões, data-scope)
- `05-state-and-data-flow.md`
