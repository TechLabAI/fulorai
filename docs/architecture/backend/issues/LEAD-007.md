# LEAD-007 -- Segmentation: SegmentEvaluator + SegmentService

## Contexto
Segmentos dinâmicos: predicado sobre perfil+score reavaliado quando o lead muda, com emissão de
`lead.segmento.alterado` em cada entrada/saída.

## Spec de referencia
- SPEC-02-lead-qualification-orchestration
- SPEC-01-api-surface

## Escopo
- `SegmentEvaluator` (`domain.service`): avalia o `predicado` (JSON) de cada `segmento` ativo sobre perfil+score.
- `SegmentService` (`@Transactional`): CRUD de segmentos; reavaliação de membership; materializa `lead_segmento`.
- Publica `journey-os.lead.segmento.alterado` (acao `ENTROU`/`SAIU`).
- `GET /segments/{id}/leads` ordena por Maturity Score desc.

## Resultado esperado
Lead que cruza o predicado entra/sai do segmento e emite o evento.

## Criterios de aceite
- [ ] Mudança de perfil/score reavalia predicados ativos.
- [ ] Entrada/saída de segmento publica `lead.segmento.alterado` com `acao` correta.
- [ ] Listagem de leads por segmento ordenada por score desc.
- [ ] `predicado` inválido → 422 `lead.segment.predicado-invalido`.

## Dependencias
- LEAD-006 (score disponível)

## Estimativa
M

## Prioridade
P2
