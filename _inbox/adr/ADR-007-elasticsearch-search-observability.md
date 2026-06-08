# ADR-007 — Elasticsearch como camada de busca/analytics/observabilidade/RAG (nunca banco primário)

> **Data:** 2026-06-04
> **Status:** draft (BA)
> **Decisor:** Arquiteto (Danilo Amaral) — pendente de promoção

---

## Contexto

O Journey OS precisa de busca textual em escala (leads, jornadas, assets),
analytics operacional (Revenue Per Journey, conversão por jornada, top assets),
observabilidade desde o MVP (APM, logs, métricas de workers, health de
integrações — OPS-001) e retrieval em escala para o RAG do Copilot (ADR-002).
PostgreSQL/pgVector (ADR-006) é o canônico, mas não é o motor ideal para busca
full-text em escala, agregações analíticas pesadas nem observabilidade.

**Elasticsearch NÃO é motor default do framework `techlab-architecture`** — sua
adoção exige justificativa forte. Ela vem do documento
`journey-os-elk-entry-points-v2.md` (§3 stack: Elastic + Kafka + TechLab AI),
que mapeia entradas onde Elastic agrega valor (observabilidade como Entrada 1 de
prioridade muito alta; avaliação de retrieval do Copilot; analytics de jornada/
receita). O princípio §2.2 / TECH-003 é inviolável: **Elastic recebe apenas
projeções de leitura via outbox/Kafka, reindexáveis a partir do canônico —
nunca é banco primário.**

A decisão: **qual motor de busca/analytics/observabilidade**, mantendo Postgres
canônico?

---

## Opções consideradas

### Opção A — Elasticsearch (busca + analytics + observabilidade + RAG), via projeção (DECIDIDA)
- **Vantagens:**
  - Um único motor cobre os **quatro** usos do Journey OS: busca full-text,
    agregações analíticas, stack de observabilidade (Elastic APM/Kibana, OPS-001)
    e retrieval em escala para o RAG (ELK v2 §3).
  - Recebe projeções via outbox→Kafka (ADR-008) → indexer (Framing §6.13);
    **reindexável** a partir do canônico (não é fonte de verdade).
  - Kibana cobre observabilidade e dashboards operacionais sem ferramenta extra.
- **Desvantagens:**
  - Custo operacional/infra relevante (cluster Elastic) — atenção FIN-001.
  - Motor não-default do framework: sem scaffold pronto, exige integração e
    disciplina (indexer, lifecycle policies, aliases por tenant).
  - Eventual consistência entre canônico e índice (lag de projeção).
- **Custo:** médio-alto operacional.

### Opção B — Só PostgreSQL (full-text `tsvector` + pgVector), sem Elastic
- **Vantagens:**
  - Um datastore a menos; menor custo de infra inicial; sem lag de projeção.
- **Desvantagens:**
  - Full-text e agregações analíticas em escala degradam no mesmo Postgres que
    serve a carga transacional — contenção de recursos.
  - **Não resolve observabilidade** (APM/logs/health de integrações), que é
    requisito de MVP (OPS-001) — precisaria de outra stack mesmo assim.
  - RAG em escala (filtros + agregações sobre milhões de eventos) é fraco.
- **Custo:** baixo inicial, alto risco de não atender observabilidade/escala.

### Opção C — OpenSearch (fork open-source do Elastic)
- **Vantagens:**
  - Licença Apache 2.0; evita restrições de licença do Elastic; APIs próximas.
- **Desvantagens:**
  - Ecossistema/observabilidade (APM, integrações) menos maduro que o Elastic;
    o doc de referência (ELK v2) foi desenhado para Elastic.
  - Compatibilidade de clients/recursos pode divergir ao longo do tempo.
- **Custo:** similar; risco de maturidade.

---

## Decisão

Escolhida: **Opção A — Elasticsearch como camada de busca/analytics/
observabilidade/RAG, alimentada por projeção via outbox→Kafka, nunca banco
primário**.

### Índices declarados (registro — espelha handoff §7.1 / `stack.elastic.indices`)

Classes: **dimension** (busca de entidade) · **fact** (eventos/série temporal) · **operational** (observabilidade, OPS-001). `domainContext` = módulo do registry (Framing §11.2). Alimenta o P2 (`index-design-*` / `query-capability-*`). Origem: ELK v2 §5 + Framing §9.2.

| slug | classe | domínio | release |
|---|---|---|---|
| `leads` | dimension | LEAD | MVP+ |
| `assets` | dimension | ASST | MVP+ |
| `knowledge-nodes` | dimension | INTL | V3 |
| `journey-events` | fact | JRNY | MVP |
| `routing-decisions` | fact | JRNY | MVP+ |
| `communication-events` | fact | COMM | MVP |
| `revenue-events` | fact | SALE | V2 |
| `campaign-events` | fact | SALE | V2 |
| `ai-copilot-events` | fact | INTL | MVP+ |
| `app-logs` | operational | INTL | MVP |
| `traces` | operational | INTL | MVP |
| `metrics` | operational | INTL | MVP |
| `integration-logs` | operational | INTL | MVP |
| `audit-events` | operational | WRKS | MVP+ |

