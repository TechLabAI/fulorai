# 02 — Architecture Blueprint — COMM (Communication Hub)

> Como COMM se posiciona no ecossistema Journey OS: fronteiras, atores, fluxos e camadas.

## 1. System Boundary

COMM (`comm-service`, `com.journeyos.comm`) é dono do **ciclo de vida da comunicação** dentro de
um workspace (`empresa`): templates, roteamento, disparo multicanal e rastreio de entrega. A
fronteira **inclui**:

- O agregado `Template` (catálogo de templates versionados + Template Studio).
- O agregado `Mensagem` (disparo) e suas `EventoEntrega` (trilha do ciclo de vida).
- O agregado `RegraRoteamento` (resolução canal/template por condição).
- A configuração `ConfigCanal` por empresa (provedor + identidade + referência de credencial).
- Os **adapters de canal** (WhatsApp/Email/Telegram/SMS) sob o port `CanalEnvioPort`.
- A projeção do ciclo de vida no índice Elastic `communication-events`.

A fronteira **exclui** (pertence a outros donos):

- Identidade, RBAC, contexto de tenant → **WRKS** (COMM apenas consome `AccessDecision`/JWT).
- Provisionamento de schema `emp_<slug>` → **MIG/WRKS**.
- Conteúdo dos assets (copy aprovada) → **ASST** (COMM consome assets publicados via Feign).
- Quem/quando acionar a comunicação (regra de jornada) → **JRNY** (COMM executa o disparo, não decide a jornada).
- Capacidade de IA (modelos, prompts, providers) → **TechLab AI** (consumida via HTTP).

## 2. External Actors and Systems

| Ator/Sistema | Tipo | Interação com COMM |
|---|---|---|
| **HEAD_GROWTH / SDR / INFOPRODUTOR** | humano (via GWY → FE) | CRUD de templates, Template Studio, regras de roteamento, disparo 1:1, consulta de status, config de canal. |
| **WRKS** | serviço (sync) | Valida JWT (JWKS) + `POST /access/evaluate` para autorização `comm.*`. |
| **ASST** | serviço (sync — Feign `AssetQueryClient`) | Lê assets **publicados** usados como fonte de conteúdo de template. |
| **JRNY / SALE / LEAD** | serviço (sync + async) | **Acionam** disparos (estágio de jornada, oferta, gatilho) via API/eventos. |
| **TechLab AI** | serviço externo (sync HTTP) | `document_composition` (Template Studio — compor/editar copy). |
| **Provedores de canal** (Meta WABA / SES / SendGrid / Telegram Bot / Twilio / SNS) | externo (sync HTTP + webhooks) | Envio efetivo (via adapters) + callbacks de entrega/leitura. |
| **Elasticsearch** | infra (sync, direct java client) | Índice `communication-events` (fact) — projeção do ciclo de vida. |
| **PostgreSQL** (`emp_<slug>`) | infra | Fonte da verdade de templates/mensagens/regras/eventos do tenant. |
| **Kafka / AWS MSK** | infra (async) | Produz/consome eventos `journey-os.*`. |
| **MIG** | serviço | Prepara o schema do tenant (precondição). |

## 3. End-to-End Flows

### Golden path — *Rotear → renderizar → enfileirar → enviar → confirmar entrega*

```
JRNY (ou SDR/SALE)
  → POST /api/v1/messages            (pede disparo: leadId, contexto, variáveis, chaveIdempotencia)
COMM
  → RegraRoteamento resolve canal (preferido/fallback) + template ATIVO
  → renderiza conteúdo (template + variáveis) → snapshot imutável
  → persiste Mensagem (PENDENTE) + grava em outbox → 202 Accepted
  → emite journey-os.mensagem.enfileirada                 (estado → ENFILEIRADA)
  → worker assíncrono seleciona o CanalEnvioAdapter pelo canal/provedor
        → adapter chama o provedor (Meta/SES/Telegram/Twilio) com Resilience4j
        → sucesso: estado → ENVIADA; grava EventoEntrega(ENVIADA)
        → emite journey-os.mensagem.enviada (ÂNCORA) + projeta em Elastic communication-events
Provedor (assíncrono, webhook)
  → POST /api/v1/webhooks/{canal}    (delivery receipt / read receipt)
        → estado → ENTREGUE / LIDA; grava EventoEntrega; emite journey-os.mensagem.entregue
JRNY/SALE/INTL
  → consomem os eventos (avança jornada, atribui toque, indexa o fato)
```

