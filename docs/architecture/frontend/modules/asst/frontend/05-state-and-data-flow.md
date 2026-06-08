# 05 — State and Data Flow — ASST

> Topologia de estado, padrão de acesso a dados, cache, updates otimistas, erros e navegação.

## 1. State Topology

| Estado | Onde vive | Dono |
|---|---|---|
| Sessão (claims, expiry, autenticado) | `@journeyos/shared/auth-session` | Access Layer (global) |
| Empresa ativa (`empresaId`) | `@journeyos/shared/empresa-context` | Access Layer (global) |
| AccessDecision (papel, permissões `asst.*`, versão) | `@journeyos/shared/access-decision` | Access Layer (global) |
| Catálogo (lista + filtros + paginação) | `libs/asst/data-access` (facade, signals) | ASST (local, por feature) |
| Asset selecionado + versões | `libs/asst/data-access` (facade, signals) | ASST (local) |
| Estado do Asset Studio (composing/degradado/draft) | `libs/asst/data-access` (facade, signals) | ASST (local) |
| Fila de aprovação | `libs/asst/data-access` (facade, signals) | ASST (local, read-mostly) |
| Breadcrumb/menu state | `libs/asst/navigation` | ASST (local) |

Regra: estado **transversal** (sessão/empresa/RBAC) é global na Access Layer; estado **de tela**
(catálogo, detalhe, studio, fila) é signal local na facade do ASST.

## 2. Data Access Pattern

```
Component (OnPush)
   │ chama método da facade (nunca HttpClient direto — UINV-2/access-layer)
   ▼
Facade (libs/asst/data-access)        signal<T> privado + .asReadonly() público
   │ chama AssetApiService / StudioApiService
   ▼
*ApiService (libs/asst/data-access)   HttpClient via @journeyos/shared/access-http-base
   │ (interceptor injeta X-Empresa-Id, Correlation; normaliza erro)
   ▼
GWY → asst-service → (TechLab AI / Elastic / PostgreSQL / Kafka)
```

- Componentes consomem `facade.catalogo()` / `facade.loading()` / `facade.error()` /
  `facade.studioState()` (signals).
- Sem `BehaviorSubject` manual; HTTP `Observable` é convertido para signal na facade.
- O Asset Studio usa o mesmo padrão: `StudioApiService.compose()` → a facade muda
  `studioState` (`composing → draft-pronto | degradado`).

## 3. Cache Strategy

- **Padrão:** chamar a API a cada navegação para a tela (catálogo e detalhe precisam refletir
  mudanças de estado/aprovação frescas).
- **Exceção justificável:** o catálogo pode manter o último resultado em signal durante a navegação
  para detalhe e voltar sem refetch imediato (UX), **revalidando** ao retornar; a confirmar no SPEC.
- Cache, quando existir, é **escopado por empresa** e invalidado na troca (ADR-005 multi-empresa).
- **Versões são imutáveis** → uma vez carregada, o conteúdo de uma `versao_asset` pode ser cacheado
  com segurança por id (não muda); apenas a versão vigente (`versaoVigenteId`) muda ao publicar.

## 4. Optimistic Updates

- **Não usar otimismo** nas transições de workflow (submit/approve/publish) nem na composição do
  Studio: dependem de validação BE (state machine, IA) — mostrar `loading` e refletir só após
  confirmação (e tratar `409`/`503`).
- **Não usar otimismo** na criação de versão (numeração é atribuída pelo BE).
- Toggles puramente visuais (expandir histórico de versões, filtros locais) são locais, sem servidor.

## 5. Error Handling

```
asst-service → ProblemDetail (RFC 7807)
   → interceptor de access-http-base normaliza
   → @journeyos/shared/error-model → AppError { code, title, detail, field? }
   → facade expõe error() signal (e studioState='degradado' para o caso da IA)
   → componente renderiza via @journeyos/shared/ui-feedback (inline em form / toast / página)
```

Mapeamentos relevantes:

| HTTP / code | Tratamento na UI |
|---|---|
| `422 asst.asset.titulo-obrigatorio` / `tipo-invalido` | erro de campo no form de criação |
| `404 asst.asset.nao-encontrado` | página de "asset não encontrado" no detalhe |
| `404 asst.asset.sem-versao-publicada` | estado "nenhuma versão publicada" no detalhe |
| `409 asst.versao.imutavel` | a UI já previne (UINV-4); se ocorrer, toast + recarrega versões |
| `409 asst.estado.transicao-invalida` | esconder/desabilitar a ação inválida + toast explicativo |
| `503 asst.studio.ia-indisponivel` | banner de degradação no Studio; oferecer composição manual; **não** bloquear o resto |
| `403 asst.acesso.permissao-negada` | esconder a ação + mensagem "sem acesso" |
| `401 asst.auth.token-invalido` | refresh/login (interceptor/auth-session) |

## 6. Breadcrumbs e Navigation State

- `libs/asst/navigation` fornece a config de breadcrumb do módulo (`asst.nav.config.ts`):
  `Assets > Catálogo`, `Assets > {título} > Versões`, `Assets > {título} > Asset Studio`,
  `Assets > Aprovações`.
- A árvore de menu é derivada por `NavigationService` (Access Layer) a partir das permissões —
  o ASST **não** monta menu ad-hoc; o deep link "Aprovações" só aparece com `asst.asset.aprovar`.
- Em troca de empresa, `NavigationService` re-deriva; breadcrumbs do ASST resetam para a raiz
  (`/asst/library`) e o catálogo é invalidado/recarregado.

---

## Referências

- `04-frontend-architecture-direction.md`
- BE: `docs/architecture/backend/services/asst-service/contracts/api-contract.md` (códigos de erro)
- `docs/architecture/frontend/standards/access-layer-contracts.md`
- ADR-002 (signals-first), ADR-005 (Asset Studio / degradação da IA)