**Recorte MVP** (coerente com D3/FIN-001 — Elastic só observabilidade + eventos críticos): `journey-events` + `communication-events` + operacionais; busca de produto (`leads`/`assets`) no MVP+. Todo índice carrega o discriminador de tenant (ADR-003).

---

## Justificativa

1. **Quatro necessidades, um motor.** O Journey OS tem busca, analytics (Revenue
   Per Journey), observabilidade de MVP (OPS-001) e RAG em escala. Resolver os
   quatro com Elastic+Kibana é mais barato e coeso que somar Postgres-FTS + uma
   stack de APM separada + um motor de agregação à parte. Justifica adotar um
   motor **não-default** (ELK v2 §3).

2. **Observabilidade é requisito de sobrevivência (OPS-001, LBC §12).** Por
   depender de integrações externas (WhatsApp/Email/Ads), a operação não pode
   ficar cega a falhas de workers, filas e webhooks. Elastic APM/Kibana é a
   Entrada 1 (prioridade muito alta) do doc ELK v2.

3. **TECH-003 mantido por construção.** Como Elastic só recebe projeções via
   outbox→Kafka (ADR-008) e é reindexável do canônico (ADR-006), a verdade nunca
   migra para fora do Postgres; o índice pode ser destruído e reconstruído.

---

## Trade-offs aceitos

- **Perdemos:** simplicidade/custo de um datastore a menos. Justificativa:
  Postgres sozinho não atende observabilidade nem analytics em escala; mitigamos
  custo entrando Elastic só por observabilidade + eventos críticos no MVP
  (FIN-001), com lifecycle policies — não indexando tudo cedo.
- **Perdemos:** consistência imediata (há lag de projeção). Justificativa: busca/
  analytics/observabilidade toleram eventual consistency; o canônico (ADR-006)
  serve leitura forte quando necessário.
- **Perdemos:** o scaffold pronto de um motor default. Justificativa: o valor dos
  quatro usos cobertos supera o custo de integrar um motor não-default.

---

## Como reverter se a decisão se mostrar errada

Como Elastic **não é fonte de verdade**, removê-lo não perde dado:
1. Desligar o `ElasticIndexingWorker` (consumer Kafka).
2. Substituir busca por Postgres FTS e analytics por queries/DW; observabilidade
   por outra stack (ex.: Grafana/Loki/Tempo).
3. Destruir o cluster Elastic.

**Custo estimado:** semanas para reimplementar busca/analytics/observabilidade
em substitutos; **zero perda de dado canônico**. A reversibilidade é justamente o
benefício de Elastic ser camada de projeção.

---

## Sinais que indicariam que está errada

- Custo do cluster Elastic dominando o orçamento de infra (>X% de FIN-001) sem
  uso analítico/observabilidade que justifique, por meses.
- Lag de projeção (outbox→Kafka→indexer) consistentemente alto degradando busca/
  Copilot a ponto de usuários perceberem dados defasados.
- Volume de dados indexados crescendo sem lifecycle policy efetiva (custo de
  storage descontrolado) — sinal de indexar cedo/demais (risco LBC §12).

---

## Consequências

- **Em código:** `ElasticIndexingWorker` (Framing §6.13) projeta eventos para
  índices `lead-search-*`, `journey-events-*`, `revenue-events-*`,
  `asset-search-*`, `communication-events-*`, `knowledge-nodes-*`,
  `routing-decisions-*`, `ai-copilot-events-*`; todo documento carrega o
  discriminador de tenant (ADR-003).
- **Em IA:** RAG híbrido lê Elastic (escala/filtros) + pgVector (preciso, ADR-006),
  filtrado por workspace (ADR-002).
- **Em operação:** Kibana para observabilidade (OPS-001) e dashboards; lifecycle/
  retention policies por índice (FIN-001).

---

## Referências

- LBC §5.2 (analytics/ROI), §8 (RAG), §12 (custo da stack, risco de cegueira operacional)
- Framing §2.2 (Elastic nunca primário), §2.7 (observabilidade), §5.6 (Search/Analytics/Obs Layer), §6.13, §9.2
- `journey-os-elk-entry-points-v2.md` §3 (stack), Entrada 1 (observabilidade)
- Constraints: TECH-003, OPS-001, FIN-001
- ADRs relacionados: ADR-006 (canônico/reindexável), ADR-008 (projeção via outbox→Kafka),
  ADR-003 (discriminador de tenant no índice), ADR-002 (RAG híbrido)
