# LEAD-005 -- Qualification orchestration + state machine (QualificationService)

## Contexto
Caso de uso central (golden path): aplicar a regra ativa, calcular o Maturity Score, transicionar
o estado do lead e publicar o evento-âncora `lead.qualificado`.

## Spec de referencia
- SPEC-02-lead-qualification-orchestration
- SPEC-03-maturity-score-6d

## Escopo
- `QualificationService.qualify` (`@Transactional`): obtém `regra_qualificacao` ativa; invoca
  `QualificationRuleEngine` + `MaturityScoreCalculator` (LEAD-006); persiste `maturity_score`/`score_dimensao`.
- Transição de estado: `>= limiar_qualificado` → `QUALIFICADO`; senão `NAO_QUALIFICADO`.
- Publica `journey-os.lead.qualificado` (transição) e `journey-os.lead.score.atualizado` (recálculo).
- Aciona reavaliação de segmentos (LEAD-007).
- `WHILE` sem regra ativa → 409 `lead.qualification.sem-regra-ativa`.

## Resultado esperado
Lead acima do limiar fica `QUALIFICADO` e emite o evento-âncora com score + breakdown + versão de regra.

## Criterios de aceite
- [ ] Score ≥ limiar → estado `QUALIFICADO` + `lead.qualificado` publicado.
- [ ] Recálculo que muda o score → `lead.score.atualizado`.
- [ ] Sem regra ativa → 409 `lead.qualification.sem-regra-ativa`.
- [ ] Ativar nova versão de regra recomputa os leads afetados.

## Dependencias
- LEAD-006 (cálculo do score)
- LEAD-007 (segmentação encadeada)

## Estimativa
L

## Prioridade
P2
