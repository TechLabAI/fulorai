# Plano — INTL (intl-service)

## Status das prioridades
- P1 — pendente
- P2 — pendente
- P3 — pendente
- P4 — pendente
- P5 — pendente
- P6 — pendente
- P7 — pendente
- P8 — pendente
- P9 — pendente

## 0. Leitura executiva

### Papel do serviço (01-architectural-vision.md)
Camada de **inteligência e plataforma** do Journey OS: AI Copilot conversacional com respostas
**fundamentadas e citadas** (RAG: Elastic → TechLab AI), Base de Conhecimento curada, governança da
plataforma de dados Elastic (contrato de rastreabilidade/DLQ/registro de índices) e leitura
analítica cross-index. Não reindexа *facts* de outros módulos; nunca chama IA direto.

### MVP scope (01)
Copilot read-only (RESPONDIDA/NAO_FUNDAMENTADA/DEGRADADA); Base de Conhecimento
(CRUD + ingestão por asset); governança Elastic + projeções próprias (`ai-copilot-events`,
`knowledge-nodes`); analítica read-only. Anchor: `journey-os.copilot.resposta.gerada`.

### Diagnóstico inicial (06)
Riscos: dependência síncrona da TechLab AI (mitigada por CB + fallback); alucinação (mitigada por
RAG + citações); vazamento cross-tenant (filtro `empresa` obrigatório); `openapi.json` vazio (P3) →
INT-INTL-002 bloqueado; gates de compile/ArchUnit/BDD deferidos (sem Gradle no ambiente).

## 1. Estratégia geral

### Objetivo macro
Entregar o golden path do copiloto fundamentado e a governança de dados, com isolamento de tenant e
degradação graciosa, sobre o esqueleto hexagonal.

### Ordem das prioridades

| P | Título | Motivo |
|---|---|---|
| P1 | Scaffold + API surface | Base executável + contratos REST. |
| P2 | Copilot orchestration (RAG) | Golden path do evento-âncora. |
| P3 | Persistência + migrations | Estado do conhecimento/conversas. |
| P4 | Integrações externas | TechLab AI + Elastic + ASST (núcleo do RAG). |
| P5 | Security + multi-tenancy | Autorização + isolamento (inviolável). |
| P6 | Messaging | Consumo transversal + outbox do âncora. |
| P7 | Observability | Custo/latência/DLQ + health. |
| P8 | BDD e2e | Validação comportamental (19 cenários). |
| P9 | Hardening | SLAs, custo, runbook DLQ. |

> P4 sobe junto ao núcleo: sem TechLab AI + Elastic não há RAG. Persistência (P3) precede P4 para
> dar onde gravar conversas/nós.

## 2. Plano por prioridade

### Prioridade 1 — Scaffold + API surface
Status: pendente
- **Objetivo:** esqueleto hexagonal + superfície REST (`/copilot`, `/knowledge`, `/analytics`).
- **Issues:** INTL-001, INTL-002, INTL-003, INTL-004
- **Specs:** SPEC-01
- **Sequência:** scaffold → controllers/DTOs → ArchUnit.
- **Aceite:** endpoints respondem; `architectureCheck` passa.
- **Riscos:** convenção de pacote (RULE-09) — `bounded_context=intl` no generator-config.
- **Instrução:** rodar scaffold; não retornar `@Entity` em controller.

### Prioridade 2 — Copilot orchestration (RAG)
Status: pendente
- **Objetivo:** golden path "Copiloto respondeu".
- **Issues:** INTL-005, INTL-006
- **Specs:** SPEC-02
- **Sequência:** recuperação → composição → fundamentação/status → persistência → projeção → evento.
- **Aceite:** RESPONDIDA com citações; degradação sem `5xx`.
- **Riscos:** alucinação — citação ⊆ evidência obrigatória.

### Prioridade 3 — Persistência + migrations
Status: pendente
- **Issues:** INTL-007, INTL-008 · **Specs:** SPEC-04
- **Sequência:** data-model → V1 (MIG) → entities/repos/adapters → `validate`.
- **Aceite:** boot valida schema; CRUD no `emp_<slug>`.

### Prioridade 4 — Integrações externas
Status: pendente
- **Issues:** INTL-009, INTL-010, INTL-011, INT-INTL-002, INT-INTL-003, INT-INTL-004
- **Specs:** SPEC-03, SPEC-10
- **Sequência:** TechLab AI client (CB/fallback) ‖ Elastic adapter (rastreabilidade/DLQ) → ingestão.
- **Aceite:** projeção válida indexa/ inválida → DLQ; fallback verificado.
- **Riscos:** `openapi.json` vazio (P3) — INT-INTL-002 programado contra portas até o sync.

### Prioridade 5 — Security + multi-tenancy
Status: pendente
- **Issues:** INTL-012, INT-INTL-001 · **Specs:** SPEC-06
- **Aceite:** fail-closed; filtro `empresa` em toda query Elastic; teste de isolamento verde.

### Prioridade 6 — Messaging
Status: pendente
- **Issues:** INTL-013, INTL-014, INT-INTL-005, INT-INTL-006 · **Specs:** SPEC-09, SPEC-05
- **Aceite:** idempotência por `eventId`; outbox exactly-once; seed idempotente.

### Prioridade 7 — Observability + health
Status: pendente
- **Issues:** INTL-015 · **Specs:** SPEC-07
- **Aceite:** health + métricas de custo/latência/DLQ; readiness degradada (não DOWN) com CB aberto.

### Prioridade 8 — BDD end-to-end
Status: pendente
- **Issues:** INTL-016 · **Specs:** SPEC-08
- **Aceite:** 19 cenários verdes (3 status, isolamento, idempotência, DLQ).

### Prioridade 9 — Hardening
Status: pendente
- **Issues:** INTL-017 · **Specs:** SPEC-07, SPEC-10
- **Aceite:** SLA do copiloto; soft-limit de custo; runbook DLQ/replay.

## 3. Dependências externas
- WRKS (AccessDecision/JWKS + eventos de tenant), ASST (`AssetQueryClient` + evento), TechLab AI
  (`knowledge`/`orchestration`), Elasticsearch (`elastic-client-lib`), Kafka/AWS MSK, MIG (schema),
  REG (discovery). **Bloqueio:** P3 sync da TechLab AI (`openapi.json`).

## 4. Restrições arquiteturais
- ArchUnit RULE-01..08 (CLAUDE.md); camadas hexagonais; `@Transactional` só em application.service;
  base package `com.journeyos.intl` (RULE-09); nunca IA direta; `ddl-auto=validate`;
  `open-in-view=false`; INTL não escreve *facts* de outros módulos (ADR-003).

## 5. Referências
- `docs/architecture/backend/services/intl-service/{01..06}.md`, `adr/`, `contracts/`, `spec/backend/`
- `docs/architecture/integrations/{elastic-data-contract,elastic-stack-integration,techlab-ai-integration}.md`
- `docs/architecture/backend/issues/INTL-001..017.md`, `INT-INTL-001..006.md`, `issues_map-INTL.md`
