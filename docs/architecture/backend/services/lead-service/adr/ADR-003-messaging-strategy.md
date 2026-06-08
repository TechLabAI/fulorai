# ADR-003 — Messaging Strategy (eventos `lead.*` via Kafka/AWS MSK)

**Status:** accepted

## Contexto

LEAD precisa notificar módulos a jusante (JRNY, SALE, COMM, INTL) quando um lead é capturado,
qualificado, tem score atualizado ou muda de segmento. Esses módulos ainda não existem; o contrato
de integração deve desacoplar produtor de consumidores. O Journey OS define um event bus de plataforma.

## Decisão

Usar **Kafka / AWS MSK** como event bus para os eventos de domínio do LEAD, de forma **assíncrona**:

- **Produz:** `journey-os.lead.capturado`, `journey-os.lead.qualificado` (âncora),
  `journey-os.lead.score.atualizado`, `journey-os.lead.segmento.alterado`.
- **Consome:** `journey-os.empresa.provisionada` (seed por tenant) e
  `journey-os.modelo.acesso.alterado` (invalidação de cache de AccessDecision), ambos de WRKS.
- Produtores/consumidores ficam em `infrastructure.messaging/{producer,consumer}`; o domínio
  publica via `LeadEventPublisherPort` (porta out), sem conhecer Kafka.
- Eventos carregam **IDs e dados não-sensíveis** (sem PII desnecessária — LGPD); payload versionável.

Interações **síncronas** (qualificação, scoring, AccessDecision, assist TechLab AI) **não** usam
mensageria — ver `04-backend-architecture-direction.md` §6.

## Alternativas consideradas

- **ActiveMQ Artemis (JMS)**: citado em templates genéricos da plataforma, mas `project-context.json`
  e o precedente de WRKS definem **Kafka/AWS MSK** como o bus do Journey OS. Rejeitada por divergir da
  decisão de plataforma.
- **Integração síncrona (Feign) com os módulos a jusante**: acoplaria LEAD a serviços que ainda não
  existem e quebraria o golden path se um consumidor caísse. Rejeitada.

## Consequências

**Positivas:** LEAD não conhece seus consumidores; novos módulos assinam eventos sem mudar LEAD;
resiliência (consumidor offline não derruba a qualificação).

**Negativas:** consistência eventual a jusante; necessidade de contrato de evento versionado e de
idempotência no consumo. Aceito; idempotência já é princípio do domínio (ADR-005).

## Referências

- `project-context.json` (`stack.messaging.engine = Kafka (AWS MSK)`)
- `docs/architecture/backend/standards/platform-patterns.md`
- `events/event-catalog.md` (gerado nas specs)
