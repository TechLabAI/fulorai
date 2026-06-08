# ADR-008 — Event-first com outbox transacional + Kafka como backbone de eventos

> **Data:** 2026-06-04
> **Status:** draft (BA)
> **Decisor:** Arquiteto (Danilo Amaral) — pendente de promoção

---

## Contexto

O Journey OS é **event-first** (princípio §2.1): toda decisão de negócio
relevante emite um evento de domínio rastreável, e o estado é consequência dos
eventos. Esses eventos alimentam múltiplos consumers desacoplados: scoring,
routing, attribution de receita, indexação Elastic (ADR-007) e triggers de IA
(ADR-002). Fluxos críticos (captura/qualificação de lead, próxima melhor ação,
progressão de jornada, atribuição de receita — Framing §8) dependem dessa malha.

Duas decisões: **(1) como garantir que o evento seja publicado de forma
consistente com a transação que mudou o dado** (problema dual-write) e **(2) qual
backbone de mensageria**. Constraint TECH-005 define outbox→Kafka como padrão,
mas é **negociável com exceção documentada** — em particular, FIN-001 alerta que
Kafka + Elastic + IA somam custo relevante e o MVP deve evitar over-engineering.

Kafka **não é motor default do framework** — exige justificativa.

---

## Opções consideradas

### Opção A — Outbox transacional + Kafka como backbone (DECIDIDA, com adoção faseada)
- **Vantagens:**
  - Outbox grava o evento na **mesma transação** do dado canônico (ADR-006),
    eliminando dual-write; um publisher lê a outbox e publica no Kafka.
  - Kafka: log particionado, retenção/replay, alto throughput, múltiplos
    consumers independentes (scoring/routing/attribution/indexer/IA) — casa com a
    fan-out do Journey OS (Framing §5.4).
  - **Replay** permite reconstruir projeções (ex.: reindexar Elastic, ADR-007) e
    reprocessar attribution — alinhado a "estado é consequência dos eventos".
- **Desvantagens:**
  - Kafka tem custo operacional/infra relevante (cluster, ZooKeeper/KRaft) —
    peso para time enxuto (ORG-001) e orçamento (FIN-001).
  - Curva de operação (partições, consumer groups, offsets).
- **Custo:** médio-alto operacional.

### Opção B — Outbox + RabbitMQ
- **Vantagens:**
  - Broker mais simples de operar; bom para roteamento/filas de trabalho.
- **Desvantagens:**
  - Sem log persistente/replay nativo como o Kafka (mensagem consumida some) —
    perde a capacidade de reconstruir projeções/attribution a partir do histórico,
    que é central para o Journey OS.
  - Fan-out a muitos consumers independentes é menos natural que no Kafka.
- **Custo:** médio; pior fit para replay/event-sourcing-leve.

### Opção C — Outbox + polling, sem broker no MVP (adiar Kafka)
- **Vantagens:**
  - Custo de infra mínimo no MVP (FIN-001) — sem cluster de mensageria.
  - Mantém o event-first: eventos ainda gravados na outbox transacional; consumers
    leem por polling/processo agendado.
  - Migração futura para Kafka é natural (a outbox já existe).
- **Desvantagens:**
  - Sem throughput/particionamento/replay de log de um broker dedicado.
  - Polling adiciona latência e não escala para alto volume de eventos.
- **Custo:** baixo inicial; teto de escala baixo.

---

## Decisão

Escolhida: **Opção A — outbox transacional + broker Kafka desde o MVP**, **via
AWS MSK (gerenciado)** (D2, sponsor 2026-06-04). A outbox transacional garante
event-first sem dual-write; o MSK entra já no MVP (não adiado) e, sendo
gerenciado, evita operar o broker manualmente — coerente com time pleno sem SRE
(ORG-001), dentro do envelope da FIN-001 (TECH-007). O domínio (hexagonal,
ADR-004) fala com a API Kafka via port, então trocar o broker no futuro não toca
o domínio.

