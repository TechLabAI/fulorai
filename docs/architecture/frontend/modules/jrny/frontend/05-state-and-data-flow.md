# 05 — State and Data Flow — JRNY (Journey & Routing)

> Topologia de estado, padrão de data-access, cache, updates otimistas, erros e breadcrumbs do FE JRNY.

## 1. State Topology

| Estado | Onde vive | Forma |
|---|---|---|
| Lista de jornadas (+filtros/busca/paginação) | `data-access` (facade `JourneyListFacade`) | `signal` + `computed` |
| Jornada em edição (metadados + estágios) | `data-access` (`JourneyBuilderFacade`) | `signal<JourneyBuilderVm>` |
| Estágio em edição | `feature-stage-editor` (local) ou builder facade | `signal<StageEditorVm>` |
| Regras de roteamento da jornada | `data-access` (`RoutingRulesFacade`) | `signal` + `computed` |
| Estado de jornada do lead + decisões | `data-access` (`DecisionLogFacade`) | `signal` (paginado) |
| Analytics de jornada | `data-access` (`JourneyAnalyticsFacade`) | `signal` |
| Sessão / empresa / RBAC | `@journeyos/shared/access-*` (**não** duplicado) | — |

## 2. Data Access Pattern

`HttpClient` (via `@journeyos/shared/access-http-base`) em **services** dentro de `data-access`; a
**facade** consome o service e emite `signal`s. Sem `BehaviorSubject` manual. RxJS só na borda
(interop `firstValueFrom`/`toSignal` na chamada). Endpoints espelham `jrny-service`:

```
JourneyService     POST/GET/PATCH /api/v1/journeys · /{id}/publicar · /{id}/arquivar · /{id}/nova-versao
StageService       POST/PATCH/GET /api/v1/journeys/{id}/estagios
RoutingRuleService POST/PATCH/GET /api/v1/routing/rules
RoutingQueryService GET /api/v1/routing/leads/{leadId}/journey · /decisions
```

## 3. Cache Strategy

Padrão = **chamar a API a cada navegação** (sem cache especulativo). A jornada em edição é mantida em
signal **enquanto a tela do builder está montada**; sair do builder descarta. Listas/decisões são
paginadas e recarregadas. Qualquer cache adicional só com justificativa no SPEC.

## 4. Optimistic Updates

**Evitar no MVP** para mutações de estado de jornada (publicar/arquivar/nova-versão) — são transições
com regras de servidor (estágio mínimo, estado válido); a UI espera a resposta e reflete o estado real
(evita render de estado inconsistente). Reordenação de estágios **pode** ser otimista (feedback
imediato no sortable) **com rollback** se o `PATCH` falhar — documentar a rollback strategy no SPEC.
Decisões são read-only (sem update).

## 5. Error Handling

`ProblemDetail` (RFC 7807) → `AppError` via `@journeyos/shared/error-model` → feedback via
`@journeyos/shared/ui-feedback`. Mapeamentos-chave (espelham o api-contract):

| error.code | UI |
|---|---|
| `jrny.jornada.sem-estagio` (422) | inline no botão publicar ("adicione ≥1 estágio") |
| `jrny.jornada.transicao-invalida` (409) | CTA "criar nova versão" em vez de erro cru |
| `jrny.estagio.ordem-duplicada` (409) | erro inline no campo `ordem` |
| `jrny.estagio.tipo-invalido` (422) | erro inline no seletor de tipo |
| `jrny.regra.condicao-invalida` (422) | erro inline no editor de condição |
| `jrny.regra.estagio-invalido` (422) | erro inline no seletor de destino |
| `jrny.jornada.nao-encontrada` / `jrny.inscricao.nao-encontrada` (404) | estado vazio amigável |
| `jrny.acesso.permissao-negada` (403) | bloqueio amigável (ação já escondida pelo guard) |
| **IA indisponível** (não-HTTP) | **badge neutro** "roteamento determinístico" (não é erro) |

## 6. Breadcrumbs e Navigation State

`libs/jrny/navigation` alimenta `BreadcrumbItem[]`:

```
Jornadas
Jornadas / {nome da jornada}                         (builder)
Jornadas / {nome} / Estágio {ordem}                  (stage editor)
Jornadas / {nome} / Regras                           (routing engine)
Leads / {leadId} / Decisões                          (decision log)
Jornadas / Analytics                                 (analytics)
```

Visibilidade de menu/itens filtrada por `NavigationService` + `AccessDecisionService` (permissões
`jrny.*`). Troca de empresa limpa o estado de navegação do módulo.

---

## Referências

- `03-domain-framing-frontend.md` · `04-frontend-architecture-direction.md` · `06-risks-gaps-assumptions.md`
- BE: `jrny-service/contracts/{api-contract,event-contracts}.md`
- `docs/architecture/frontend/standards/access-layer-contracts.md`
