# ADR-003 — Mensageria + IA: roteamento dirigido por evento (Kafka) + assist sync resiliente (TechLab AI)

**Status:** accepted

## Contexto

JRNY precisa (a) **reagir** a sinais de domínio (lead qualificado, score/segmento atualizados) e
**notificar** outros módulos quando um lead é roteado/avança/conclui, e (b) **consultar** a
TechLab AI (`orchestration`) para recomendar o próximo estágio. São naturezas diferentes:
notificação/gatilho de domínio (desacoplado) vs. orquestração de uma capacidade externa (com
resposta esperada na janela da decisão, porém **dispensável**).

## Decisão

- **Gatilhos e eventos de domínio → assíncronos via Kafka/AWS MSK** com **idempotência** (consumo) e **outbox** (produção):
  - **Consome:** `journey-os.lead.qualificado`, `journey-os.lead.score.atualizado`,
    `journey-os.lead.segmento.alterado` (LEAD → gatilho de roteamento);
    `journey-os.asset.versao.publicada` (ASST → atualiza referência de conteúdo);
    `journey-os.modelo.acesso.alterado` (WRKS → invalida cache AccessDecision);
    `journey-os.empresa.provisionada` (WRKS → seed de jornadas default).
  - **Produz:** `journey-os.jornada.publicada`, `journey-os.lead.roteado` (âncora),
    `journey-os.estagio.transicionado`, `journey-os.jornada.concluida`. Consumidores
    (COMM/SALE/INTL) reagem sem acoplamento síncrono.
- **Assist de IA (TechLab AI `orchestration`) → síncrono com proteção Resilience4j**
  (timeout curto + circuit breaker + retry limitado) e **fallback determinístico**: se a TechLab
  AI estiver indisponível/lenta, o Routing Engine decide **somente com as regras versionadas** e
  a decisão registra `assist_ia=INDISPONIVEL`. O assist **nunca** está no caminho crítico.
- **Indexação Elastic (`journey-events`/`routing-decisions`) → síncrona best-effort**, não bloqueia a decisão (projeção reconciliável).

## Alternativas consideradas

- **Assist de IA obrigatório/bloqueante:** acoplaria a decisão à disponibilidade da TechLab AI e tornaria o roteamento frágil. Rejeitada — a IA aprimora, não habilita, o roteamento.
- **Roteamento por polling do estado do lead:** simples, mas reativo com atraso e custoso. Rejeitada em favor de gatilhos por evento.
- **Notificar COMM/SALE por Feign (síncrono):** acoplaria JRNY aos consumidores e propagaria falhas de execução à decisão. Rejeitada — notificação é via evento; leitura adicional é via Feign `JourneyQueryClient`.

## Consequências

**Positivas:** roteamento reativo e desacoplado; decisões auditáveis; resiliente a falha de IA; consumidores independentes.

**Negativas:** complexidade de idempotência/outbox; necessidade de fixar o contexto de empresa a partir do payload do evento no consumo; janela de timeout do assist a calibrar.

## Referências

- `docs/architecture/backend/standards/platform-patterns.md` (Kafka, outbox, Feign+Resilience4j)
- `docs/architecture/integrations/techlab-ai-integration.md` (`orchestration`)
- `adr/ADR-005-routing-engine-model.md` (fallback determinístico)
- ADR global: `docs/architecture/backend/adr/ADR-003-multi-tenancy.md` (contexto de plataforma)
