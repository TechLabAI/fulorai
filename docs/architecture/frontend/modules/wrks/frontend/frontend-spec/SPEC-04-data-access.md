# SPEC-04 — Data Access — WRKS

> Services (`*ApiService`) + facades (signals) + endpoints. **Fonte:** BE
> `wrks-service/contracts/api-contract.md` (base `/api/v1/iam`). Todas as chamadas via
> `@journeyos/shared/access-http-base` (interceptor injeta `Authorization` + `X-Correlation-Id`;
> `empresa_id` viaja como **claim do JWT**, não como path/body).

## Tabela mestre

| Resource | Endpoint (base `/api/v1/iam`) | Service | Facade | Operations | Cache? |
|---|---|---|---|---|---|
| Session | `/sessao/login`, `/sessao/trocar-empresa`, `/sessao/refresh`, `/sessao/logout`, `/sessao/restore` | (delegado a `@journeyos/shared/auth-session`) | `auth-session` | login, trocarEmpresa, refresh, logout, restore | sessão |
| Empresa | `GET/POST /empresas`, `GET/PUT /empresas/{id}`, `POST /empresas/{id}/provisionar` | `EmpresaApiService` | `WorkspaceFacade` | list, get, create, update, provisionar | get: por-empresa |
| Usuario | `GET/POST /usuarios`, `GET/PUT/DELETE /usuarios/{id}`, `POST /usuarios/{id}/empresas` | `UsuarioApiService` | `UsersFacade`, `UserDetailFacade` | list, get, create, update, delete, associar | no |
| Papel | `GET /papeis`, `GET /papeis/{codigo}/permissoes` | `PapelApiService` | `RbacFacade` | list, getPermissoes | sessão (read-only) |
| BusinessUnit | `GET/POST /business-units`, `PUT /business-units/{id}` | `BusinessUnitApiService` | `OrgStructureFacade` | list, create, update | no |
| Team | `GET/POST /teams`, `PUT /teams/{id}` | `TeamApiService` | `OrgStructureFacade` | list, create, update | no |

> `Papel PUT /papeis/{codigo}/permissoes` (`wrks.papel.editar`) é **fora do MVP** (RBAC viewer é
> read-only). `Auditoria` (`/auditoria`) também fora do MVP.

## Padrão de facade (signals)

```typescript
@Injectable()
class UsersFacade {
  private readonly _users   = signal<UserRow[]>([]);
  private readonly _loading = signal(false);
  private readonly _error   = signal<AppError | null>(null);

  readonly users   = this._users.asReadonly();
  readonly loading  = this._loading.asReadonly();
  readonly error    = this._error.asReadonly();

  constructor(private api: UsuarioApiService) {}

  load(): void { /* set loading; api.list() → _users | _error; clear loading */ }
  invite(form: InviteUserForm): void { /* api.create + associar; reload (sem otimismo) */ }
  toggle(id: string): void { /* api.update status; reload */ }
}
```

## DTOs FE

- Mapear respostas do BE para os VMs do SPEC-03. Quando `@journeyos/shared/contracts` (gerado do
  OpenAPI do `wrks-service`) existir, **usar os tipos gerados** como fonte e mapear para VM local.
- Enquanto o OpenAPI não está materializado (ver gap R-1 / SPEC-06 BE), os DTOs FE seguem o shape
  documentado no `api-contract.md` (cross-link em `contracts/backend-api-cross-link.md`).

## Error mapping (resumo — detalhe em SPEC-07)

| `error.code` BE | HTTP | UX |
|---|---|---|
| `wrks.usuario.duplicado` | 409 | erro de campo `email` no form de convite |
| `wrks.papel.escalonamento` | 403 | erro no editor de papel ("você não pode atribuir papel acima do seu") |
| `wrks.empresa.acesso-negado` | 403 | bloqueia troca de empresa; toast |
| `wrks.empresa.slug-duplicado` | 409 | erro de campo `slug` |
| `iam.refresh-invalido` / `iam.token-expirado` | 401 | refresh → se falhar, redirect `/login` |
| `iam.sessao.versao-desatualizada` | 401 | re-avaliar AccessDecision + navegação |

## Cancelamento / multi-empresa

- Em `EmpresaContextService.switchTo`, **cancelar** requisições in-flight da empresa anterior e
  **invalidar** caches escopados (`Empresa.get`) — ver ADR-005. As facades expõem `reset()` para
  isso, chamado pela Access Layer na troca.

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL route every WRKS API call through @journeyos/shared/access-http-base so Authorization and X-Correlation-Id are injected.`
- `THE SYSTEM SHALL carry empresa_id as a JWT claim rather than as a path or body parameter.`
- `WHEN the user switches empresa via EmpresaContextService.switchTo, THE SYSTEM SHALL cancel in-flight requests of the previous empresa and invalidate empresa-scoped caches.`
- `WHEN the active empresa changes, THE SYSTEM SHALL reload empresa-scoped lists in the new empresa scope and keep data from the previous empresa out of the view.`
- `WHEN a list load fails, THE SYSTEM SHALL surface the failure through the facade error signal and offer a manual retry.`
