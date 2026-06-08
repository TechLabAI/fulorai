# COMM-009 -- Template Studio (TechLab AI document_composition) + fallback

## Contexto
Composição assistida de copy de template via TechLab AI `document_composition`, com degradação
graciosa quando a IA está indisponível.

## Spec de referencia
- SPEC-10-integrations
- SPEC-01-api-surface

## Escopo
- `TemplateStudioController`: `POST /api/v1/templates/{id}/studio/compose` (+ `Idempotency-Key`).
- `ComporNoStudioService` (`@Transactional`) via `ComposicaoIaPort` (impl `TechLabAiClient`, INT-COMM-003).
- Resultado vira corpo do template em RASCUNHO (bump versão) + grava `brief_composicao`; nunca ativa automático.
- Falha/timeout/CB aberto → 503 `comm.studio.ia-indisponivel`, corpo inalterado.

## Resultado esperado
Marina compõe um rascunho de copy a partir de um brief; IA fora não derruba o CRUD.

## Criterios de aceite
- [ ] Composição OK → corpo atualizado em RASCUNHO + `briefComposicao` gravado.
- [ ] TechLab AI fora → 503 `comm.studio.ia-indisponivel`, corpo inalterado.
- [ ] `Idempotency-Key` repetida → uma chamada à IA, mesmo resultado.

## Dependencias
- COMM-003 (precede)
- INT-COMM-003 (TechLab AI client)

## Estimativa
M

## Prioridade
P4
