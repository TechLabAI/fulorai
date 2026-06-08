# 05 — State and Data Flow — COMM

> Topologia de estado, padrão de acesso a dados, cache, atualizações otimistas, erros e navegação.

## 1. State Topology

| Estado | Onde vive | Tipo |
|---|---|---|
| Sessão / claims / bearer | `@journeyos/shared/auth-session` | Access Layer (não COMM) |
| Empresa ativa | `@journeyos/shared/empresa-context` | Access Layer (não COMM) |
| Decisões de acesso (`comm.*`) | `@journeyos/shared/access-decision` | Access Layer (não COMM) |
| Catálogo de templates + filtros/busca | `libs/comm/data-access` (TemplateFacade) | signal local |
| Template selecionado / editor | `libs/comm/data-access` (TemplateFacade) | signal local |
| Estado do Studio (`studioState`) | `libs/comm/data-access` (StudioFacade) | signal local |
| Regras de roteamento | `libs/comm/data-access` (RoutingFacade) | signal local |
| Mensagens (lista) + filtros | `libs/comm/data-access` (MessageFacade) | signal local |
| Mensagem selecionada + eventos (timeline) | `libs/comm/data-access` (MessageFacade) | signal local |
| Controle de polling de entrega | `libs/comm/data-access` (MessageFacade) | signal + RxJS interval |
| Canais configurados | `libs/comm/data-access` (ChannelFacade) | signal local |
| Breadcrumbs/menu | `libs/comm/navigation` | signal local |

## 2. Data Access Pattern

- Cada recurso tem um `*ApiService` (`HttpClient` via `@journeyos/shared/access-http-base`) que retorna
  `Observable`/`Promise`; a **facade** consome, atualiza `signal<T>` privado e expõe `.asReadonly()`.
- Componentes (features) consomem **somente facades** — nunca `HttpClient` direto (UINV-5).
- Mapeamento de endpoints → facades:
  - `TemplateApiService`: `GET/POST /templates`, `GET/PATCH /templates/{id}`, `POST /templates/{id}/{ativar,arquivar}`.
  - `StudioApiService`: `POST /templates/{id}/studio/compose` (com `Idempotency-Key`).
  - `RoutingApiService`: `GET/POST /routing-rules`, `GET/PATCH /routing-rules/{id}`.
  - `MessageApiService`: `POST /messages` (com `Idempotency-Key`), `GET /messages`, `GET /messages/{id}`, `GET /messages/{id}/events`.
  - `ChannelApiService`: `GET/POST /channels`, `PATCH /channels/{id}`.

## 3. Cache Strategy

- **Padrão = chamar a API a cada navegação** (sem cache persistente). Listas recarregam ao entrar na rota.
- Exceção justificada: durante a sessão de **detalhe de mensagem**, os `eventos` são acumulados em
  memória entre ticks de polling (append-only) para a timeline não "piscar"; descartados ao sair.
- Troca de empresa **invalida** todos os signals de COMM em tela antes do reload (UINV-9).

## 4. Optimistic Updates

- **Disparo de mensagem**: **sem otimismo** — a UI só mostra a mensagem após `202` (estado real
  `ENFILEIRADA`), evitando refletir um envio que o BE pode rejeitar (`409`/`422`).
- **Template Studio**: **sem otimismo** — o novo corpo só aparece após `200`; durante `composing` o
  formulário do Studio fica bloqueado (sem alterar o corpo atual).
- **Ativar/Arquivar template**: atualização otimista **leve** do `state-chip` permitida, com rollback
  se o POST falhar (a transição é determinística e barata); documentar rollback no implement.
- **Edição de template / regra / canal**: sem otimismo (revalidação síncrona + confirmação do PATCH).

## 5. Error Handling

`ProblemDetail` (BE) → `AppError` (`@journeyos/shared/error-model`) → mensagem via `ui-feedback`.
Mapeamento explícito:

| HTTP · code | Tratamento na UI |
|---|---|
| `422 comm.template.canal-invalido` / `tipo-invalido` / `nome-obrigatorio` | Validação de formulário (idealmente síncrona antes do POST). |
| `422 comm.template.assunto-obrigatorio` | Campo `assunto` destacado quando `canal=EMAIL` (UINV-2). |
| `422 comm.template.variavel-nao-declarada` | Editor destaca placeholder não declarada (UINV-1). |
| `404 comm.template.nao-encontrado` / `comm.mensagem.nao-encontrada` | Estado "não encontrado" + voltar ao catálogo/lista. |
| `409 comm.template.nao-ativo` | Bloqueia disparo; CTA "ativar template" (UINV-3). |
| `422 comm.mensagem.variavel-ausente` | Form de disparo destaca variável faltante. |
| `409 comm.mensagem.estado-invalido` | Timeline informa transição inválida (rara; não-fatal). |
| `422 comm.roteamento.sem-canal` | Sugere escolher canal manual ou criar regra. |
| `422 comm.canal.nao-configurado` | CTA para `/comm/channels`. |
| `409 comm.canal.duplicado` | Form de canal informa config (canal, provedor) já existente. |
| `503 comm.studio.ia-indisponivel` | `studioState='degradado'`, banner + CTA "editar manualmente"; corpo inalterado (UINV-7). |
| `503 comm.canal.provedor-indisponivel` | Mensagem em `FALHADA` com `motivoFalha`; timeline exibe a falha. |
| `401 comm.auth.token-invalido` | Delegado à Access Layer (re-login). |
| `403 comm.acesso.permissao-negada` | Estado "sem permissão"; ação não deveria estar visível (defesa em profundidade). |

## 6. Breadcrumbs e Navigation State

`libs/comm/navigation` alimenta `BreadcrumbItem[]` por rota:

```
Comunicação ▸ Templates                         (/comm/templates)
Comunicação ▸ Templates ▸ {nome do template}    (/comm/templates/:id)
Comunicação ▸ Templates ▸ {nome} ▸ Studio       (/comm/templates/:id/studio)
Comunicação ▸ Roteamento                        (/comm/routing-rules)
Comunicação ▸ Mensagens                         (/comm/messages)
Comunicação ▸ Mensagens ▸ {id curto}            (/comm/messages/:id)
Comunicação ▸ Canais                            (/comm/channels)
```

O `NavigationService` (`@journeyos/shared/access-decision`) filtra deep-links por permissão; itens sem
`comm.*` correspondente não aparecem no menu.

---

## Referências

- `03-domain-framing-frontend.md` (VMs + invariantes) · `04-frontend-architecture-direction.md` (libs/rotas)
- BE API + erros: `docs/architecture/backend/services/comm-service/contracts/api-contract.md` §5
- `docs/architecture/frontend/standards/access-layer-contracts.md`
- ADR-002 (signals) · ADR-005 (polling de entrega)