### Fluxos alternativos

- **Falha de envio:** o provedor rejeita ou esgota retries → estado `FALHADA`; grava `EventoEntrega(FALHADA, motivo)`; emite `journey-os.mensagem.falhada`. Worker aplica backoff (1s/5s/30s) antes de declarar falha; DLQ para reprocesso manual.
- **Fallback de canal:** canal preferido indisponível/sem endereço do lead → roteamento usa o `canal_fallback` configurado; se nenhum canal resolver, falha **explícita** (sem envio silencioso).
- **Composição manual (sem IA):** Marina escreve/edita o corpo do template diretamente (sem Template Studio); demais fluxos idênticos.
- **TechLab AI indisponível:** Template Studio retorna `503`/ProblemDetail de degradação; CRUD de template, roteamento e disparo **não** são afetados (ver `ADR-003`).
- **Asset atualizado:** ASST publica nova versão de um asset vinculado a um template → COMM consome `journey-os.asset.versao.publicada` e sinaliza o template para revisão (não republica automático).
- **Idempotência:** segundo `POST /messages` com a mesma `chave_idempotencia` retorna a mensagem já criada (não dispara de novo).

## 4. Internal Boundaries (camadas hexagonais)

```
api/            controllers REST (/api/v1/templates/**, /messages/**, /routing-rules/**,
                /channels/**, /webhooks/{canal}), DTO records, @RestControllerAdvice (ProblemDetail)
application/    use cases (@Service, @Transactional): CriarTemplate, ComporNoStudio, RotearMensagem,
                EnviarMensagem, RegistrarEventoEntrega, ConfigurarCanal, BuscarStatus; ports in/out
domain/         Template, Mensagem, EventoEntrega, RegraRoteamento, ConfigCanal, Canal (enum),
                EstadoEntrega (state machine), TipoTemplate — POJO puro; domain services
                (resolução de roteamento, transição de entrega, render de template) — zero Spring/JPA
infrastructure/ persistence (JPA emp_<slug>), clients (Feign WRKS + ASST; client TechLab AI),
                channels/ (adapters WhatsApp/Email/Telegram/SMS sob CanalEnvioPort),
                messaging (producer/consumer Kafka, outbox), search (Elastic adapter
                `communication-events`), security (EmpresaContextHolder, JWT), config (DomainServiceConfig)
```

Regras ArchUnit RULE-01..09 (ver `ADR-001` e `hexagonal-patterns.md`).

## 5. Cross-cutting Concerns

- **Security / multi-tenancy:** todo request carrega JWT (validado contra JWKS de WRKS); `EmpresaContextHolder.require()` fixa o `emp_<slug>`; autorização por permissões `comm.<recurso>.<acao>` via `AccessDecision` (cache curto, invalidado por `modelo.acesso.alterado`). Webhooks de provedor autenticados por assinatura/segredo do provedor (não por JWT de usuário).
- **Observability:** MDC com `correlationId` + `empresaId`; logs estruturados (SLF4J/Lombok); métricas de latência por canal/provedor, taxa de entrega/falha, profundidade da fila de disparo.
- **Resiliência:** chamadas a provedores e à TechLab AI com timeout + circuit breaker (Resilience4j) + retry com backoff; disparo via outbox + worker (desacopla do request); idempotência por chave (ver SPEC-05).
- **LGPD:** mensagens contêm dados pessoais (telefone, e-mail, nome) → retenção/arquivamento por tenant; consentimento básico registrado; expurgo por anonimização preservando a trilha de eventos para auditoria. Credenciais de provedor nunca persistidas em claro (só `credencial_ref`).
- **Idempotência:** disparo idempotente por `chave_idempotencia`; consumo de eventos idempotente por `eventId` (`processed_events`); registro de callbacks idempotente por `(mensagem, tipo, provedor_message_id)`.

---

## Referências

- `01-architectural-vision.md` · `03-initial-domain-framing.md` · `04-backend-architecture-direction.md`
- `docs/architecture/backend/standards/hexagonal-patterns.md` · `platform-patterns.md`
- `docs/architecture/integrations/techlab-ai-integration.md` · `elastic-data-contract.md`
- `adr/ADR-005-channel-adapter-pattern.md`