> Nota: a Opção B (RabbitMQ) e a Opção C (outbox+polling sem broker) seguem
> válidas como alternativas consideradas. A alternativa self-hosted (Redpanda/
> Kafka em K8s) foi considerada e **descartada** pelo sponsor — risco de operação
> com time enxuto; MSK gerenciado foi preferido (TECH-007).

---

## Justificativa

1. **Outbox é inegociável para o event-first (§2.1).** Sem ele, há dual-write
   (gravar no banco e publicar no broker em passos separados) e risco de evento
   perdido/duplicado — quebraria a rastreabilidade que é princípio do produto.

2. **Kafka pelo replay e fan-out, que o Journey OS realmente usa.** Reindexar
   Elastic (ADR-007), reprocessar attribution de receita e alimentar múltiplos
   consumers independentes são casos concretos (Framing §8) que dependem de um
   log persistente e particionado — exatamente o que diferencia Kafka de
   RabbitMQ. Isso justifica adotar um motor não-default.

3. **Custo controlado por fase (FIN-001, LBC §12).** Como a outbox desacopla a
   publicação, o Kafka pode entrar quando o volume justificar, sem
   over-engineering no piloto. O domínio (hexagonal, ADR-004) não sabe se atrás
   do port há Kafka ou polling.

---

## Trade-offs aceitos

- **Perdemos:** simplicidade de não operar broker. Justificativa: a outbox
  transacional é barata; o Kafka entra faseado conforme FIN-001.
- **Perdemos:** o roteamento/filas mais simples do RabbitMQ. Justificativa: replay
  e log persistente valem mais para reconstruir projeções/attribution.
- **Perdemos:** consistência síncrona entre domínios. Justificativa: event-first é
  assíncrono por design; consumers são eventualmente consistentes (aceitável para
  scoring/indexação/attribution).

---

## Como reverter se a decisão se mostrar errada

**De Kafka para polling/RabbitMQ (sem perder o event-first):** trocar o adapter de
publish/subscribe atrás do port; a outbox e os eventos permanecem. **Custo:**
dias a poucas semanas — baixo, porque o domínio está desacoplado (ADR-004).

**Abandonar o event-first (improvável):** removeria a rastreabilidade que é
princípio do produto; exigiria reescrever os fluxos §8. **Custo:** alto. Como
ainda **não há código de produção** (Estágio 0), o desenho pode ser ajustado
agora a custo baixo.

---

## Sinais que indicariam que está errada

- Custo do cluster Kafka desproporcional ao volume real de eventos no piloto
  (FIN-001) — sinal de que a fase de polling deveria ter durado mais.
- Lag de consumer consistentemente alto degradando scoring/routing/indexação a
  ponto de impactar a "próxima melhor ação".
- Complexidade operacional do Kafka consumindo o tempo do time enxuto (ORG-001)
  sem ganho de throughput necessário.

---

## Consequências

- **Em código:** `EventPlatform` (Framing §6.12) com EventStore + outbox publisher;
  port de publish/subscribe (adapter Kafka ou polling); consumers: scoring,
  routing, `RevenueAttributionWorker`, `ElasticIndexingWorker`, triggers de IA.
- **Em dados:** outbox na mesma transação do canônico (ADR-006); eventos carregam
  discriminador de tenant em header (ADR-003), `correlation_id`/`causation_id`.
- **Em custo:** Kafka faseado; lifecycle/retention alinhados a FIN-001.

---

## Referências

- LBC §12 (custo/complexidade da stack cedo demais; multi-tenant)
- Framing §2.1 (event-first), §5.4 (event backbone), §6.12 (EventPlatform), §8 (fluxos)
- `journey-os-elk-entry-points-v2.md` §3.1/§3.2 (event-first, Kafka)
- Constraints: TECH-005 (negociável com exceção — adiar Kafka), FIN-001, ORG-001
- ADRs relacionados: ADR-006 (outbox no Postgres), ADR-007 (indexer consome eventos),
  ADR-009 (routing reage a eventos), ADR-004 (publish/subscribe via port)
