# ADR-002 — Fronteira: single service (template + roteamento + disparo + entrega coesos)

**Status:** accepted

## Contexto

COMM cobre catálogo de templates, Template Studio (composição via IA), regras de roteamento,
disparo multicanal através de adapters de canal e rastreio do ciclo de vida de entrega.
Poderíamos decompor (ex.: um "serviço de envio" separado do "catálogo de templates", ou um
serviço por canal), mas isso introduz coordenação distribuída cedo demais.

## Decisão

Implementar COMM como **um único serviço** (`comm-service`, `com.journeyos.comm`), default do
monorepo. O Template Studio é um **caso de uso interno** (orquestra TechLab AI) e os adapters de
canal são **detalhe de infraestrutura** sob um port único (`CanalEnvioPort`), não serviços
separados. A coesão entre `Template` (renderizado em) `Mensagem` (roteada por) `RegraRoteamento`
favorece transações locais e consistência forte da máquina de entrega.

## Alternativas consideradas

- **Um serviço por canal (whatsapp-service, email-service, ...):** isolaria provedores, mas multiplicaria contratos internos, duplicaria roteamento/idempotência e exigiria orquestração distribuída sem ganho no MVP. Rejeitada — canais são adapters, não serviços (ver `ADR-005`).
- **Serviço de "envio" separado do "catálogo":** separaria carga de disparo da gestão de template, mas exigiria sincronizar template/regra entre serviços; complexidade distribuída sem necessidade no volume inicial. Rejeitada (reavaliar se a carga de disparo justificar escala independente).
- **Delegar todo o envio a INTL (Integrations):** viável pós-MVP, mas adiciona um salto de rede e INTL ainda não está arquitetado. Adiada.

## Consequências

**Positivas:** transações locais para a máquina de entrega; deploy/observabilidade simples; menos contratos internos; roteamento e idempotência num só lugar.

**Negativas:** a carga de disparo (workers de canal) compartilha o processo do CRUD — mitigado por outbox + worker assíncrono, circuit breaker/timeout por adapter e, se necessário, escala horizontal do serviço (ver `ADR-003`).

## Referências

- `04-backend-architecture-direction.md` (§2 Service Boundary)
- `adr/ADR-005-channel-adapter-pattern.md`
- ADR global: `docs/architecture/backend/adr/ADR-002-modular-monolith.md`
