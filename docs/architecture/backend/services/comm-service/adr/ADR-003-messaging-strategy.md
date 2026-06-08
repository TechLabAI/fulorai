# ADR-003 — Mensageria + IA: disparo async (Kafka/outbox + worker) + composição sync resiliente (TechLab AI)

**Status:** accepted

## Contexto

COMM precisa (a) notificar outros módulos quando uma mensagem é enfileirada/enviada/entregue/falhada,
(b) **enviar** mensagens a provedores externos que têm latência, rate-limit e indisponibilidade,
e (c) compor copy via TechLab AI no Template Studio. São naturezas diferentes: notificação de
domínio (desacoplada), execução de envio (precisa absorver falha do provedor sem derrubar o
request) e orquestração de capacidade externa com resposta esperada na UX.

## Decisão

- **Eventos de domínio → assíncronos via Kafka/AWS MSK** com padrão **outbox** + idempotência:
  `journey-os.mensagem.enfileirada`, `journey-os.mensagem.enviada` (evento-âncora),
  `journey-os.mensagem.entregue`, `journey-os.mensagem.falhada`. Consumidores (JRNY/SALE/INTL)
  reagem sem acoplamento síncrono. COMM consome `journey-os.modelo.acesso.alterado` (invalida
  cache de AccessDecision), `journey-os.empresa.provisionada` (seed de canais/templates),
  `journey-os.asset.versao.publicada` (sinaliza template vinculado) e
  `journey-os.lead.segmento.alterado` (reavalia roteamento).

- **Disparo → assíncrono (outbox + worker):** `POST /api/v1/messages` valida, renderiza o
  conteúdo (snapshot imutável), persiste `Mensagem` em `PENDENTE`, grava na outbox **na mesma
  transação** e retorna `202 Accepted` (`ENFILEIRADA`). Um **worker** lê a outbox e chama o
  provedor através do `CanalEnvioAdapter` correspondente, com **timeout + circuit breaker + retry
  com backoff** (Resilience4j). Isso desacopla a UX da latência/rate-limit do provedor e torna o
  envio idempotente por `chave_idempotencia`. Após N falhas → DLQ para reprocesso.

- **Callbacks de entrega (webhooks) → assíncronos (inbound):** o provedor confirma
  entrega/leitura quando ocorre; o endpoint `/api/v1/webhooks/{canal}` (autenticado por
  assinatura do provedor) normaliza o payload em `EventoEntrega` e avança o estado.

- **Template Studio (TechLab AI `document_composition`) → síncrono com proteção Resilience4j**
  (timeout + circuit breaker + retry limitado) e **fallback graceful**: TechLab AI indisponível →
  o endpoint do Studio retorna degradação explícita (ProblemDetail) sem afetar CRUD de
  template/roteamento/disparo. Composições longas podem migrar para **assíncrono** pós-MVP.

- **Projeção Elastic (`communication-events`) → síncrona best-effort**, não bloqueia o disparo
  (projeção reconciliável a partir de `evento_entrega`).

## Alternativas consideradas

- **Envio síncrono no request (sem worker):** simples, mas acopla a UX à latência/falha do provedor e estoura timeouts em rate-limit. Rejeitada — disparo é via outbox + worker.
- **Composição IA também assíncrona desde o MVP:** melhor para picos, mas complica a UX (polling/notificação) sem necessidade no volume inicial. Adiada (pós-MVP).
- **Notificar consumidores via Feign síncrono:** acoplaria COMM aos consumidores e propagaria falhas. Rejeitada — notificação é via evento; leitura é via API.

## Consequências

**Positivas:** disparo resiliente e idempotente; UX desacoplada do provedor; publicação auditável; falha de IA ou de provedor não derruba o hub.

**Negativas:** complexidade de outbox/worker/idempotência e de DLQ; composição síncrona limita o tamanho/tempo da geração no MVP (mitigado por timeout e plano async pós-MVP).

## Referências

- `docs/architecture/backend/standards/platform-patterns.md` (Kafka, outbox, Feign+Resilience4j, DLQ)
- `docs/architecture/integrations/techlab-ai-integration.md` (`document_composition`)
- `adr/ADR-005-channel-adapter-pattern.md` (o worker chama o adapter de canal)
- ADR global: `docs/architecture/backend/adr/ADR-003-multi-tenancy.md` (contexto de plataforma)
