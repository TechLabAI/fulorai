# SPEC-02 — Copilot Orchestration (RAG fundamentado)

> Core orchestration (substantivo+verbo central: "Copiloto respondeu"). ADR-005, ADR-004.
> Ref: `contracts/api-contract.md §1`, `contracts/techlab-ai-integration.md`.

## Objetivo

Orquestrar a geração de respostas do copiloto via RAG fundamentado: recuperação no Elasticsearch
→ composição na TechLab AI → resposta citada → persistência → projeção → evento.

## Escopo

**In:** `CopilotService.responder(pergunta)`; recuperação; composição; fundamentação; degradação;
persistência de `conversa`/`mensagem`/`citacao`; projeção `ai-copilot-events`; evento âncora.
**Out:** ações/automações (write-back); UI; copilot assíncrono.

## Decisões técnicas

- Recuperação primária via `SearchPort` (Elastic), filtrada por `empresa`; reranking opcional via
  `KnowledgePort` (TechLab AI `knowledge`).
- Composição via `OrchestrationPort` (TechLab AI `orchestration`) recebendo evidência *grounded*.
- Circuit breaker/timeout (Resilience4j); falha → modo recuperação-apenas (`DEGRADADA`).
- `@Transactional` em `application.service` apenas.

## Implementação (pseudo)

```
responder(conversaId, pergunta):
  autoriza intl.copilot.use
  conversa = repo.find(conversaId) ?? 404
  ev = searchPort.search(empresa, pergunta, topK)            # filtrado por empresa
  if ev.isEmpty(): persistirMensagem(NAO_FUNDAMENTADA, [])  # sem alucinar
  else:
    try:
      r = orchestrationPort.compose(pergunta, ev)            # circuit breaker
      cit = r.citacoes ∩ ev                                  # citações ⊆ evidência
      status = cit.isEmpty() ? NAO_FUNDAMENTADA : RESPONDIDA
      persistirMensagem(status, cit, r.modelo, r.custo, r.latencia)
    catch CallNotPermitted | Timeout:
      persistirMensagem(DEGRADADA, evidenciaComoTexto(ev), modelo=null, custo=0)
  indexPort.index("ai-copilot-events", docRastreavel(mensagem))
  publisher.publish(copilot.resposta.gerada)
  return resposta
```

## Casos de borda

- Evidência recuperada mas composição sem citação fundamentadora → `NAO_FUNDAMENTADA`.
- Citação retornada pela IA fora da evidência recuperada → descartada (não fundamentada).
- Timeout parcial → degrada (não meio-termo).

## Critérios de aceite (EARS)

- WHEN uma pergunta é recebida, THE SYSTEM SHALL recuperar evidência filtrada por `empresa` antes de compor.
- WHEN a composição produz ≥ 1 citação ⊆ evidência recuperada, THE SYSTEM SHALL marcar a resposta `RESPONDIDA`.
- IF a evidência é insuficiente, THEN THE SYSTEM SHALL marcar a resposta `NAO_FUNDAMENTADA` sem apresentar fato como confirmado.
- IF a TechLab AI está indisponível, THEN THE SYSTEM SHALL marcar a resposta `DEGRADADA` e responder `200`.
- WHEN a resposta é persistida, THE SYSTEM SHALL projetar `ai-copilot-events` e publicar `journey-os.copilot.resposta.gerada`.
- THE SYSTEM SHALL nunca chamar um provedor de IA fora da TechLab AI.
