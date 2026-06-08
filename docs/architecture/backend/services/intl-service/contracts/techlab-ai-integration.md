# TechLab AI Integration — intl-service (INTL)

> INTL delega **todo raciocínio de IA** à TechLab AI (HTTP). **Nunca** chama provedor de IA
> diretamente (RULE do monorepo). Capabilities: **`knowledge`** (embeddings + recuperação/composição
> RAG) e **`orchestration`** (composição da resposta do copiloto). DTOs **gerados** de
> `integrations/techlab-ai/openapi.json` (não escritos à mão) — `openapi.json` ainda vazio (P3).

## 1. Capabilities consumidas

| Capability | Uso em INTL | Caminho degradável? |
|---|---|---|
| `knowledge` | Gerar embedding de nó/pergunta; recuperação/ranqueamento RAG sobre evidência. | Embedding de nó: **não** (retorna `503` p/ retry). Recuperação no Copilot: **sim** (degrada). |
| `orchestration` | Compor a resposta do copiloto a partir da evidência *grounded* recuperada. | **Sim** — falha → modo recuperação-apenas (`DEGRADADA`). |
| `analytics` | *(pós-MVP)* insights/sumarização analítica. | n/a no MVP. |

## 2. Operações (porta → cliente HTTP)

Portas de saída (`application.port.out`), implementadas em `infrastructure.clients.TechLabAiClient`:

| Porta | Operação lógica | Request (resumo) | Response (resumo) | Fallback |
|---|---|---|---|---|
| `KnowledgePort.embed(texto)` | embedding | `{ texto, empresa }` | `{ vetor[], modelo }` | indexação: `503`; copilot: usa busca textual. |
| `KnowledgePort.retrieve(pergunta, topK)` | recuperação RAG (via Elastic + reranking) | `{ pergunta, topK, empresa }` | `{ hits: [{ documentoId, indice, trecho, score }] }` | usa `SearchPort` direto (sem rerank IA). |
| `OrchestrationPort.compose(pergunta, evidencia)` | composição da resposta | `{ pergunta, evidencia[], empresa }` | `{ texto, citacoes[], modelo, custoTokens }` | modo recuperação-apenas (`DEGRADADA`). |

> A recuperação primária ocorre via `SearchPort` (Elasticsearch). A capability `knowledge`
> pode reordenar/expandir; a composição final é `orchestration`. Resultado bruto do Elastic
> **nunca** é passado direto a um provedor de IA — sempre via TechLab AI.

## 3. Headers de propagação

`X-Correlation-Id`, `X-Tenant` (= `empresa`), `X-Principal-Id` (usuário) propagados em toda
chamada HTTP à TechLab AI (auditoria/custo upstream).

## 4. Resiliência (Resilience4j)

| Parâmetro | Valor (MVP) |
|---|---|
| Timeout | `TECHLAB_AI_TIMEOUT_MS` (default 20000) |
| Circuit breaker | `failure-rate-threshold=50%`, `slow-call-duration=15s`, `wait-in-open=30s` |
| Retry | 1 retry em erro transitório (5xx/timeout) para `embed` na indexação; **sem** retry no caminho síncrono do copiloto (degrada direto). |

EARS:
- IF a TechLab AI excede o timeout ou o circuit breaker está aberto no caminho do copiloto, THEN THE SYSTEM SHALL retornar resposta `DEGRADADA` (recuperação-apenas) sem propagar erro ao cliente.
- IF a TechLab AI falha na geração de embedding de um nó, THEN THE SYSTEM SHALL manter o nó `RASCUNHO` e sinalizar `503` para retry.
- THE SYSTEM SHALL registrar `modelo`, `custoTokens` e `latenciaMs` de cada composição bem-sucedida.

## 5. Geração de DTOs

Os DTOs de request/response da TechLab AI são gerados por `openapi-generator-cli` a partir de
`integrations/techlab-ai/openapi.json` em `backend/services/intl-service/src/main/gen/techlabai/dtos/`.
Enquanto o `openapi.json` estiver vazio (P3 pendente), as portas são definidas contra os contratos
lógicos acima; os DTOs concretos entram no sync (`scripts/sync-techlab-ai.py`).
