# SPEC-07 — Error Handling — WRKS

> `ProblemDetail` (RFC 7807, BE) → `AppError` (`@journeyos/shared/error-model`) → mensagem
> user-facing (`@journeyos/shared/ui-feedback`). Códigos do `api-contract.md` (error catalogue).

## Mapeamento `error.code` → UX

| `error.code` | HTTP | Mensagem FE (pt-BR) | Apresentação | Retry |
|---|---|---|---|---|
| `iam.credenciais-invalidas` | 401 | "Não foi possível entrar. Tente novamente." | banner no login | manual (botão) |
| `iam.token-expirado` | 401 | (silencioso) | — | automático (refresh) |
| `iam.refresh-invalido` | 401 | "Sua sessão expirou. Entre novamente." | redirect `/login` | re-login |
| `iam.sessao.versao-desatualizada` | 401 | (silencioso) | — | re-avaliar acesso/nav |
| `wrks.empresa.acesso-negado` | 403 | "Você não tem acesso a esta empresa." | toast | — |
| `wrks.papel.escalonamento` | 403 | "Você não pode atribuir um papel acima do seu." | erro inline no editor de papel | corrigir |
| `wrks.usuario.duplicado` | 409 | "Já existe um usuário com este e-mail." | erro inline no campo `email` | corrigir |
| `wrks.empresa.slug-duplicado` | 409 | "Este identificador de empresa já existe." | erro inline no campo `slug` | corrigir |
| `wrks.usuario.sem-empresa-ativa` | 422 | "Sua conta ainda não tem acesso a nenhuma empresa." | página "sem acesso" | aguardar convite |
| `wrks.usuario.associacao-nao-encontrada` | 404 | "Associação não encontrada." | toast | — |
| `wrks.empresa.provisionamento-falhou` | 502 | "Falha ao provisionar a empresa. Tente novamente." | banner | manual |
| (genérico/5xx) | 5xx | "Algo deu errado. Tente novamente em instantes." | banner | manual |

## Critérios de apresentação

- **Inline (erro de campo):** validações/conflitos atrelados a um campo (`email`, `slug`, papel).
- **Toast:** ações pontuais (troca de empresa negada, associação não encontrada).
- **Banner:** falhas de carregamento de página / 5xx / provisionamento.
- **Redirect:** sessão irrecuperável (`iam.refresh-invalido`).

## Retry

- **Automático:** apenas `iam.token-expirado` (via refresh no interceptor de `access-http-base`).
- **Manual (botão):** carregamentos de lista e provisionamento.
- Nenhum retry automático em mutações sensíveis a RBAC (evita duplicidade / escalonamento).

## Princípios

- O FE **não** inventa mensagens a partir do HTTP cru — sempre via `error.code` → `AppError`.
- `403` por permissão deve, idealmente, **nem renderizar a ação** (esconder via `can()`); o toast é
  o fallback para casos derivados do servidor.

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL map every backend ProblemDetail to an AppError via @journeyos/shared/error-model instead of building messages from raw HTTP.`
- `WHEN login fails with iam.credenciais-invalidas, THE SYSTEM SHALL show a banner on the login page and offer a manual retry.`
- `WHEN a session token expires with iam.token-expirado, THE SYSTEM SHALL refresh it silently through the access-http-base interceptor.`
- `IF the refresh token is invalid with iam.refresh-invalido, THEN THE SYSTEM SHALL redirect the user to /login.`
- `WHEN inviting a user returns wrks.usuario.duplicado, THE SYSTEM SHALL show an inline error on the email field and create no new user.`
- `IF a role assignment would escalate above the caller's role with wrks.papel.escalonamento, THEN THE SYSTEM SHALL reject it with an inline error and leave the target user's role unchanged.`
- `IF the authenticated user has no active empresa with wrks.usuario.sem-empresa-ativa, THEN THE SYSTEM SHALL render the "sem acesso" page.`
- `WHEN an empresa switch is denied with wrks.empresa.acesso-negado, THE SYSTEM SHALL show a toast and keep the previous empresa active.`
- `THE SYSTEM SHALL retry automatically only for iam.token-expirado and keep automatic retry off for RBAC-sensitive mutations.`
