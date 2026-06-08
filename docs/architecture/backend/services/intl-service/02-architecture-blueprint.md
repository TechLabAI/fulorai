# 02 — Architecture Blueprint — INTL

> Serviço: `intl-service` · Pacote: `com.journeyos.intl` · Porta: `8087`

## 1. System Boundary

`intl-service` é responsável por:

- **Domínio Copilot/Conhecimento:** agregados `ConversaCopiloto` e `BaseConhecimento`
  (`NoConhecimento`), persistidos em PostgreSQL `emp_<slug>` + projeção Elastic.
- **Plataforma de dados:** governança do contrato Elastic (rastreabilidade, DLQ, registro de
  índices/ILM), projeções próprias (`ai-copilot-events`, `knowledge-nodes`), leitura analítica.

Fora da fronteira: identidade/autorização (WRKS), raciocínio de IA (TechLab AI), os *facts* de
JRNY/COMM/SALE (cada módulo escreve os seus), e a ingestão de observabilidade (infra/APM).

## 2. External Actors and Systems

| Ator/Sistema | Direção | Papel |
|---|---|---|
| Usuário (`INFOPRODUTOR`/`HEAD_GROWTH`/`SDR`) | → (via GWY) | Faz perguntas ao Copilot; cura conhecimento; lê analítica. |
| **WRKS** | ← Feign / ← Kafka | AccessDecision/JWT (`AccessEvaluateClient`); eventos `empresa.provisionada`, `modelo.acesso.alterado`. |
| **TechLab AI** | → HTTP | `knowledge` (embeddings + RAG) + `orchestration` (composição). DTOs gerados de `openapi.json`. |
| **Elasticsearch** | ↔ `elastic-client-lib` | `SearchPort` (recuperação/analítica), `IndexPort` (projeções próprias + DLQ). |
| **Kafka / AWS MSK** | ← consumer | Consome `asset.versao.publicada`, `empresa.provisionada`, `modelo.acesso.alterado`. → producer: `copilot.resposta.gerada`. |
| **ASST** | ← Feign / ← Kafka | `AssetQueryClient` (conteúdo do asset publicado como fonte de conhecimento — opcional). |
| **PostgreSQL + pgVector** | ↔ JPA | Schema `emp_<slug>`: conhecimento + conversas (embedding opcional). |
| **MIG** | (pré-condição) | Prepara o schema `emp_<slug>` e o registro de índices. |

## 3. End-to-End Flows

### Golden path — pergunta ao Copilot (RAG fundamentado)

```
Usuário → GWY → intl-service POST /api/v1/copilot/conversas/{id}/perguntar
  1. CopilotService.responder(empresa, pergunta)
     - AccessEvaluateClient autoriza intl.copilot.use
     - EmpresaContextHolder resolve emp_<slug>
  2. SearchPort.search() → recupera evidência (knowledge-nodes + facts relevantes), filtrada por empresa
  3. KnowledgePort/OrchestrationPort (TechLab AI) compõe resposta a partir da evidência grounded
     - circuit breaker: se falhar → modo recuperação-apenas (resposta degradada/nao_fundamentada)
  4. Persiste mensagem_copiloto (papel=COPILOTO, conteudo, citacoes[], custo, modelo, latencia, status)
  5. IndexPort.index() → ai-copilot-events (com bloco de rastreabilidade)
  6. Publica journey-os.copilot.resposta.gerada
  7. Retorna RespostaCopilotoResponse (texto + citações + status)
```

### Fluxo — ingestão de nó de conhecimento

```
(a) Manual: POST /api/v1/knowledge/nos → NoConhecimento (RASCUNHO)
(b) Evento: asset.versao.publicada → KnowledgeIngestService ingere conteúdo publicado
  → KnowledgePort (TechLab AI) gera embedding → IndexPort.index() knowledge-nodes (status INDEXADO)
  → opcional: persiste embedding em pgvector
```

### Fluxo — leitura analítica cross-index

```
GET /api/v1/analytics/funil?periodo=... → AnalyticsService
  → SearchPort agrega facts (revenue-events/journey-events/communication-events) filtrando por empresa
  → retorna projeção consolidada (read-only; INTL não escreve esses índices)
```

### Alternativas / falhas

- **TechLab AI indisponível** → circuit breaker abre → resposta em modo recuperação-apenas
  (lista evidência sem síntese, `status=DEGRADADA`); evento ainda é emitido (custo=0, modelo=null).
- **Documento sem bloco de rastreabilidade** → `IndexPort` roteia para `journey-os_dlq`
  (`parse_status=error`), nunca indexa silenciosamente.
- **Recuperação vazia** → resposta `nao_fundamentada` explícita ("sem evidência suficiente").

## 4. Internal Boundaries (camadas hexagonais)

```
api/            controllers REST (/copilot, /knowledge, /analytics), DTOs (records), ProblemDetail
application/    CopilotService, KnowledgeIngestService, AnalyticsService, EventPlatformService
                ports/in (use cases) · ports/out (SearchPort, IndexPort, KnowledgePort,
                OrchestrationPort, AccessDecisionCachePort, IntlEventPublisherPort, AssetQueryPort)
domain/         ConversaCopiloto, MensagemCopiloto, NoConhecimento, BaseConhecimento,
                Citacao, EventoIndexado, RegistroIndice — POJOs puros + domain services
infrastructure/ persistence (JPA emp_<slug>), clients (TechLabAi HTTP, AssetQuery Feign, WRKS),
                elastic (adapter via elastic-client-lib), messaging (consumers Kafka + producer),
                security (JWT/MDC/EmpresaContextHolder), config (DomainServiceConfig)
```

## 5. Cross-cutting Concerns

- **Security/multi-tenancy:** JWT validado (JWKS WRKS); `AccessEvaluateClient` autoriza `intl.*`;
  `EmpresaContextHolder` resolve `emp_<slug>`; **toda** query Elastic filtra `empresa`.
- **Observability:** MDC (`empresa`, `traceId`, `conversaId`); métricas de custo/latência da TechLab AI;
  contadores de DLQ; `spring.jpa.open-in-view=false`.
- **Resiliência:** Resilience4j (circuit breaker + timeout + fallback) na TechLab AI e no Elastic;
  retries idempotentes no consumer Kafka; DLQ para documentos inválidos.
- **LGPD:** conversas/nós podem conter PII → `base_legal`, anonimização/expurgo; citações restritas
  ao escopo `empresa` do solicitante.
- **Auditabilidade (D-269):** bloco de rastreabilidade de 8 campos obrigatório em toda indexação.
