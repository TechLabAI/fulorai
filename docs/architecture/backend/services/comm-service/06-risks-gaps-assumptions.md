# 06 — Risks, Gaps & Assumptions — COMM (Communication Hub)

> Itens a validar antes/durante specs e implementação. Cada risco com mitigação.

## 1. Riscos

| # | Risco | Impacto | Mitigação |
|---|---|---|---|
| R1 | **Provedor de canal indisponível/lento** (Meta/Twilio/SES) | Alto | Adapter com timeout + circuit breaker + retry/backoff (Resilience4j); disparo via worker/outbox (não bloqueia o request); fallback de canal por roteamento; DLQ para reprocesso. |
| R2 | **TechLab AI indisponível** degrada o Template Studio | Médio | Timeout + CB + fallback graceful; CRUD/roteamento/disparo independem da IA (`ADR-003`). |
| R3 | **Mensagens duplicadas** ao lead (reprocesso/clique duplo) | Alto | Idempotência por `chave_idempotencia` (unique por empresa); registro de callbacks idempotente; consumo de eventos por `eventId`. |
| R4 | **Vazamento de credenciais de provedor** | Alto | `config_canal` guarda apenas `credencial_ref` (secret manager/`${VAR}`); segredo nunca persistido/logado. |
| R5 | **Webhook forjado** (callback de provedor falso) | Alto | Verificação de assinatura/segredo do provedor no endpoint de webhook; rejeição de payloads não autenticados. |
| R6 | **Inconsistência PostgreSQL ↔ Elastic** (`communication-events`) | Médio | Elastic é projeção; reindex idempotente a partir de `evento_entrega`; PostgreSQL é fonte da verdade. |
| R7 | **Vazamento cross-empresa** | Alto | `EmpresaContextHolder.require()` + `empresa_id` guard + testes de isolamento; schema-per-tenant. |
| R8 | **Compliance / opt-out** — enviar a quem optou por não receber | Médio | Consentimento básico registrado; verificação de supressão antes do disparo (MVP simples; supressão regulatória completa pós-MVP). |
| R9 | **Acoplamento de provedor no domínio** | Médio | Adapters de canal sob `CanalEnvioPort`; domínio conhece só `canal` (`ADR-005`); ArchUnit barra import de SDK fora de `infrastructure.channels`. |

## 2. Gaps Conhecidos

- **Contrato TechLab AI `document_composition` não pinado:** `integrations/techlab-ai/openapi.json` e `techlab-ai-integration.md` ainda são placeholders (P3 bloqueado — aguarda 1º commit upstream). Endpoints/DTOs exatos do Template Studio serão fixados quando o SHA for pinado.
- **Contratos dos provedores de canal:** os schemas de envio e de webhook por provedor (Meta WABA, Twilio, SES, Telegram) serão detalhados em `contracts/integration-contracts.md` nas specs; o MVP define a interface canônica (`CanalEnvioPort` + normalização de callback), não cada provedor em detalhe.
- **Modelo de `condicoes` de roteamento:** o schema jsonb de condições (segmento/estágio/preferência/janela) e a semântica de prioridade/fallback serão detalhados nas specs (`data-model.md` + SPECs).
- **Permissões `comm.*`:** o conjunto canônico (`comm.template.criar/editar/publicar/ler`, `comm.mensagem.enviar/ler`, `comm.roteamento.editar`, `comm.canal.configurar`) precisa ser confirmado no RBAC global (`shared/rbac/permissoes.md`).
- **Acionamento por JRNY:** o contrato exato pelo qual JRNY pede um disparo (API síncrona vs evento de comando) será fixado quando JRNY for arquitetado; COMM expõe `POST /api/v1/messages` como ponto de acoplamento estável.
- **Produtor do índice `communication-events`:** se COMM projeta direto (best-effort) ou se INTL consome os eventos e indexa — MVP assume projeção direta por COMM (simetria com ASST→`assets`), reconciliável.

## 3. Suposições a Validar

1. Anexos/mídia são **referenciados por URL** no MVP — COMM não hospeda upload.
2. Disparo aceito de forma assíncrona (`202` + worker) é adequado à UX; envio "instantâneo" síncrono não é requisito do MVP.
3. Um provedor por canal por empresa no MVP (least-cost/múltiplos provedores do mesmo canal é pós-MVP).
4. TechLab AI expõe `document_composition` adequado a compor copy de mensagem (marketing/educação) em pt-BR.
5. O índice Elastic `communication-events` é **fact** (append-only), reconstruível de `evento_entrega`.
6. Read receipts (`LIDA`) dependem do suporte do canal/provedor; ausência não quebra o ciclo de vida (estado para em `ENTREGUE`).
7. Os 4 canais do MVP (WhatsApp/Email/Telegram/SMS) cobrem o uso inicial; novos canais são novos adapters.

## 4. Dependências Críticas

| Dependência | Estado | Bloqueia |
|---|---|---|
| **WRKS** (identidade/RBAC/AccessDecision) | vision+specs OK; scaffold pendente | Autorização `comm.*` em runtime (não bloqueia a arquitetura/scaffold de COMM). |
| **ASST** (`AssetQueryClient`) | vision→scaffold OK | Vínculo template↔asset em runtime (não bloqueia specs/scaffold; contrato Feign estável). |
| **MIG** (schema `emp_<slug>`) | scaffold OK | Execução local (`bootRun`) — não bloqueia specs/scaffold. |
| **TechLab AI** (`document_composition`) | P3 bloqueado (placeholder) | Detalhamento fino do contrato do Template Studio nas specs; geração de DTOs no scaffold. |
| **Provedores de canal** | externos (config por empresa) | Envio real em runtime; specs modelam a interface, config concreta é operacional. |
| **Elastic** índice `communication-events` | declarado em `project-context.json` | Analytics/rastreio; contrato em `elastic-data-contract.md`. |
| **REG/GWY** | scaffold OK | Discovery/edge em runtime. |
| **JRNY** (acionamento) | não arquitetado | Gatilho automático por jornada (COMM expõe API estável; não bloqueia a pipeline de COMM). |

> **Nota para o autopilot:** as dependências de WRKS/ASST/JRNY são de **runtime/contrato**, não de
> arquitetura. A pipeline vision→specs→backlog→scaffold de COMM pode prosseguir mesmo com JRNY
> ainda não arquitetado. O contrato fino da TechLab AI (`document_composition`) e os contratos dos
> provedores de canal permanecem como gaps até serem pinados — as specs devem modelar contra a
> interface esperada (`CanalEnvioPort`, `ComposicaoIaPort`) e marcar o ponto exato de acoplamento.

---

## Referências

- `01-architectural-vision.md` (§5 Out of Scope) · `04-backend-architecture-direction.md`
- `adr/ADR-003-messaging-strategy.md` · `adr/ADR-005-channel-adapter-pattern.md`
- `docs/architecture/integrations/techlab-ai-integration.md` (placeholder — P3)
