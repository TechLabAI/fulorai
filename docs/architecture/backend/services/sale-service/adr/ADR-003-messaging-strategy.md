# ADR-003 — Messaging strategy — eventos `oportunidade.*`/`compra.*` via Kafka/AWS MSK

**Status:** accepted

## Contexto

SALE é a fonte da verdade da venda e da receita. Vários módulos a jusante (INTL para analytics de
receita, COMM para pós-venda/nutrição, JRNY para o funil) precisam reagir a fatos de venda, mas
SALE não deve conhecê-los nem depender deles em runtime. A plataforma Journey OS adota **Kafka/AWS
MSK** como event bus (confirmado em `project-context.json` e nos precedentes WRKS/LEAD).

## Decisão

Comunicação a jusante por **eventos assíncronos** publicados em **Kafka/AWS MSK**, com a porta
`SaleEventPublisherPort` (out) implementada por um producer em `infrastructure.messaging.producer`.

Eventos produzidos (nomes canônicos `journey-os.<dominio>.<fato>`):
`oportunidade.criada`, `oportunidade.estagio.alterado`, `oportunidade.ganha`, `oportunidade.perdida`,
`compra.confirmada` (**âncora**), `receita.atribuida`, `ltv.atualizado`.

Eventos consumidos (consumers em `infrastructure.messaging.consumer`):
`lead.qualificado` / `lead.score.atualizado` (LEAD), `empresa.provisionada` / `modelo.acesso.alterado` (WRKS).

A dependência sync com WRKS (`AccessDecision`) permanece via Feign — não tudo é evento.

## Alternativas consideradas

- **Chamadas Feign síncronas a jusante** (SALE→INTL/COMM): acoplaria SALE à disponibilidade dos
  consumidores e inverteria a direção de dependência saudável. Rejeitada.
- **Artemis/JMS**: não é o broker de plataforma do Journey OS (que padronizou Kafka/MSK). Rejeitada.

## Consequências

**Positivas:** SALE desacoplado dos consumidores; novos consumidores entram sem tocar SALE;
escala e replay nativos do Kafka.

**Negativas:** consistência eventual a jusante; contratos de evento precisam ser versionados e
estáveis; idempotência no consumidor (LEAD→oportunidade) é responsabilidade do consumer. Aceito.

## Referências

- `docs/architecture/backend/standards/platform-patterns.md` (Kafka, MDC, outbox)
- `events/event-catalog.md` (a ser gerado em `/be-architect-specs SALE`)
- ADR-001 (porta out) · ADR-005 (eventos de receita/atribuição)
