# Backend API Cross-Link — WRKS

> Liga os contratos FE do WRKS ao contrato REST autoritativo do `wrks-service` (BE).
> **Fonte da verdade da API:** `docs/architecture/backend/services/wrks-service/contracts/api-contract.md`
> (base `/api/v1/iam`, erros RFC 7807).

## Endpoints consumidos pelo FE

| Feature FE | Endpoint BE | Permissão | Observações |
|---|---|---|---|
| `feature-login` | `POST /sessao/login`, `GET /sessao/restore`, `POST /sessao/refresh`, `POST /sessao/logout` | público / sessão | via `@journeyos/shared/auth-session`; refresh é cookie httpOnly |
| `feature-empresa-select` | `POST /sessao/login` (lista `empresasDisponiveis`), `POST /sessao/trocar-empresa` | sessão | `selecaoNecessaria: true` quando N>1 |
| `feature-workspace` | `GET/PUT /empresas/{id}`, `GET/POST /business-units`, `GET/POST /teams`, `PUT /{..}/{id}` | `wrks.empresa.read/editar`, `wrks.business_unit.*`, `wrks.team.*` | `empresa_id` vem do claim JWT |
| `feature-users` | `GET/POST /usuarios`, `GET/PUT/DELETE /usuarios/{id}`, `POST /usuarios/{id}/empresas` | `wrks.usuario.*` | associar = papel + data_scope |
| `feature-rbac-viewer` | `GET /papeis`, `GET /papeis/{codigo}/permissoes` | `wrks.papel.read` | read-only no MVP |

## Diferenças / decisões FE (diffs em relação ao contrato BE)

- **`empresa_id`**: o BE o trata como **claim do JWT** (não path/body). O FE **nunca** o envia em
  body/path; o interceptor de `access-http-base` cuida do header de debug `X-Empresa-Id`. O FE lê o
  contexto só de `EmpresaContextService` (UINV-3).
- **Sessão delegada**: login/refresh/logout/restore/trocar-empresa são encapsulados por
  `@journeyos/shared/auth-session` — as features do WRKS chamam a fachada, não o `HttpClient`.
- **Fora do MVP FE**: `PUT /papeis/{codigo}/permissoes` (`wrks.papel.editar`), `/empresas` (criar/
  provisionar — fluxo de criação de empresa é admin de grupo, fora do MVP de UI), `/auditoria`.

## DTO generation (status)

- O OpenAPI do `wrks-service` ainda não foi materializado para gerar `@journeyos/shared/contracts`
  (gap R-1). Enquanto isso, os DTOs FE seguem o shape do `api-contract.md`. Quando o OpenAPI existir,
  os tipos gerados passam a ser a fonte e este cross-link aponta para eles.

## Rastreabilidade

- Erros: ver `frontend-spec/SPEC-07-error-handling.md` (mapeia o error catalogue do BE).
- BDD: os `.feature` do FE (`../e2e/`) espelham, do lado da UI, os cenários de
  `wrks-service/tests/cucumber/` (login-and-session, user-administration, access-decision).
