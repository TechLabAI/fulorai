# INTL-005 -- CopilotService: orquestração RAG (golden path)

## Contexto
Implementar o golden path do evento-âncora "Copiloto respondeu": recuperação → composição →
persistência → projeção → evento.

## Spec de referência
- SPEC-02, ADR-005

## Escopo
`CopilotService.responder`: recupera evidência (`IntlSearchPort`, filtrada por `empresa`); compõe
via `OrchestrationPort` (circuit breaker); persiste `conversa`/`mensagem`/`citacao`; projeta
`ai-copilot-events`; publica `journey-os.copilot.resposta.gerada`. `@Transactional` na service.

## Resultado esperado
Pergunta com evidência retorna `RESPONDIDA` com ≥1 citação; evento emitido; doc projetado.

## Critérios de aceite
- [ ] Recuperação sempre precede a composição e é filtrada por `empresa`
- [ ] Resposta com citação ⊆ evidência → `RESPONDIDA`
- [ ] Mensagem persistida + `ai-copilot-events` projetado + evento publicado
- [ ] Nunca chama provedor de IA direto (só TechLab AI)

## Dependências
- INTL-003, INTL-007, INTL-009, INTL-010 (precedem na integração; stubbable para teste)

## Estimativa
L

## Prioridade
P2
