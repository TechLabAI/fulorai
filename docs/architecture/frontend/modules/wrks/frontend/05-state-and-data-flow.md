# 05 — State and Data Flow — WRKS

> Topologia de estado, padrão de acesso a dados, cache, updates otimistas, erros e navegação.

## 1. State Topology

| Estado | Onde vive | Dono |
|---|---|---|
| Sessão (claims, expiry, autenticado) | `@journeyos/shared/auth-session` | Access Layer (global) |
| Empresa ativa (`empresaId`) | `@journeyos/shared/empresa-context` | Access Layer (global) |
| AccessDecision (papel, permissões, scope, versão) | `@journeyos/shared/access-decision` | Access Layer (global) |
| Lista de empresas do usuário | `libs/wrks/data-access` (facade) → alimenta `empresa-context` | WRKS (local) |
| Lista/edição de usuários | `libs/wrks/data-access` (facade, signals) | WRKS (local, por feature) |
| Workspace/org structure | `libs/wrks/data-access` (facade, signals) | WRKS (local) |
| RBAC viewer (papéis×permissões) | `libs/wrks/data-access` (facade, signals) | WRKS (local, read-only) |
| Breadcrumb/menu state | `libs/wrks/navigation` | WRKS (local) |

Regra: estado **transversal** (sessão/empresa/RBAC) é global na Access Layer; estado **de tela**
é signal local na facade do WRKS.

## 2. Data Access Pattern

```
Component (OnPush)
   │ chama método da facade (nunca HttpClient direto — UINV/access-layer)
   ▼
Facade (libs/wrks/data-access)        signal<T> privado + .asReadonly() público
   │ chama *ApiService
   ▼
*ApiService (libs/wrks/data-access)   HttpClient via @journeyos/shared/access-http-base
   │ (interceptor injeta X-Empresa-Id, Correlation; normaliza erro)
   ▼
GWY → wrks-service
```

- Componentes consomem `facade.users()` / `facade.loading()` / `facade.error()` (signals).
- Sem `BehaviorSubject` manual; HTTP `Observable` é convertido para signal na facade.

## 3. Cache Strategy

- **Padrão:** chamar a API a cada navegação para a tela (dados de admin mudam e precisam ser frescos).
- **Exceção justificável:** lista de empresas do usuário pode ser cacheada durante a sessão
  (muda raramente) — invalidada em `switchTo` e em `modelo.acesso.alterado`. Será confirmada no SPEC.
- Cache, quando existir, é **escopado por empresa** e invalidado na troca (ADR-005).

## 4. Optimistic Updates

- **Não usar otimismo** em mutações sensíveis a RBAC (convite, alteração de papel): dependem de
  validação BE (anti-escalonamento INV-1) — mostrar `loading` e refletir só após confirmação.
- Toggles puramente visuais (ex.: expandir/contrair org tree) são locais, sem ida ao servidor.

## 5. Error Handling

```
wrks-service → ProblemDetail (RFC 7807)
   → interceptor de access-http-base normaliza
   → @journeyos/shared/error-model → AppError { code, title, detail, field? }
   → facade expõe error() signal
   → componente renderiza via @journeyos/shared/ui-feedback (inline em form / toast / página de erro)
```

Mapeamentos relevantes: `403` (sem permissão) → mensagem "sem acesso" + esconder ação;
`409` (anti-escalonamento / slug duplicado) → erro de campo no form; `401` → refresh/login.

## 6. Breadcrumbs e Navigation State

- `libs/wrks/navigation` fornece a config de breadcrumb do módulo (`wrks.nav.config.ts`).
- A árvore de menu é derivada por `NavigationService` (Access Layer) a partir das permissões —
  o WRKS **não** monta menu ad-hoc.
- Em troca de empresa, `NavigationService` re-deriva; breadcrumbs do WRKS resetam para a raiz do módulo.

---

## Referências

- `04-frontend-architecture-direction.md`
- `docs/architecture/frontend/standards/access-layer-contracts.md`
- ADR-002 (signals-first), ADR-005 (multi-empresa-context)
