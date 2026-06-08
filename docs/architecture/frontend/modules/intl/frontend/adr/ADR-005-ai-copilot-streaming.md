# ADR-005 — Render da resposta do Copilot: request/response no MVP; streaming (SSE) diferido

- **Status:** accepted

## Contexto

O AI Copilot é a feature mais sensível de UX do INTL: a resposta tem **latência alta e variável**
(RAG no Elasticsearch + composição na TechLab AI). A pergunta natural é se a UI deve **streamar a
resposta token-a-token** (SSE/WebSocket, estilo "digitando") para reduzir a latência percebida.

O contrato do BE (`intl-service/contracts/api-contract.md`) expõe `POST
/api/v1/copilot/conversas/{id}/perguntar` como **endpoint síncrono** que retorna `200` com a
resposta **completa** (`texto` + `status` + `citacoes`). **Não há** endpoint de streaming no MVP do
BE. Além disso, a fundamentação (citações) só é conhecida ao final da composição — streaming
parcial arriscaria exibir texto antes de saber se a resposta é `RESPONDIDA`/`NAO_FUNDAMENTADA`/
`DEGRADADA`, ferindo o princípio de "fundamentação acima de fluência" (ADR-005 BE).

## Decisão

No **MVP**, renderizar a resposta em modelo **request/response** com **estado `pensando` otimista**:

1. Ao enviar, inserir imediatamente a bolha do usuário + uma bolha `COPILOTO` em `PENDENTE`
   (feedback < 100 ms), com indicador "pensando" e botão **Cancelar** (`AbortController`).
2. No `200`, substituir a bolha `PENDENTE` pela resposta completa — só então renderizar texto,
   **badge de `status`** e **chips de citação**. Citações nunca aparecem antes do status final.
3. **Streaming (SSE) fica diferido** para o pós-MVP, atrás da feature-flag
   `intl.copilot-streaming` (`defaultState: off`). Quando o BE expuser um endpoint de streaming
   *grounded* (texto + sinal de fundamentação incremental), um novo ADR substitui este.

## Alternativas consideradas

- **Streaming SSE token-a-token já no MVP** — rejeitada: **não há endpoint no BE**; e exibir texto
  antes do `status`/citações violaria a regra de fundamentação (risco de mostrar como fato algo que
  será `NAO_FUNDAMENTADA`).
- **Polling de uma resposta assíncrona** — rejeitada: o BE é síncrono; polling adicionaria
  complexidade sem ganho (a conexão já bloqueia até a resposta).
- **Sem feedback otimista (spinner global)** — rejeitada: latência variável tornaria a UX ruim;
  o estado `pensando` na bolha é mais informativo e permite cancelar.

## Consequências

- **Positivas:** alinhado ao contrato real do BE; preserva a regra de fundamentação; UX aceitável
  via `pensando` + cancelamento; caminho claro para streaming quando o BE suportar (flag pronta).
- **Negativas:** latência percebida maior que um streaming verdadeiro em respostas longas
  (mitigada pelo feedback imediato e pelo cancelamento); a flag reservada precisa de um ADR futuro
  para ser ativada com segurança.

## Referências

- BE: `docs/architecture/backend/services/intl-service/contracts/api-contract.md` (§1.2 perguntar)
- BE ADR-005 (RAG fundamentado / degradação graciosa)
- `04-frontend-architecture-direction.md` (§7 feature-flags) · `05-state-and-data-flow.md` (§4 otimismo)
