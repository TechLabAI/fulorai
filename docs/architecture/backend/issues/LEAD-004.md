# LEAD-004 -- Lead capture + deduplication (LeadService.create)

## Contexto
Ingestão idempotente de leads: cria ou faz merge por `chave_natural` normalizada e publica `lead.capturado`.

## Spec de referencia
- SPEC-02-lead-qualification-orchestration
- SPEC-05-idempotency-concurrency

## Escopo
- `LeadService.create` (`@Transactional` em `application.service`): normaliza `chave_natural`
  (lower(email) e/ou dígitos(telefone) + fonte); cria `lead`/`perfil_lead`/`atributo_perfil` ou faz merge.
- Valida `base_legal` (rejeita 422 `lead.lead.base-legal-invalida` se ausente/inválida).
- Publica `journey-os.lead.capturado` (via `LeadEventPublisherPort`); dispara recálculo de score (LEAD-005).

## Resultado esperado
Capturar duas vezes a mesma `chave_natural` resulta em 1 lead (merge), não 2.

## Criterios de aceite
- [ ] POST `/leads` cria lead em `EM_QUALIFICACAO` e publica `lead.capturado`.
- [ ] Recaptura com mesma `chave_natural` retorna `duplicado=true` e não duplica.
- [ ] `base_legal` ausente → 422 `lead.lead.base-legal-invalida`.
- [ ] `chave_natural` UNIQUE garante dedup sob concorrência.

## Dependencias
- LEAD-003 (precede)
- LEAD-005 (recálculo encadeado)

## Estimativa
M

## Prioridade
P2
