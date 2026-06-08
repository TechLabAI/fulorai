# API Contract — intl-service (INTL)

> Base path `/api/v1`. Auth OAuth2 (JWT RS256, JWKS de WRKS) + AccessDecision (`intl.*`).
> Headers obrigatórios: `Authorization: Bearer <jwt>`, `X-Correlation-Id`. Tenant via claim JWT
> (`empresa`) resolvido por `EmpresaContextHolder`. Erros em RFC 7807 (`ProblemDetail`).
> EARS guide: `docs/architecture/backend/standards/ears-notation.md`.

## 0. Convenções

- **Tenant:** derivado do claim `empresa` do JWT — **nunca** de path/body. Toda resposta opera no
  schema `emp_<slug>` resolvido.
- **Autorização:** cada endpoint exige uma permissão `intl.*` via `AccessEvaluateClient` (WRKS).
- **Correlação:** `X-Correlation-Id` propagado a TechLab AI e ao Elastic (MDC).

EARS transversais:
- IF o JWT está ausente/inválido, THEN THE SYSTEM SHALL responder `401`.
- IF o AccessDecision nega a permissão `intl.*`, THEN THE SYSTEM SHALL responder `403`.
- IF `X-Correlation-Id` está ausente, THEN THE SYSTEM SHALL gerar um e ecoá-lo na resposta.

## 1. Copilot — `/api/v1/copilot`

### 1.1 `POST /api/v1/copilot/conversas` — abrir conversa
- **Permissão:** `intl.copilot.use`
- **Request:** `{ "titulo": "string?" }`
- **Response 201:** `ConversaResponse { id, titulo, estado: "ABERTA", criadaEm }`

### 1.2 `POST /api/v1/copilot/conversas/{conversaId}/perguntar` — perguntar (RAG)
- **Permissão:** `intl.copilot.use`
- **Request:** `PerguntaRequest { "texto": "string", "topK": "int? (default 8)" }`
- **Response 200:** `RespostaCopilotoResponse { mensagemId, texto, status, citacoes: [{ documentoId, indice, trecho, score }], modelo?, custoTokens?, latenciaMs }`
- **Status semantics:** `RESPONDIDA` (fundamentada), `NAO_FUNDAMENTADA` (sem evidência suficiente), `DEGRADADA` (TechLab AI indisponível — recuperação-apenas).

EARS:
- WHEN uma pergunta é recebida, THE SYSTEM SHALL recuperar evidência filtrada por `empresa` antes de compor a resposta.
- WHEN a resposta é composta com ≥ 1 citação fundamentadora, THE SYSTEM SHALL marcá-la `RESPONDIDA` e responder `200`.
- IF a recuperação retorna evidência insuficiente, THEN THE SYSTEM SHALL marcar a resposta `NAO_FUNDAMENTADA` e responder `200` (sem alucinar fato).
- IF a TechLab AI está indisponível, THEN THE SYSTEM SHALL responder `200` com `status=DEGRADADA` (evidência recuperada, sem síntese) — nunca `5xx` por falha da IA.
- WHEN a resposta é gerada, THE SYSTEM SHALL persistir a mensagem, projetar `ai-copilot-events` e publicar `journey-os.copilot.resposta.gerada`.
- IF `conversaId` não existe na `empresa`, THEN THE SYSTEM SHALL responder `404`.

### 1.3 `GET /api/v1/copilot/conversas/{conversaId}` — histórico
- **Permissão:** `intl.copilot.read`
- **Response 200:** `ConversaDetalheResponse { id, titulo, estado, mensagens: [...] }`

## 2. Knowledge — `/api/v1/knowledge`

### 2.1 `POST /api/v1/knowledge/nos` — criar nó (manual)
- **Permissão:** `intl.knowledge.write`
- **Request:** `NoConhecimentoRequest { titulo, conteudo, tags: [string], fonte: { tipo: "MANUAL", referencia? } }`
- **Response 201:** `NoConhecimentoResponse { id, status: "RASCUNHO", versao: 1 }`

### 2.2 `POST /api/v1/knowledge/nos/{id}/indexar` — indexar/embedding
- **Permissão:** `intl.knowledge.write`
- **Response 202:** `{ id, status: "INDEXADO", versao }`

EARS:
- WHEN um nó é indexado, THE SYSTEM SHALL gerar embedding via TechLab AI `knowledge` e projetar o documento em `knowledge-nodes` com o bloco de rastreabilidade.
- IF a geração de embedding falha, THEN THE SYSTEM SHALL manter o nó em `RASCUNHO` e responder `503` (retry posterior) — nunca indexar parcialmente.

### 2.3 `GET /api/v1/knowledge/nos` — listar/buscar
- **Permissão:** `intl.knowledge.read`
- **Query:** `?q=&tag=&status=&page=&size=`
- **Response 200:** `Page<NoConhecimentoResponse>`

### 2.4 `PUT /api/v1/knowledge/nos/{id}` / `DELETE` (arquivar)
- **Permissão:** `intl.knowledge.write`
- `PUT` edita (incrementa `versao`, reindexação); `DELETE` arquiva (`status=ARQUIVADO`, sem hard-delete).

## 3. Analytics — `/api/v1/analytics` (read-only)

### 3.1 `GET /api/v1/analytics/funil` — funil consolidado
- **Permissão:** `intl.analytics.read`
- **Query:** `?periodo=&granularidade=`
- **Response 200:** `FunilResponse { etapas: [{ nome, total }], periodo }` — agrega *facts* já projetados pelos módulos (read-only).

### 3.2 `GET /api/v1/analytics/copilot` — uso/custo do copiloto
- **Permissão:** `intl.analytics.read`
- **Response 200:** `CopilotUsageResponse { totalRespostas, custoTokens, taxaFundamentadas, taxaDegradadas }`

EARS:
- THE SYSTEM SHALL filtrar toda agregação analítica por `empresa`.
- THE SYSTEM SHALL ser read-only em `/analytics` (nenhuma escrita em índice de *fact* de outro módulo).

## 4. Erros (RFC 7807)

| Status | `type` (sufixo) | Quando |
|---|---|---|
| 400 | `validation-error` | payload inválido |
| 401 | `unauthorized` | JWT ausente/inválido |
| 403 | `forbidden` | AccessDecision nega `intl.*` |
| 404 | `not-found` | conversa/nó inexistente na `empresa` |
| 409 | `conflict` | indexação concorrente do mesmo nó |
| 503 | `ai-unavailable` / `embedding-unavailable` | dependência externa indisponível em fluxo não-degradável (embedding) |

> Falha da TechLab AI **no fluxo do Copilot** não vira erro: degrada para `200`/`DEGRADADA`.
> Falha **na indexação de embedding** (sem caminho degradado) vira `503` para retry.
